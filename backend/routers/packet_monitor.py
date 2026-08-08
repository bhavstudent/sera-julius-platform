"""
Packet Monitor API for Sera
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from services.monitoring.packet_sniffer import (
    start_packet_monitor,
    stop_packet_monitor,
    get_packet_stats,
    get_packet_detections
)
from routers.auth import get_current_user

router = APIRouter(prefix="/api/packet-monitor", tags=["Packet Monitor"])

@router.post("/start")
async def start_monitor(interface: str = "eth0", current_user = Depends(get_current_user)):
    """Start packet monitoring"""
    result = start_packet_monitor(interface)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result

@router.post("/stop")
async def stop_monitor(current_user = Depends(get_current_user)):
    """Stop packet monitoring"""
    return stop_packet_monitor()

@router.get("/stats")
async def get_stats(current_user = Depends(get_current_user)):
    """Get packet monitor stats"""
    return get_packet_stats()

@router.get("/detections")
async def get_detections(limit: int = 20, current_user = Depends(get_current_user)):
    """Get packet detections"""
    return get_packet_detections(limit)