"""
Network Scanner API for Sera
"""

import sys
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from services.monitoring.network_scanner import (
    start_network_scan,
    get_scan_status,
    get_scan_results
)
from routers.auth import get_current_user

router = APIRouter(prefix="/api/network-scan", tags=["Network Scanner"])

@router.post("/start")
async def start_scan(ip_range: Optional[str] = None, current_user = Depends(get_current_user)):
    """Start network scan"""
    return start_network_scan(ip_range)

@router.get("/status")
async def get_status(current_user = Depends(get_current_user)):
    """Get scan status"""
    return get_scan_status()

@router.get("/results")
async def get_results(limit: int = 10, current_user = Depends(get_current_user)):
    """Get scan results"""
    return get_scan_results(limit)