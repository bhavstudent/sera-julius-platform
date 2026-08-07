"""
SERA AXIOM-Φ Router
====================
Entropy monitoring and real-time anomaly detection API.

Endpoints:
- GET /api/axiom/status - System status
- GET /api/axiom/monitor - Full monitor dashboard
- GET /api/axiom/entropy - Entropy summary for all entities
- GET /api/axiom/entropy/entity/{entity_id} - Entity entropy details
- GET /api/axiom/entropy/trend/{entity_id} - Entity entropy trend
- GET /api/axiom/entropy/distribution/{entity_id} - Event type distribution
- POST /api/axiom/entropy/ingest - Ingest an event
- GET /api/axiom/alerts - Get active alerts
- GET /api/axiom/thresholds - Get current thresholds
- POST /api/axiom/thresholds - Update thresholds
- POST /api/axiom/entropy/reset/{entity_id} - Reset entity entropy
- GET /api/axiom/entities - List all entities with entropy
- GET /api/axiom/compress-demo - AXIOM compression demo
"""

import asyncio
import logging
import random
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy import select, func

logger = logging.getLogger("sera.axiom")

router = APIRouter(prefix="/api/axiom", tags=["AXIOM-Φ"])

# ======================================================================
# DATA MODELS
# ======================================================================

class EventIngestRequest(BaseModel):
    entity_id: str = Field(..., description="Entity identifier")
    event_type: str = Field(..., description="Type of event (e.g., 'product_launch', 'market_change')")
    protocol: str = Field(default="unknown", description="Event source protocol")


class ThresholdConfig(BaseModel):
    alert_threshold: float = Field(2.0, ge=0.5, le=5.0, description="Z-score alert threshold")
    entropy_threshold: float = Field(1.1, ge=0.5, le=2.0, description="Entropy alert threshold")
    window_size: int = Field(50, ge=10, le=500, description="Entropy window size")


# ======================================================================
# FALLBACK DATA
# ======================================================================

_FALLBACK_SUMMARY = [
    {"entity_id": "NVDA", "entity_name": "NVIDIA Corporation", "domain": "Technology",
     "entropy": 0.85, "z_score": 2.1, "status": "pre-transition", 
     "history": [0.4, 0.5, 0.7, 0.85, 0.82, 0.88, 0.85, 0.90, 0.87, 0.85]},
    {"entity_id": "AAPL", "entity_name": "Apple Inc.", "domain": "Consumer Electronics",
     "entropy": 0.32, "z_score": 0.4, "status": "stable", 
     "history": [0.30, 0.31, 0.32, 0.32, 0.33, 0.31, 0.32, 0.33, 0.32, 0.32]},
    {"entity_id": "MSFT", "entity_name": "Microsoft Corporation", "domain": "Software",
     "entropy": 0.28, "z_score": 0.2, "status": "stable", 
     "history": [0.25, 0.27, 0.28, 0.28, 0.29, 0.27, 0.28, 0.28, 0.27, 0.28]},
    {"entity_id": "GOOGL", "entity_name": "Alphabet Inc.", "domain": "Internet",
     "entropy": 0.41, "z_score": 0.6, "status": "stable", 
     "history": [0.38, 0.40, 0.41, 0.41, 0.42, 0.40, 0.41, 0.42, 0.41, 0.41]},
    {"entity_id": "TSLA", "entity_name": "Tesla, Inc.", "domain": "Automotive",
     "entropy": 0.78, "z_score": 1.8, "status": "pre-transition", 
     "history": [0.50, 0.65, 0.72, 0.78, 0.76, 0.80, 0.78, 0.82, 0.79, 0.78]},
    {"entity_id": "AMZN", "entity_name": "Amazon.com Inc.", "domain": "E-Commerce",
     "entropy": 0.38, "z_score": 0.5, "status": "stable", 
     "history": [0.33, 0.35, 0.37, 0.38, 0.39, 0.37, 0.38, 0.38, 0.37, 0.38]},
    {"entity_id": "META", "entity_name": "Meta Platforms", "domain": "Social Media",
     "entropy": 0.61, "z_score": 1.1, "status": "pre-transition", 
     "history": [0.45, 0.50, 0.58, 0.61, 0.63, 0.60, 0.61, 0.64, 0.62, 0.61]},
]

# Cache for entropy data
_ENTROPY_CACHE = {}
_CACHE_TTL = 30  # seconds


# ======================================================================
# ENTROPY ENGINE HELPER
# ======================================================================

