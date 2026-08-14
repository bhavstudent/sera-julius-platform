"""
Security Authentication Module
"""
from fastapi import HTTPException, Depends, Header
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
async def secure_endpoint(token: Optional[str] = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
async def get_current_user(token: Optional[str] = Header(None)):
    if not token:
        return {"username": "anonymous", "role": "guest"}
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload.get("sub", "unknown"), "role": payload.get("role", "user")}
    except:
        return {"username": "anonymous", "role": "guest"}
async def get_current_active_user(current_user: dict = Depends(secure_endpoint)):
    return current_user
