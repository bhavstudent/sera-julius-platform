"""
Authentication Router
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
import logging
import os
import json

# ✅ FIXED: Use absolute import
from database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ============================================================
# API KEYS - Parse from environment variable
# ============================================================

API_KEYS_ENV = os.getenv("API_KEYS", "")
API_KEYS = {}

if API_KEYS_ENV.strip():
    try:
        parsed = json.loads(API_KEYS_ENV)
        if isinstance(parsed, dict):
            API_KEYS = parsed
        elif isinstance(parsed, list):
            API_KEYS = {k: f"client_{i}" for i, k in enumerate(parsed)}
    except json.JSONDecodeError:
        for val in API_KEYS_ENV.split(","):
            val = val.strip()
            if val:
                API_KEYS[val] = f"client_{val[-4:] if len(val) >= 4 else val}"

# ============================================================
# MODELS
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/login")
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    """
    # Simple mock authentication for now
    # Replace with actual database check
    if request.username == "admin" and request.password == "admin123":
        token = jwt.encode(
            {
                "sub": request.username,
                "exp": datetime.utcnow() + timedelta(hours=1)
            },
            "secret_key",
            algorithm="HS256"
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "username": request.username,
                "role": "admin"
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register")
async def register(request: RegisterRequest):
    """
    Register a new user.
    """
    # Simple mock registration
    # Replace with actual database insertion
    return {
        "status": "success",
        "message": "User registered successfully",
        "username": request.username
    }

@router.get("/status")
async def auth_status():
    """Check authentication service status."""
    return {
        "status": "ok",
        "message": "Auth service is running",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/verify")
async def verify_token(token: Optional[str] = None):
    """
    Verify JWT token validity.
    """
    if not token:
        raise HTTPException(status_code=400, detail="Token required")
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        return {
            "valid": True,
            "user": payload.get("sub"),
            "expires_at": datetime.fromtimestamp(payload.get("exp")).isoformat()
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/keys")
async def list_api_keys():
    """
    List available API keys (admin only).
    """
    return {
        "keys": list(API_KEYS.keys()) if API_KEYS else [],
        "count": len(API_KEYS) if API_KEYS else 0
    }

@router.post("/refresh")
async def refresh_token(token: str):
    """
    Refresh JWT token.
    """
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        new_token = jwt.encode(
            {
                "sub": payload.get("sub"),
                "exp": datetime.utcnow() + timedelta(hours=1)
            },
            "secret_key",
            algorithm="HS256"
        )
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me")
async def get_current_user(request: Request):
    """
    Get current user information from token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        return {
            "username": payload.get("sub"),
            "role": payload.get("role", "user"),
            "authenticated": True
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