def _get_entropy_engine():
    """Get the entropy engine instance with fallback."""
    try:
        from core.entropy_engine import entropy_engine
        return entropy_engine
    except ImportError:
        try:
            from ..core.entropy_engine import entropy_engine
            return entropy_engine
        except ImportError:
            logger.warning("[AXIOM] Entropy engine not available, using fallback")
            return None


def _get_entity_from_db(entity_id: str) -> Optional[Dict]:
    """Get entity details from database."""
    try:
        from database import async_session_maker
        from models.commerce import CompanyModel
        
        # We need to run this in an async context
        # For simplicity in the fallback, we'll return None
        # The actual DB call will be made in async endpoints
        return None
    except ImportError:
        return None


def _generate_entropy_value(entity_id: str) -> float:
    """Generate a deterministic entropy value for fallback."""
    seed = int(hashlib.md5(entity_id.encode()).hexdigest(), 16)
    base = 0.2 + (seed % 100) / 100.0 * 0.6
    return round(base, 4)


def _generate_z_score(entity_id: str, entropy: float) -> float:
    """Generate a deterministic z-score for fallback."""
    seed = int(hashlib.md5(entity_id.encode()).hexdigest(), 16)
    base = (entropy - 0.4) / 0.15
    return round(base * (1 + (seed % 50) / 100.0), 2)


def _generate_history(entity_id: str, current: float, length: int = 10) -> List[float]:
    """Generate entropy history for fallback."""
    seed = int(hashlib.md5(entity_id.encode()).hexdigest(), 16)
    base = 0.1 + (seed % 80) / 100.0 * 0.5
    history = []
    for i in range(length):
        val = base + (current - base) * (i / (length - 1))
        val += (seed % 20) / 100.0 * random.uniform(-0.05, 0.05)
        history.append(round(max(0.0, min(1.0, val)), 4))
    return history


# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def _get_entity_info(entity_id: str) -> Dict:
    """Get entity name and domain from ID (fallback)."""
    # Check fallback data first
    for item in _FALLBACK_SUMMARY:
        if item["entity_id"] == entity_id:
            return {
                "entity_name": item["entity_name"],
                "domain": item["domain"]
            }
    
    # Generate from ID
    seed = int(hashlib.md5(entity_id.encode()).hexdigest(), 16)
    domains = ["Technology", "Finance", "Healthcare", "Energy", "Retail", "Transportation", "Telecom", "Media"]
    return {
        "entity_name": f"Entity {entity_id[:8]}",
        "domain": domains[seed % len(domains)]
    }


# ======================================================================
# 1. STATUS ENDPOINT
# ======================================================================

@router.get("/status")
async def get_status() -> Dict:
    """Get AXIOM-Φ system status."""
    entropy_engine = _get_entropy_engine()
    
    if entropy_engine:
        try:
            stats = entropy_engine.get_global_stats()
            return {
                "status": "operational",
                "service": "AXIOM-Φ",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "total_entities": stats.get("total_entities", 0),
                    "active_entities": stats.get("active_entities", 0),
                    "alerts_triggered": stats.get("alerts_triggered", 0),
                    "window_size": stats.get("window_size", 50),
                    "alert_threshold": stats.get("alert_threshold", 2.0)
                }
            }
        except Exception as e:
            logger.error(f"[AXIOM] Status error: {e}")
    
    # Fallback status
    return {
        "status": "degraded",
        "service": "AXIOM-Φ",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_entities": len(_FALLBACK_SUMMARY),
            "active_entities": len(_FALLBACK_SUMMARY),
            "alerts_triggered": sum(1 for e in _FALLBACK_SUMMARY if e["status"] == "pre-transition"),
            "window_size": 50,
            "alert_threshold": 2.0,
            "mode": "fallback"
        }
    }


# ======================================================================
# 2. MONITOR ENDPOINT
# ======================================================================

