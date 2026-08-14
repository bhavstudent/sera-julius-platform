"""
Terminal Router - Linux/WSL Terminal Execution
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

# ✅ FIXED: Use absolute import instead of relative
from services.linux_shell import execute_linux, get_shell_status
from database import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/terminal", tags=["Terminal"])


# ============================================================
# MODELS
# ============================================================

class CommandRequest(BaseModel):
    command: str
    timeout: Optional[int] = 120
    cwd: Optional[str] = None


class CommandResponse(BaseModel):
    id: str
    command: str
    output: str
    error: Optional[str] = None
    exit_code: int
    success: bool
    duration_ms: float
    timestamp: str


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/status")
async def terminal_status():
    """Get terminal/shell status."""
    status = get_shell_status()
    return {
        "status": "ok",
        "operational": status.get("operational", False),
        "backend": status.get("backend", "unknown"),
        "host_os": status.get("host_os", "unknown"),
        "details": status
    }


@router.post("/execute")
async def execute_command(request: CommandRequest):
    """Execute a Linux command."""
    cmd_id = f"cmd_{uuid.uuid4().hex[:8]}"
    
    try:
        result = execute_linux(
            command=request.command,
            timeout=request.timeout,
            cwd=request.cwd
        )
        
        # Log to database
        db.add_event(
            event_id=f"evt_term_{uuid.uuid4().hex[:8]}",
            event_type="terminal_command",
            source="terminal-api",
            data={
                "command": request.command,
                "success": result.get("success", False),
                "exit_code": result.get("exit_code", -1),
                "duration_ms": result.get("duration_ms", 0)
            }
        )
        
        return CommandResponse(
            id=cmd_id,
            command=request.command,
            output=result.get("output", ""),
            error=result.get("error"),
            exit_code=result.get("exit_code", -1),
            success=result.get("success", False),
            duration_ms=result.get("duration_ms", 0),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"[TERMINAL] Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_command_history(limit: int = 20):
    """Get command history."""
    # This would need to be implemented in linux_shell
    return {
        "history": [],
        "limit": limit
    }

