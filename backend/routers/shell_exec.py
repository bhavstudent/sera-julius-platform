"""
Shell Execution API for Sera
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from services.remote.linux_shell import (
    execute_command_api,
    get_shell_info_api,
    get_system_info_api,
    get_history_api
)
from security.auth import get_current_user

router = APIRouter(prefix="/api/shell", tags=["Linux Shell"])

@router.post("/execute")
async def execute_command(
    command: str,
    session_id: str = "default",
    current_user = Depends(get_current_user)
):
    """Execute a Linux command"""
    return execute_command_api(command, session_id, current_user.get("id"))

@router.get("/status")
async def get_shell_status(current_user = Depends(get_current_user)):
    """Get shell status"""
    return get_shell_info_api(current_user.get("id"))

@router.get("/system-info")
async def get_system_info(current_user = Depends(get_current_user)):
    """Get system information"""
    return get_system_info_api(current_user.get("id"))

@router.get("/history")
async def get_history(
    session_id: str = "default",
    limit: int = 20,
    current_user = Depends(get_current_user)
):
    """Get command history"""
    return get_history_api(session_id, limit)