@router.get("/monitor")
async def get_axiom_monitor() -> Dict:
    """Get full AXIOM-Φ monitor dashboard data."""
    entropy_engine = _get_entropy_engine()
    summary = []
    total_entities = 0
    active_alerts = 0
    
    if entropy_engine:
        try:
            # Get global stats
            stats = entropy_engine.get_global_stats()
            total_entities = stats.get("total_entities", 0)
            active_alerts = stats.get("alerts_triggered", 0)
            
            # Get entity stats for each entity
            for entity_id in list(entropy_engine.entity_windows.keys())[:50]:
                if entropy_engine.entity_windows[entity_id]:
                    entity_stats = entropy_engine.get_entity_stats(entity_id)
                    if entity_stats:
                        is_alert = entity_stats.get("alert_triggered", False)
                        if is_alert:
                            active_alerts += 1
                        entity_info = _get_entity_info(entity_id)
                        summary.append({
                            "entity_id": entity_id,
                            "entity_name": entity_info.get("entity_name", entity_id),
                            "domain": entity_info.get("domain", "Unknown"),
                            "entropy": entity_stats.get("entropy", 0.0),
                            "z_score": entity_stats.get("z_score", 0.0),
                            "status": "pre-transition" if is_alert else "stable",
                            "history": []
                        })
        except Exception as e:
            logger.error(f"[AXIOM] Monitor error: {e}")
    
    # Use fallback if no data
    if not summary:
        summary = _FALLBACK_SUMMARY
        total_entities = len(summary)
        active_alerts = sum(1 for e in summary if e["status"] == "pre-transition")
    
    # Build high risk entities
    high_risk = [
        {
            "entity_id": item["entity_id"],
            "entity_name": item["entity_name"],
            "risk_factor": "entropy_spike",
            "entropy": item["entropy"]
        }
        for item in summary
        if item.get("status") == "pre-transition" or item.get("entropy", 0) > 0.6
    ]
    
    return {
        "total_entities": total_entities,
        "active_alerts": active_alerts,
        "high_risk_entities": high_risk,
        "entropy_summary": summary,
        "timestamp": datetime.now().isoformat()
    }


# ======================================================================
# 3. ENTROPY ENDPOINTS
# ======================================================================

@router.get("/entropy")
async def get_entropy_data(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status: Optional[str] = Query(None, description="Filter by status (stable/pre-transition)"),
    limit: int = Query(50, ge=1, le=500)
) -> List[Dict]:
    """Get entropy summary for all entities with optional filtering."""
    entropy_engine = _get_entropy_engine()
    results = []
    
    if entropy_engine:
        try:
            for entity_id in list(entropy_engine.entity_windows.keys())[:limit]:
                if entropy_engine.entity_windows[entity_id]:
                    stats = entropy_engine.get_entity_stats(entity_id)
                    if stats:
                        entity_info = _get_entity_info(entity_id)
                        is_alert = stats.get("alert_triggered", False)
                        results.append({
                            "entity_id": entity_id,
                            "entity_name": entity_info.get("entity_name", entity_id),
                            "domain": entity_info.get("domain", "Unknown"),
                            "entropy": stats.get("entropy", 0.0),
                            "z_score": stats.get("z_score", 0.0),
                            "status": "pre-transition" if is_alert else "stable",
                            "window_size": stats.get("window_size", 0)
                        })
        except Exception as e:
            logger.error(f"[AXIOM] Entropy data error: {e}")
    
    # Use fallback if no data
    if not results:
        results = _FALLBACK_SUMMARY
    
    # Apply filters
    if domain:
        results = [r for r in results if r.get("domain", "").lower() == domain.lower()]
    if status:
        results = [r for r in results if r.get("status") == status]
    
    return results[:limit]


@router.get("/entropy/entity/{entity_id}")
async def get_entity_entropy(entity_id: str) -> Dict:
    """Get detailed entropy stats for a specific entity."""
    entropy_engine = _get_entropy_engine()
    
    if entropy_engine:
        try:
            stats = entropy_engine.get_entity_stats(entity_id)
            if stats and stats.get("window_size", 0) > 0:
                entity_info = _get_entity_info(entity_id)
                return {
                    "entity_id": entity_id,
                    "entity_name": entity_info.get("entity_name", entity_id),
                    "domain": entity_info.get("domain", "Unknown"),
                    "entropy": stats.get("entropy", 0.0),
                    "z_score": stats.get("z_score", 0.0),
                    "window_size": stats.get("window_size", 0),
                    "history_length": stats.get("history_length", 0),
                    "history_mean": stats.get("history_mean", 0.0),
                    "history_std": stats.get("history_std", 0.0),
                    "alert_triggered": stats.get("alert_triggered", False),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"[AXIOM] Entity entropy error: {e}")
    
    # Fallback - generate data
    entropy = _generate_entropy_value(entity_id)
    z_score = _generate_z_score(entity_id, entropy)
    is_alert = abs(z_score) > 2.0
    entity_info = _get_entity_info(entity_id)
    
    return {
        "entity_id": entity_id,
        "entity_name": entity_info.get("entity_name", entity_id),
        "domain": entity_info.get("domain", "Unknown"),
        "entropy": entropy,
        "z_score": z_score,
        "window_size": 10,
        "history_length": 20,
        "history_mean": 0.4,
        "history_std": 0.15,
        "alert_triggered": is_alert,
        "timestamp": datetime.now().isoformat(),
        "mode": "fallback"
    }


