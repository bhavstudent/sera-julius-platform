"""
Shell Execution API for Sera
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from services.remote.linux_shell import (
    execute_linux,
    get_shell_status,
    get_system_info,
    get_command_history
)
from routers.auth import get_current_user

router = APIRouter(prefix="/api/shell", tags=["Linux Shell"])

@router.post("/execute")
async def execute_command(
    command: str,
    session_id: str = "default",
    current_user = Depends(get_current_user)
):
    """Execute a Linux command"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else "admin"
    return execute_linux(command, session_id, user_id)

@router.get("/status")
async def get_status(current_user = Depends(get_current_user)):
    """Get shell status"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else "admin"
    return get_shell_status(user_id)

@router.get("/system-info")
async def get_sys_info(current_user = Depends(get_current_user)):
    """Get system info"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else "admin"
    return get_system_info(user_id)

@router.get("/history")
async def get_history(session_id: str = "default", limit: int = 20, current_user = Depends(get_current_user)):
    """Get command history"""
    return get_command_history(session_id, limit)
