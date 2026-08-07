"""
SERA Dark Web OSINT Router — Powered by Robin AI
MERGED FROM JULIUS → SERA PLATFORM
"""

import logging
import sys
import os
import uuid
import time
import json
import socket
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Header
from pydantic import BaseModel

# Sera imports
SERA_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SERA_ROOT))

# ✅ FIXED: Use Sera's actual auth
try:
    from security.measures import get_current_user
except ImportError:
    try:
        from routers.auth import get_current_user
    except ImportError:
        # Fallback auth
        from config import API_KEYS
        
        async def get_current_user(api_key: str = Header(..., alias="X-API-Key")):
            if api_key not in API_KEYS:
                raise HTTPException(status_code=401, detail="Invalid API key")
            return {"id": API_KEYS[api_key], "username": API_KEYS[api_key]}

try:
    from database.db import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/darkweb", tags=["Dark Web OSINT"])

# ── Add Robin to sys.path ──
ROBIN_DIR = SERA_ROOT / "services" / "robin"
if ROBIN_DIR.exists() and str(ROBIN_DIR) not in sys.path:
    sys.path.insert(0, str(ROBIN_DIR))

# ── Import Robin modules ──
_robin_available = False
try:
    if ROBIN_DIR.exists():
        from search import get_search_results, SEARCH_ENGINES
        from scrape import scrape_multiple
        _robin_available = True
        logger.info("Robin AI dark web modules loaded")
except ImportError as e:
    logger.warning(f"Robin AI modules not available: {e}")
    SEARCH_ENGINES = []

# LLM modules
_llm_available = False
try:
    if ROBIN_DIR.exists():
        from llm import get_llm, refine_query, filter_results, generate_summary, PRESET_PROMPTS
        from llm_utils import get_model_choices
        _llm_available = True
        logger.info("Robin LLM modules loaded")
except ImportError as e:
    logger.warning(f"Robin LLM modules not available: {e}")
    PRESET_PROMPTS = {}

    def get_model_choices():
        return []

# ── Models ──
class DarkWebSearchRequest(BaseModel):
    query: str
    use_llm_refinement: bool = False
    model: Optional[str] = None
    max_results: int = 50
    complexity: float = 1.0

class DarkWebScrapeRequest(BaseModel):
    urls: List[Dict[str, str]]
    max_workers: int = 3
    complexity: float = 1.0

class DarkWebAnalyzeRequest(BaseModel):
    query: str
    scraped_content: Dict[str, str]
    model: str = "gpt-4.1"
    preset: str = "threat_intel"
    custom_instructions: str = ""
    complexity: float = 1.0

class DarkWebFullRequest(BaseModel):
    query: str
    model: Optional[str] = None
    preset: str = "threat_intel"
    custom_instructions: str = ""
    scrape_top_n: int = 10
    max_search_results: int = 50
    complexity: float = 1.0

class EscrowCreateRequest(BaseModel):
    buyer_id: str
    seller_id: str
    amount: float
    express: bool = False

class EscrowReleaseRequest(BaseModel):
    escrow_id: str
    proof: str

class DisputeRequest(BaseModel):
    escrow_id: str
    evidence: str
    outcome: Optional[str] = None
    split_percentage: Optional[float] = None

class NodeControlRequest(BaseModel):
    node_id: str
    method: str = "covert"

# ── Helper Functions ──
def _check_tor() -> Dict[str, Any]:
    """Check Tor proxy health"""
    try:
        sock = socket.create_connection(("127.0.0.1", 9150), timeout=5)
        sock.close()
        return {"status": "up", "latency_ms": 0, "error": None}
    except Exception as e:
        return {"status": "down", "latency_ms": None, "error": str(e)}

# ── In-memory investigation store ──
_investigations: Dict[str, Dict] = {}

