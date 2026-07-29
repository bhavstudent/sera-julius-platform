"""
SERA Censys Router
===================
REST endpoints exposing Censys internet-scan data.

GET  /api/censys/lookup/{ip}        — Full host data for an IP
GET  /api/censys/search             — Search Censys (q= param)
GET  /api/censys/exposure           — Check domain exposure (domain= param)
GET  /api/censys/enrich/{ip}        — Enrich a STYX detection with Censys data
GET  /api/censys/status             — Check if Censys is configured & working
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from services.censys_service import censys_service

logger = logging.getLogger("sera.routers.censys")
router = APIRouter(prefix="/api/censys", tags=["censys"])


@router.get("/status", summary="Check Censys API connectivity")
async def censys_status():
    return {
        "available": censys_service.is_available,
        "message": (
            "Censys connected and ready." if censys_service.is_available
            else "Censys not configured. Set CENSYS_API_ID and CENSYS_API_SECRET in .env"
        ),
        "api_id_set": bool(censys_service.api_id),
        "api_secret_set": bool(censys_service.api_secret),
    }


@router.get("/lookup/{ip}", summary="Full Censys host data for an IP address")
async def lookup_ip(ip: str):
    """
    Returns all publicly-known information about an IP:
    open ports, running services, software versions, TLS certificates,
    geographic location, ASN.
    """
    result = await censys_service.lookup_ip(ip)
    if "error" in result and "rate_limit" not in result.get("error", ""):
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/search", summary="Search Censys for matching hosts")
async def search_hosts(
    q: str = Query(..., description="Censys search query. E.g. 'services.port=6379 and location.country=IN'"),
    limit: int = Query(25, ge=1, le=100, description="Max results to return")
):
    """
    Search the entire Censys internet dataset.
    Useful for finding exposed services, vulnerable software, or attacker infrastructure.
    """
    results = await censys_service.search_hosts(q, max_results=limit)
    return {"query": q, "count": len(results), "results": results}


@router.get("/exposure", summary="Check public exposure of a domain")
async def check_exposure(
    domain: str = Query(..., description="Domain to check. E.g. 'example.com'")
):
    """
    Returns what attackers can see about a domain:
    - How many IPs are associated
    - What ports are open across all those IPs
    - Risk score (0-100)
    """
    result = await censys_service.check_exposure(domain)
    return result


@router.get("/enrich/{ip}", summary="Enrich a STYX detection with Censys context")
async def enrich_styx(ip: str):
    """
    Used after STYX detects an anomaly — enriches the suspicious IP
    with Censys data to determine if it's known attacker infrastructure,
    a Tor exit node, an exposed server, etc.
    """
    result = await censys_service.enrich_styx_detection(ip)
    return result


@router.get("/recon", summary="Get real Censys recon data for a target scope")
async def get_recon_data(
    scope: str = Query(..., description="Target scope string. E.g. '10.0.1.0/24, api.example.com'")
):
    """
    Called by the AI security pipeline to get REAL internet-scan data
    for a target scope instead of AI-guessing. Returns actual open ports,
    services, and exposure details for all IPs and domains in scope.
    """
    result = await censys_service.get_recon_data(scope)
    return result
