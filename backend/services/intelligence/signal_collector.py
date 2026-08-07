"""
STRATUM Signal Collector Service - MERGED FROM JULIUS TO SERA
Orchestrates collection from multiple public data sources
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, Dict, List
from enum import Enum
from pathlib import Path
import sys

# Add Sera paths
SERA_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERA_ROOT))

# Sera-specific imports
try:
    from config import settings
    SERA_CONFIG = settings
except ImportError:
    SERA_CONFIG = None

try:
    from database.db import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Setup Sera logging
LOG_DIR = SERA_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'sera_signal_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_signal_collector")

# Constants
class SourceType(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    NPM = "npm"
    PYPI = "pypi"
    GOVUK = "govuk"
    COMPANIES_HOUSE = "companies_house"
    WIKIDATA = "wikidata"
    OPENCORPORATES = "opencorporates"
    GDELT = "gdelt"
    HACKERTARGET = "hackertarget"
    IPINFO = "ipinfo"
    SHODAN = "shodan"
    WHOIS = "whois"

RATE_LIMIT_CONFIG = {
    SourceType.GITHUB: 1.0,
    SourceType.GITLAB: 1.0,
    SourceType.NPM: 0.5,
    SourceType.PYPI: 1.0,
    SourceType.GOVUK: 0.5,
    SourceType.COMPANIES_HOUSE: 1.0,
    SourceType.WIKIDATA: 0.5,
    SourceType.OPENCORPORATES: 1.0,
    SourceType.GDELT: 2.0,
    SourceType.HACKERTARGET: 1.0,
    SourceType.IPINFO: 1.0,
    SourceType.SHODAN: 2.0,
    SourceType.WHOIS: 1.0,
}

@dataclass
class CollectionSource:
    source_type: SourceType
    queries: list[str] = field(default_factory=list)
    max_results_per_query: int = 50
    enabled: bool = True
    api_key: Optional[str] = None

@dataclass
class CollectionJob:
    job_id: str
    status: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    target_profiles: int = 100000
    collected_profiles: int = 0
    deduplicated_profiles: int = 0
    stored_profiles: int = 0
    sources: list[CollectionSource] = field(default_factory=list)
    progress_percent: int = 0
    processed_count: int = 0
    total_count: int = 0
    source_breakdown: dict[str, int] = field(default_factory=dict)
    recent_errors: list[str] = field(default_factory=list)
    stop_requested: bool = False
    target_reached: bool = False

class SeraSignalCollector:
    """Orchestrates signal collection from multiple sources with Sera integration"""
    
    def __init__(self):
        self._jobs: dict[str, CollectionJob] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._stored_profiles: set[str] = set()
        
        # Sera components
        self.db = self._init_database()
        self.auth = self._init_auth()
        self.audit = self._init_audit()
        
        # Rate limiters
        self._rate_limiters = {}
        for source_type in SourceType:
            self._rate_limiters[source_type] = asyncio.Semaphore(1)
        
        logger.info("Sera Signal Collector initialized")
    
    def _init_database(self):
        """Initialize Sera database"""
        if DB_AVAILABLE:
            return get_db()
        logger.warning("Database not available - using memory storage")
        return None
    
    def _init_auth(self):
        """Initialize Sera authentication"""
        try:
            from security.auth import get_current_user
            return get_current_user
        except ImportError:
            logger.warning("Auth not available - development mode")
            return None
    
    def _init_audit(self):
        """Initialize Sera audit logging"""
        try:
            from services.audit_service import log_activity
            return log_activity
        except ImportError:
            logger.warning("Audit service not available - using local logging")
            return None
    
    def _default_sources(self) -> list[CollectionSource]:
        """Default collection sources"""
        return [
            CollectionSource(SourceType.GITHUB, ['location:"UK"', 'location:"United Kingdom"'], 100),
            CollectionSource(SourceType.GITLAB, ["UK", "United Kingdom"], 50),
            CollectionSource(SourceType.NPM, ["UK", "United Kingdom"], 50),
            CollectionSource(SourceType.PYPI, ["UK", "United Kingdom"], 50),
            CollectionSource(SourceType.GOVUK, ["UK", "government", "policy"], 50),
            CollectionSource(SourceType.COMPANIES_HOUSE, ["*"], 100),
            CollectionSource(SourceType.GDELT, ["United Kingdom", "UK news"], 50),
        ]
    
    async def start_collection(self, target_profiles: int = 100000,
                              sources: Optional[list[CollectionSource]] = None) -> CollectionJob:
        """Start a new collection job"""
        job_id = f"collect-{uuid.uuid4().hex[:8]}"
        
        if sources is None:
            sources = self._default_sources()
        
        total_count = sum(
            len(source.queries) * source.max_results_per_query
            for source in sources
            if source.enabled
        )
        
        job = CollectionJob(
            job_id=job_id,
            status="running",
            target_profiles=max(1, target_profiles),
            sources=sources,
            total_count=max(1, total_count),
        )
        
        async with self._lock:
            self._jobs[job_id] = job
            self._tasks[job_id] = asyncio.create_task(self._run_collection(job))
        
        logger.info(f"Started collection job {job_id}, target {target_profiles}")
        
        # Audit log
        self._log_collection_start(job)
        
        return job
    
    async def _run_collection(self, job: CollectionJob) -> None:
        """Main collection loop"""
        import httpx
        
        try:
            job.status = "running"
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                for source in job.sources:
                    if not source.enabled:
                        continue
                    if job.stop_requested or job.target_reached:
                        break
                    
                    for query in source.queries:
                        if job.stop_requested or job.target_reached:
                            break
                        
                        await self._rate_limiters[source.source_type].acquire()
                        
                        try:
                            profiles = await self._collect_from_source(
                                client, source.source_type, query, 
                                source.max_results_per_query
                            )
                            
                            if profiles:
                                for profile in profiles[:source.max_results_per_query]:
                                    if job.collected_profiles >= job.target_profiles:
                                        job.target_reached = True
                                        break
                                    self._store_profile(profile)
                                    job.collected_profiles += 1
                                    job.stored_profiles += 1
                                    source_str = str(source.source_type.value)
                                    job.source_breakdown[source_str] = job.source_breakdown.get(source_str, 0) + 1
                                
                                logger.info(f"Collected {len(profiles)} from {source.source_type}")
                        except Exception as e:
                            logger.error(f"Collection failed for {source.source_type}:{query}: {e}")
                            job.recent_errors.append(f"{source.source_type}: {str(e)}")
                        
                        await asyncio.sleep(RATE_LIMIT_CONFIG[source.source_type])
            
            if job.stop_requested:
                job.status = "stopped"
            else:
                job.status = "completed"
            
            job.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"Collection job {job.job_id} complete: {job.stored_profiles} profiles")
            
            self._log_collection_complete(job)
            
        except Exception as e:
            logger.error(f"Collection job {job.job_id} failed: {e}")
            job.status = "failed"
            job.recent_errors.append(str(e))
            job.completed_at = datetime.now(timezone.utc).isoformat()
    
    async def _collect_from_source(self, client, source_type: SourceType, 
                                   query: str, max_results: int) -> list[dict]:
        """Collect from a specific source"""
        try:
            if source_type == SourceType.GITHUB:
                return await self._collect_github(client, query, max_results)
            elif source_type == SourceType.GITLAB:
                return await self._collect_gitlab(client, query, max_results)
            elif source_type == SourceType.NPM:
                return await self._collect_npm(client, query, max_results)
            elif source_type == SourceType.PYPI:
                return await self._collect_pypi(client, query, max_results)
            elif source_type == SourceType.GOVUK:
                return await self._collect_govuk(client, query, max_results)
            elif source_type == SourceType.COMPANIES_HOUSE:
                return await self._collect_companies_house(client, query, max_results)
            elif source_type == SourceType.GDELT:
                return await self._collect_gdelt(client, query, max_results)
            else:
                return []
        except Exception as e:
            logger.warning(f"Collection error for {source_type}: {e}")
            return []
    
    async def _collect_github(self, client, query: str, max_results: int) -> list[dict]:
        """Collect from GitHub"""
        try:
            url = "https://api.github.com/search/users"
            params = {"q": query, "per_page": min(100, max_results)}
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [{
                "platform": "github",
                "handle": user.get("login"),
                "profile_url": user.get("html_url"),
                "source": "github"
            } for user in data.get("items", [])[:max_results] if user.get("login")]
        except Exception as e:
            logger.warning(f"GitHub collection error: {e}")
            return []
    
    async def _collect_gitlab(self, client, query: str, max_results: int) -> list[dict]:
        """Collect from GitLab"""
        try:
            url = "https://gitlab.com/api/v4/users"
            params = {"search": query, "per_page": min(100, max_results)}
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [{
                "platform": "gitlab",
                "handle": user.get("username"),
                "profile_url": user.get("web_url"),
                "source": "gitlab"
            } for user in data[:max_results] if user.get("username")]
        except Exception as e:
            logger.warning(f"GitLab collection error: {e}")
            return []
    
    async def _collect_npm(self, client, query: str, max_results: int) -> list[dict]:
        """Collect from npm"""
        try:
            url = "https://registry.npmjs.org/-/v1/search"
            params = {"text": query, "size": min(100, max_results)}
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [{
                "platform": "npm",
                "name": pkg.get("package", {}).get("name"),
                "profile_url": f"https://www.npmjs.com/package/{pkg.get('package', {}).get('name')}",
                "source": "npm"
            } for pkg in data.get("objects", [])[:max_results] if pkg.get("package", {}).get("name")]
        except Exception as e:
            logger.warning(f"npm collection error: {e}")
            return []
    
    async def _collect_pypi(self, client, query: str, max_results: int) -> list[dict]:
        """Collect from PyPI"""
        try:
            url = f"https://pypi.org/pypi/{query}/json"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                info = data.get("info", {})
                return [{
                    "platform": "pypi",
                    "name": info.get("name"),
                    "profile_url": f"https://pypi.org/project/{info.get('name')}/",
                    "source": "pypi"
                }]
            return []
        except Exception as e:
            logger.warning(f"PyPI collection error: {e}")
            return []
    
    async def _collect_govuk(self, client, query: str, max_results: int) -> list[dict]:
        """Collect from GOV.UK"""
        try:
            url = "https://www.gov.uk/api/search.json"
            params = {"q": query, "count": min(100, max_results)}
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [{
                "platform": "govuk",
                "title": result.get("title"),
                "profile_url": result.get("link"),
                "source": "govuk"
            } for result in data.get("results", [])[:max_results] if result.get("title")]
        except Exception as e:
            logger.warning(f"GOV.UK collection error: {e}")
            return []
    
    async def _collect_companies_house(self, client, query: str, max_results: int) -> list[dict]:
        """Collect from Companies House"""
        try:
            url = "https://api.company-information.service.gov.uk/search/companies"
            params = {"q": query, "items_per_page": min(100, max_results)}
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [{
                "platform": "companies_house",
                "company_name": company.get("title"),
                "company_number": company.get("company_number"),
                "source": "companies_house"
            } for company in data.get("items", [])[:max_results] if company.get("title")]
        except Exception as e:
            logger.warning(f"Companies House collection error: {e}")
            return []
    
    async def _collect_gdelt(self, client, query: str, max_results: int) -> list[dict]:
        """Collect from GDELT"""
        try:
            url = "https://api.gdeltproject.org/api/v2/doc/doc"
            params = {
                "query": query,
                "mode": "timelinevolume",
                "format": "json",
                "maxrecords": min(250, max_results),
            }
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [{
                "platform": "gdelt",
                "title": doc.get("title"),
                "profile_url": doc.get("url"),
                "source": "gdelt"
            } for doc in data.get("articles", [])[:max_results] if doc.get("title")]
        except Exception as e:
            logger.warning(f"GDELT collection error: {e}")
            return []
    
    def _store_profile(self, profile: dict) -> None:
        """Store profile in Sera database"""
        try:
            if self.db:
                # Store in Sera database
                # Assuming Sera has an identities or profiles table
                import sqlite3
                conn = self.db if hasattr(self.db, 'cursor') else None
                if conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO profiles 
                        (id, platform, handle, data, collected_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        f"prof_{uuid.uuid4().hex[:8]}",
                        profile.get('platform', 'unknown'),
                        profile.get('handle', profile.get('name', '')),
                        json.dumps(profile),
                        datetime.now(timezone.utc).isoformat()
                    ))
                    conn.commit()
                    logger.debug(f"Stored profile from {profile.get('platform')}")
        except Exception as e:
            logger.error(f"Failed to store profile: {e}")
    
    def _log_collection_start(self, job: CollectionJob):
        """Log collection start to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="signal_collection_start",
                    target=f"job_{job.job_id}",
                    details={"target_profiles": job.target_profiles}
                )
            else:
                audit_file = LOG_DIR / f"collection_{datetime.now().strftime('%Y%m%d')}.log"
                with open(audit_file, 'a') as f:
                    f.write(json.dumps({
                        "action": "start",
                        "job_id": job.job_id,
                        "timestamp": job.started_at
                    }) + '\n')
        except Exception as e:
            logger.error(f"Error logging collection start: {e}")
    
    def _log_collection_complete(self, job: CollectionJob):
        """Log collection complete to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="signal_collection_complete",
                    target=f"job_{job.job_id}",
                    details={
                        "stored_profiles": job.stored_profiles,
                        "status": job.status
                    }
                )
        except Exception as e:
            logger.error(f"Error logging collection complete: {e}")
    
    def get_job(self, job_id: str) -> Optional[CollectionJob]:
        """Get job status"""
        return self._jobs.get(job_id)
    
    def list_jobs(self) -> list[CollectionJob]:
        """List all jobs"""
        return sorted(self._jobs.values(), key=lambda j: j.started_at, reverse=True)
    
    async def stop_collection(self, job_id: str) -> bool:
        """Stop a running job"""
        job = self._jobs.get(job_id)
        if job:
            job.stop_requested = True
            logger.info(f"Stop requested for job {job_id}")
            return True
        return False

# Singleton
_collector_instance = None

def get_collector() -> SeraSignalCollector:
    """Get or create collector instance"""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = SeraSignalCollector()
    return _collector_instance

# Sera API Functions
async def start_collection(target_profiles: int = 100000) -> Dict[str, Any]:
    """API: Start signal collection"""
    collector = get_collector()
    job = await collector.start_collection(target_profiles)
    return {
        "status": "success",
        "job_id": job.job_id,
        "target_profiles": job.target_profiles
    }

async def get_collection_status(job_id: str) -> Dict[str, Any]:
    """API: Get collection status"""
    collector = get_collector()
    job = collector.get_job(job_id)
    if not job:
        return {"status": "error", "message": "Job not found"}
    return {
        "status": "success",
        "job": {
            "job_id": job.job_id,
            "status": job.status,
            "collected_profiles": job.collected_profiles,
            "stored_profiles": job.stored_profiles,
            "progress_percent": job.progress_percent
        }
    }

async def list_collections() -> Dict[str, Any]:
    """API: List all collections"""
    collector = get_collector()
    jobs = collector.list_jobs()
    return {
        "status": "success",
        "total": len(jobs),
        "jobs": [
            {
                "job_id": j.job_id,
                "status": j.status,
                "collected": j.collected_profiles,
                "started_at": j.started_at
            }
            for j in jobs
        ]
    }

async def stop_collection(job_id: str) -> Dict[str, Any]:
    """API: Stop collection"""
    collector = get_collector()
    stopped = await collector.stop_collection(job_id)
    return {
        "status": "success" if stopped else "error",
        "message": "Collection stopped" if stopped else "Job not found"
    }

if __name__ == "__main__":
    print("Sera Signal Collector loaded")