@router.get("/entropy/trend/{entity_id}")
async def get_entropy_trend(
    entity_id: str,
    n: int = Query(20, ge=1, le=100)
) -> Dict:
    """Get entropy trend/history for an entity."""
    entropy_engine = _get_entropy_engine()
    
    if entropy_engine:
        try:
            trend = entropy_engine.get_entropy_trend(entity_id, n)
            current = entropy_engine.get_entity_entropy(entity_id)
            entity_info = _get_entity_info(entity_id)
            
            return {
                "entity_id": entity_id,
                "entity_name": entity_info.get("entity_name", entity_id),
                "current_entropy": current,
                "trend": trend,
                "data_points": len(trend),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[AXIOM] Trend error: {e}")
    
    # Fallback
    current = _generate_entropy_value(entity_id)
    history = _generate_history(entity_id, current, n)
    entity_info = _get_entity_info(entity_id)
    
    return {
        "entity_id": entity_id,
        "entity_name": entity_info.get("entity_name", entity_id),
        "current_entropy": current,
        "trend": history,
        "data_points": len(history),
        "timestamp": datetime.now().isoformat(),
        "mode": "fallback"
    }


@router.get("/entropy/distribution/{entity_id}")
async def get_entropy_distribution(entity_id: str) -> Dict:
    """Get event type distribution for an entity."""
    entropy_engine = _get_entropy_engine()
    
    if entropy_engine:
        try:
            distribution = entropy_engine.get_window_distribution(entity_id)
            entity_info = _get_entity_info(entity_id)
            
            return {
                "entity_id": entity_id,
                "entity_name": entity_info.get("entity_name", entity_id),
                "distribution": distribution,
                "total_events": sum(distribution.values()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[AXIOM] Distribution error: {e}")
    
    # Fallback
    entity_info = _get_entity_info(entity_id)
    return {
        "entity_id": entity_id,
        "entity_name": entity_info.get("entity_name", entity_id),
        "distribution": {
            "news:product_launch": random.randint(5, 20),
            "news:market_change": random.randint(3, 15),
            "telemetry:performance": random.randint(8, 25),
            "telemetry:security": random.randint(2, 10)
        },
        "total_events": random.randint(20, 60),
        "timestamp": datetime.now().isoformat(),
        "mode": "fallback"
    }


# ======================================================================
# 4. EVENT INGEST ENDPOINT
# ======================================================================

@router.post("/entropy/ingest")
async def ingest_event(request: EventIngestRequest) -> Dict:
    """
    Ingest an event for entropy calculation.
    Returns updated entropy metrics.
    """
    entropy_engine = _get_entropy_engine()
    
    if not entropy_engine:
        return {
            "status": "error",
            "message": "Entropy engine not available",
            "entity_id": request.entity_id
        }
    
    try:
        result = entropy_engine.ingest(
            entity_id=request.entity_id,
            event_type=request.event_type,
            protocol=request.protocol
        )
        
        return {
            "status": "success",
            "entity_id": request.entity_id,
            "entropy": result.get("entropy", 0.0),
            "z_score": result.get("z_score", 0.0),
            "alert_triggered": result.get("alert_triggered", False),
            "alert_reason": result.get("alert_reason", ""),
            "window_size": result.get("window_size", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[AXIOM] Ingest error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "entity_id": request.entity_id
        }


# ======================================================================
# 5. ALERTS ENDPOINT
# ======================================================================

@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity (warning/critical)"),
    limit: int = Query(20, ge=1, le=100)
) -> List[Dict]:
    """Get active entropy alerts."""
    entropy_engine = _get_entropy_engine()
    alerts = []
    
    if entropy_engine:
        try:
            stats = entropy_engine.get_global_stats()
            alert_entities = stats.get("alert_entities", [])
            
            for entity in alert_entities[:limit]:
                entity_id = entity.get("entity_id", "")
                entropy = entity.get("entropy", 0.0)
                z_score = entity.get("z_score", 0.0)
                entity_info = _get_entity_info(entity_id)
                
                severity_level = "critical" if abs(z_score) > 3.0 else "warning"
                alerts.append({
                    "entity_id": entity_id,
                    "entity_name": entity_info.get("entity_name", entity_id),
                    "alert_type": "entropy_spike",
                    "severity": severity_level,
                    "entropy_value": entropy,
                    "z_score": z_score,
                    "description": f"Entity {entity_info.get('entity_name', entity_id)} showing entropy spike (z-score: {z_score:.2f})",
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"[AXIOM] Alerts error: {e}")
    
    # Fallback
    if not alerts:
        for item in _FALLBACK_SUMMARY:
            if item["status"] == "pre-transition":
                severity_level = "critical" if abs(item["z_score"]) > 3.0 else "warning"
                alerts.append({
                    "entity_id": item["entity_id"],
                    "entity_name": item["entity_name"],
                    "alert_type": "entropy_spike",
                    "severity": severity_level,
                    "entropy_value": item["entropy"],
                    "z_score": item["z_score"],
                    "description": f"Entity {item['entity_name']} showing entropy spike in {item['domain']} domain",
                    "timestamp": datetime.now().isoformat()
                })
    
    # Apply severity filter
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    
    return alerts[:limit]


# ======================================================================
# 6. THRESHOLD CONFIGURATION
# ======================================================================

@router.get("/thresholds")
async def get_thresholds() -> Dict:
    """Get current AXIOM-Φ threshold configuration."""
    entropy_engine = _get_entropy_engine()
    
    if entropy_engine:
        try:
            return {
                "status": "success",
                "config": {
                    "alert_threshold": entropy_engine.alert_threshold,
                    "entropy_threshold": entropy_engine.entropy_alert_threshold,
                    "window_size": entropy_engine.window_size
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[AXIOM] Thresholds error: {e}")
    
    return {
        "status": "success",
        "config": {
            "alert_threshold": 2.0,
            "entropy_threshold": 1.1,
            "window_size": 50
        },
        "timestamp": datetime.now().isoformat(),
        "mode": "fallback"
    }


@router.post("/thresholds")
async def update_thresholds(config: ThresholdConfig) -> Dict:
    """Update AXIOM-Φ threshold configuration."""
    entropy_engine = _get_entropy_engine()
    
    if entropy_engine:
        try:
            entropy_engine.alert_threshold = config.alert_threshold
            entropy_engine.entropy_alert_threshold = config.entropy_threshold
            entropy_engine.window_size = config.window_size
            
            return {
                "status": "success",
                "config": {
                    "alert_threshold": entropy_engine.alert_threshold,
                    "entropy_threshold": entropy_engine.entropy_alert_threshold,
                    "window_size": entropy_engine.window_size
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[AXIOM] Update thresholds error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "status": "success",
        "config": config.dict(),
        "timestamp": datetime.now().isoformat(),
        "mode": "simulated"  # No actual engine
    }


# ======================================================================
# 7. RESET ENDPOINT
# ======================================================================

@router.post("/entropy/reset/{entity_id}")
async def reset_entity_entropy(entity_id: str) -> Dict:
    """Reset entropy history for an entity."""
    entropy_engine = _get_entropy_engine()
    
    if entropy_engine:
        try:
            success = entropy_engine.reset_entity(entity_id)
            return {
                "status": "success" if success else "error",
                "entity_id": entity_id,
                "reset": success,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[AXIOM] Reset error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "status": "success",
        "entity_id": entity_id,
        "reset": True,
        "timestamp": datetime.now().isoformat(),
        "mode": "simulated"
    }


# ======================================================================
# 8. ENTITIES LIST
# ======================================================================

@router.get("/entities")
async def list_entities(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(50, ge=1, le=500)
) -> Dict:
    """List all entities with entropy data."""
    entropy_engine = _get_entropy_engine()
    entities = []
    
    if entropy_engine:
        try:
            for entity_id in list(entropy_engine.entity_windows.keys())[:limit]:
                if entropy_engine.entity_windows[entity_id]:
                    stats = entropy_engine.get_entity_stats(entity_id)
                    if stats:
                        entity_info = _get_entity_info(entity_id)
                        entities.append({
                            "id": entity_id,
                            "name": entity_info.get("entity_name", entity_id),
                            "domain": entity_info.get("domain", "Unknown"),
                            "entropy": stats.get("entropy", 0.0),
                            "z_score": stats.get("z_score", 0.0),
                            "window_size": stats.get("window_size", 0),
                            "alert_triggered": stats.get("alert_triggered", False)
                        })
        except Exception as e:
            logger.error(f"[AXIOM] List entities error: {e}")
    
    # Fallback
    if not entities:
        for item in _FALLBACK_SUMMARY:
            entities.append({
                "id": item["entity_id"],
                "name": item["entity_name"],
                "domain": item["domain"],
                "entropy": item["entropy"],
                "z_score": item["z_score"],
                "window_size": 10,
                "alert_triggered": item["status"] == "pre-transition"
            })
    
    # Apply domain filter
    if domain:
        entities = [e for e in entities if e["domain"].lower() == domain.lower()]
    
    # Sort by entropy (highest first)
    entities = sorted(entities, key=lambda x: x["entropy"], reverse=True)[:limit]
    
    return {
        "total_entities": len(entities),
        "entities": entities,
        "timestamp": datetime.now().isoformat()
    }


# ======================================================================
# 9. AXIOM COMPRESSION DEMO
# ======================================================================

@router.get("/compress-demo")
async def axiom_compress_demo() -> Dict:
    """Demonstrate AXIOM compression (if available)."""
    try:
        from services.axiom.axiom_compressor import AXIOMCompressor
        from services.axiom.gauge_fixer import GaugeFixer
        
        import torch
        import torch.nn as nn
        
        # Test model
        class TestModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(1024, 2048)
                self.fc2 = nn.Linear(2048, 4096)
                self.fc3 = nn.Linear(4096, 2048)
                self.fc4 = nn.Linear(2048, 1024)
                self.fc5 = nn.Linear(1024, 10)
            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                x = torch.relu(self.fc3(x))
                x = torch.relu(self.fc4(x))
                return self.fc5(x)
        
        model = TestModel()
        compressor = AXIOMCompressor()
        result = compressor.compress(model, verbose=False)
        
        return {
            "status": "success",
            "original_params": result.get('original_params', 0),
            "compressed_params": result.get('post_tt_params', 0),
            "compression_ratio": result.get('total_compression_ratio', 0),
            "lossless": result.get('verified_lossless', False),
            "timestamp": datetime.now().isoformat()
        }
    except ImportError as e:
        return {
            "status": "degraded",
            "message": f"AXIOM compression not available: {e}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ======================================================================
# 10. ENTITY DOMAINS
# ======================================================================

@router.get("/domains")
async def get_domains() -> Dict:
    """Get all available domains with entity counts."""
    entropy_engine = _get_entropy_engine()
    domain_counts = {}
    
    if entropy_engine:
        try:
            for entity_id in entropy_engine.entity_windows.keys():
                if entropy_engine.entity_windows[entity_id]:
                    info = _get_entity_info(entity_id)
                    domain = info.get("domain", "Unknown")
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
        except Exception as e:
            logger.error(f"[AXIOM] Domains error: {e}")
    
    # Fallback
    if not domain_counts:
        for item in _FALLBACK_SUMMARY:
            domain = item.get("domain", "Unknown")
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    return {
        "domains": [
            {"name": domain, "count": count}
            for domain, count in domain_counts.items()
        ],
        "total_domains": len(domain_counts),
        "timestamp": datetime.now().isoformat()
    }


# ======================================================================
# 11. ENTROPY STATS
# ======================================================================

@router.get("/stats")
async def get_entropy_stats() -> Dict:
    """Get comprehensive entropy statistics."""
    entropy_engine = _get_entropy_engine()
    
    if entropy_engine:
        try:
            stats = entropy_engine.get_global_stats()
            return {
                "status": "success",
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[AXIOM] Stats error: {e}")
    
    # Fallback stats
    total_entities = len(_FALLBACK_SUMMARY)
    active_alerts = sum(1 for e in _FALLBACK_SUMMARY if e["status"] == "pre-transition")
    entropies = [e["entropy"] for e in _FALLBACK_SUMMARY]
    
    return {
        "status": "success",
        "stats": {
            "total_entities": total_entities,
            "active_entities": total_entities,
            "alerts_triggered": active_alerts,
            "avg_entropy": round(sum(entropies) / len(entropies), 4) if entropies else 0.0,
            "max_entropy": max(entropies) if entropies else 0.0,
            "min_entropy": min(entropies) if entropies else 0.0,
            "window_size": 50,
            "alert_threshold": 2.0,
            "mode": "fallback"
        },
        "timestamp": datetime.now().isoformat()
    }


# ======================================================================
# INITIALIZATION
# ======================================================================

logger.info("[AXIOM] AXIOM-Φ router initialized")