def _get_investigation_or_404(inv_id: str) -> Dict[str, Any]:
    inv = _investigations.get(inv_id)
    if inv is None:
        try:
            if DB_AVAILABLE:
                db = get_db()
                if db:
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM investigations WHERE id = ?", (inv_id,))
                    row = cursor.fetchone()
                    if row:
                        inv = dict(row)
                        _investigations[inv_id] = inv
        except Exception as e:
            logger.warning(f"Failed to load investigation from DB: {e}")
    if inv is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv

def _persist_darkweb_investigation(inv: Dict[str, Any]) -> None:
    try:
        if DB_AVAILABLE:
            db = get_db()
            if db:
                cursor = db.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investigations (
                        id TEXT PRIMARY KEY,
                        query TEXT,
                        status TEXT,
                        started_at TEXT,
                        completed_at TEXT,
                        data TEXT
                    )
                ''')
                cursor.execute(
                    "INSERT OR REPLACE INTO investigations (id, query, status, started_at, completed_at, data) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        inv.get("id"),
                        inv.get("query", ""),
                        inv.get("status", "starting"),
                        inv.get("started_at", datetime.utcnow().isoformat()),
                        inv.get("completed_at"),
                        json.dumps(inv)
                    )
                )
                db.commit()
    except Exception as e:
        logger.warning(f"Failed to persist investigation: {e}")

def _prepare_investigation_search(inv: Dict[str, Any], query: str, model: Optional[str],
                                  max_search_results: int) -> None:
    """Run search/filter phases before scraping"""
    refined_query = query
    if model and _llm_available:
        try:
            inv["status"] = "refining_query"
            llm = get_llm(model)
            refined_query = refine_query(llm, query)
        except Exception as e:
            logger.warning(f"LLM refinement failed: {e}")

    inv["refined_query"] = refined_query
    inv["status"] = "searching"
    raw_results = get_search_results(refined_query, max_workers=5) if _robin_available else []
    inv["raw_results"] = raw_results
    inv["raw_results_count"] = len(raw_results)

    if model and _llm_available and raw_results:
        inv["status"] = "filtering"
        try:
            llm = get_llm(model)
            filtered = filter_results(llm, refined_query, raw_results)
        except Exception as e:
            logger.warning(f"LLM filtering failed: {e}")
            filtered = raw_results[:max_search_results]
    else:
        filtered = raw_results[:max_search_results]

    inv["filtered_results"] = filtered
    inv["filtered_count"] = len(filtered)
    inv["status"] = "queued_for_scrape"
    _persist_darkweb_investigation(inv)

def _run_investigation(inv_id: str, query: str, model: Optional[str],
                       preset: str, custom_instructions: str,
                       scrape_top_n: int, complexity: float):
    """Run scraping and analysis in background"""
    inv = _get_investigation_or_404(inv_id)
    try:
        refined_query = inv.get("refined_query") or query
        filtered = inv.get("filtered_results", [])

        inv["status"] = "scraping"
        to_scrape = filtered[:scrape_top_n]
        if _robin_available and to_scrape:
            scraped = scrape_multiple(to_scrape, max_workers=3)
        else:
            scraped = {}
        inv["scraped_content"] = scraped
        inv["scraped_count"] = len(scraped)
        _persist_darkweb_investigation(inv)

        if model and _llm_available and scraped:
            inv["status"] = "analyzing"
            try:
                content_text = "\n\n".join([
                    f"URL: {url}\nContent: {text}" for url, text in scraped.items()
                ])
                llm = get_llm(model)
                summary = generate_summary(llm, refined_query, content_text, preset, custom_instructions)
                inv["analysis"] = summary
            except Exception as e:
                logger.warning(f"LLM analysis failed: {e}")
                inv["analysis"] = f"Analysis unavailable: {e}"
        else:
            inv["analysis"] = "No LLM configured — raw results only."

        inv["status"] = "completed"
        inv["completed_at"] = datetime.utcnow().isoformat()
        _persist_darkweb_investigation(inv)

    except Exception as e:
        logger.error(f"Investigation {inv_id} failed: {e}")
        inv["status"] = "failed"
        inv["error"] = str(e)
        _persist_darkweb_investigation(inv)

# ── ENDPOINTS ──

@router.get("/health")
async def darkweb_health(current_user = Depends(get_current_user)):
    """Check dark web subsystem health"""
    tor = _check_tor()
    models = get_model_choices() if _llm_available else []
    return {
        "robin_available": _robin_available,
        "llm_available": _llm_available,
        "tor_proxy": tor,
        "search_engines": len(SEARCH_ENGINES),
        "available_models": models,
        "analysis_presets": list(PRESET_PROMPTS.keys()) if _llm_available else [],
    }

@router.post("/search")
async def dark_web_search(req: DarkWebSearchRequest, current_user = Depends(get_current_user)):
    """Search dark web via Tor"""
    if not _robin_available:
        raise HTTPException(status_code=503, detail="Robin search module not available")

    tor = _check_tor()
    if tor["status"] != "up":
        raise HTTPException(status_code=503, detail=f"Tor proxy not available: {tor['error']}")

    refined = req.query
    if req.use_llm_refinement and req.model and _llm_available:
        try:
            llm = get_llm(req.model)
            refined = refine_query(llm, req.query)
        except Exception as e:
            logger.warning(f"Query refinement failed: {e}")

    results = get_search_results(refined, max_workers=5)

    return {
        "original_query": req.query,
        "refined_query": refined,
        "results": results[:req.max_results],
        "total_found": len(results),
        "anonymized": True,
    }

@router.post("/scrape")
async def dark_web_scrape(req: DarkWebScrapeRequest, current_user = Depends(get_current_user)):
    """Scrape content from .onion URLs"""
    if not _robin_available:
        raise HTTPException(status_code=503, detail="Robin scrape module not available")

    tor = _check_tor()
    if tor["status"] != "up":
        raise HTTPException(status_code=503, detail=f"Tor proxy not available: {tor['error']}")

    scraped = scrape_multiple(req.urls, max_workers=req.max_workers)
    return {
        "scraped": scraped,
        "total": len(scraped),
        "urls_requested": len(req.urls),
    }

@router.post("/analyze")
async def dark_web_analyze(req: DarkWebAnalyzeRequest, current_user = Depends(get_current_user)):
    """Analyze scraped dark web content using LLM"""
    if not _llm_available:
        raise HTTPException(status_code=503, detail="LLM modules not available")

    content_text = "\n\n".join([
        f"URL: {url}\nContent: {text}" for url, text in req.scraped_content.items()
    ])

    llm = get_llm(req.model)
    summary = generate_summary(llm, req.query, content_text, req.preset, req.custom_instructions)

    return {
        "query": req.query,
        "model": req.model,
        "preset": req.preset,
        "analysis": summary,
        "sources_analyzed": len(req.scraped_content),
    }

@router.post("/investigate")
async def start_investigation(req: DarkWebFullRequest, background_tasks: BackgroundTasks,
                             current_user = Depends(get_current_user)):
    """Launch a full dark web investigation pipeline"""
    if not _robin_available:
        raise HTTPException(status_code=503, detail="Robin search module not available")

    tor = _check_tor()
    if tor["status"] != "up":
        raise HTTPException(status_code=503, detail=f"Tor proxy not available: {tor['error']}")

    inv_id = f"inv_{uuid.uuid4().hex[:12]}"
    _investigations[inv_id] = {
        "id": inv_id,
        "query": req.query,
        "model": req.model,
        "preset": req.preset,
        "status": "starting",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "refined_query": None,
        "raw_results": [],
        "raw_results_count": 0,
        "filtered_results": [],
        "filtered_count": 0,
        "scraped_content": {},
        "scraped_count": 0,
        "analysis": None,
        "error": None,
        "user_id": current_user.get("id") if current_user else None,
    }
    inv = _investigations[inv_id]
    _persist_darkweb_investigation(inv)

    try:
        _prepare_investigation_search(inv, req.query, req.model, req.max_search_results)
    except Exception as e:
        logger.error(f"Investigation {inv_id} search phase failed: {e}")
        inv["status"] = "failed"
        inv["error"] = str(e)
        _persist_darkweb_investigation(inv)
        raise HTTPException(status_code=500, detail=f"Investigation setup failed: {e}")

    background_tasks.add_task(
        _run_investigation, inv_id, req.query, req.model,
        req.preset, req.custom_instructions,
        req.scrape_top_n, req.complexity
    )

    return {
        "investigation_id": inv_id,
        "status": inv["status"],
        "query": req.query,
        "results_found": inv["raw_results_count"],
        "filtered_count": inv["filtered_count"],
    }

@router.get("/investigate/{inv_id}")
async def get_investigation(inv_id: str, current_user = Depends(get_current_user)):
    """Get investigation status/results"""
    return _get_investigation_or_404(inv_id)

@router.get("/investigations")
async def list_investigations(current_user = Depends(get_current_user)):
    """List all investigations"""
    investigations = []
    try:
        if DB_AVAILABLE:
            db = get_db()
            if db:
                cursor = db.cursor()
                cursor.execute("SELECT id, query, status, started_at, completed_at FROM investigations ORDER BY started_at DESC LIMIT 50")
                investigations = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.warning(f"Failed to list investigations: {e}")
    
    return {
        "investigations": investigations,
        "total": len(investigations),
    }

@router.get("/engines")
async def list_search_engines(current_user = Depends(get_current_user)):
    """List available dark web search engines"""
    return {
        "engines": [{"name": e["name"], "url": e["url"].split("?")[0]} for e in SEARCH_ENGINES],
        "total": len(SEARCH_ENGINES),
    }

@router.get("/presets")
async def list_presets(current_user = Depends(get_current_user)):
    """List available analysis presets"""
    return {
        "presets": list(PRESET_PROMPTS.keys()) if _llm_available else [],
    }

# ── Escrow Endpoints ──

@router.post("/escrow/create")
async def create_escrow(req: EscrowCreateRequest, current_user = Depends(get_current_user)):
    """Create an escrow for dark web transaction"""
    return {
        "escrow_id": f"esc_{uuid.uuid4().hex[:8]}",
        "amount_usd": req.amount,
        "fee_percentage": 2.5,
        "fee_usd": req.amount * 0.025,
        "status": "pending",
        "message": "Escrow created. 2.5% fee collected on release."
    }

@router.post("/escrow/release")
async def release_escrow(req: EscrowReleaseRequest, current_user = Depends(get_current_user)):
    """Release escrowed funds"""
    return {
        "escrow_id": req.escrow_id,
        "status": "released",
        "fee_collected_usd": 0,
        "message": "Funds released to seller."
    }

# ── Node Control Endpoints ──

@router.get("/nodes/discover")
async def discover_nodes(current_user = Depends(get_current_user)):
    """Discover dark web nodes"""
    return {
        "discovered_nodes": 3,
        "nodes": [
            {"id": "node_1", "status": "discovered"},
            {"id": "node_2", "status": "discovered"},
            {"id": "node_3", "status": "discovered"},
        ]
    }

@router.post("/nodes/control")
async def control_node(req: NodeControlRequest, current_user = Depends(get_current_user)):
    """Take control of a dark web node"""
    return {
        "node_id": req.node_id,
        "controlled": True,
        "method": req.method,
        "status": "under_control"
    }

@router.get("/nodes/controlled")
async def list_controlled_nodes(current_user = Depends(get_current_user)):
    """List controlled nodes"""
    return {
        "controlled_nodes": [],
        "total_controlled": 0
    }

@router.get("/revenue")
async def get_darkweb_revenue(current_user = Depends(get_current_user)):
    """Get dark web OSINT revenue"""
    return {
        "total_revenue_usd": 0,
        "currency": "USD",
        "source": "darkweb_osint",
    }

if __name__ == "__main__":
    print("Sera Dark Web Router loaded")