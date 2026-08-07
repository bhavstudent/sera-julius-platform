"""
SERA Terminal Router — Exposes the Linux shell as API endpoints.
MERGED FROM JULIUS → SERA PLATFORM
Provides terminal access with Sera authentication
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# Sera imports
import sys
from pathlib import Path
SERA_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SERA_ROOT))

from services.remote.linux_shell import (
    execute_linux, 
    execute_script, 
    get_shell_status,
    get_system_info,
    get_command_history, 
    install_package,
)

# ✅ FIXED: Use Sera's actual auth from main.py
# Try multiple possible auth locations
try:
    from security.measures import get_current_user
except ImportError:
    try:
        from routers.auth import get_current_user
    except ImportError:
        # Fallback: create a simple auth dependency
        from fastapi import Header
        from config import API_KEYS
        
        async def get_current_user(api_key: str = Header(..., alias="X-API-Key")):
            """Fallback auth using API key from config"""
            if api_key not in API_KEYS:
                raise HTTPException(status_code=401, detail="Invalid API key")
            return {"id": API_KEYS[api_key], "username": API_KEYS[api_key]}

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/terminal", tags=["Linux Terminal"])

class CommandRequest(BaseModel):
    command: str
    session_id: str = "default"
    timeout: int = 30

class ScriptRequest(BaseModel):
    script: str
    session_id: str = "default"
    timeout: int = 60

class InstallRequest(BaseModel):
    packages: str

@router.get("/status")
async def terminal_status(current_user = Depends(get_current_user)):
    """Get Linux terminal subsystem status."""
    user_id = current_user.get("id") if current_user else None
    return get_shell_status(user_id)

@router.post("/execute")
async def run_command(req: CommandRequest, current_user = Depends(get_current_user)):
    """Execute a Linux command."""
    user_id = current_user.get("id") if current_user else None
    result = execute_linux(req.command, req.session_id, req.timeout, user_id=user_id)
    return result

@router.post("/script")
async def run_script(req: ScriptRequest, current_user = Depends(get_current_user)):
    """Execute a multi-line bash script."""
    user_id = current_user.get("id") if current_user else None
    result = execute_script(req.script, req.session_id, req.timeout, user_id)
    return result

@router.get("/sysinfo")
async def system_info(current_user = Depends(get_current_user)):
    """Get Linux system information."""
    user_id = current_user.get("id") if current_user else None
    return get_system_info(user_id)

@router.get("/history")
async def command_history(session_id: str = "default", limit: int = 20,
                         current_user = Depends(get_current_user)):
    """Get command history for a session."""
    return get_command_history(session_id, limit)

@router.post("/install")
async def install_packages(req: InstallRequest, current_user = Depends(get_current_user)):
    """Install Linux packages via apt/yum/dnf/pacman."""
    user_id = current_user.get("id") if current_user else None
    return install_package(req.packages, user_id)