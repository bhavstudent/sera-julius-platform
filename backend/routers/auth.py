"""
SERA Auth Router
================
REST endpoints for User Login, Profile, and RBAC Management.

POST /api/auth/login    — Login and retrieve JWT token
GET  /api/auth/me       — Retrieve current user profile
GET  /api/auth/users    — List system users (Admin)
POST /api/auth/users    — Create new user (Admin)
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy import select
from database import async_session_maker
from models.user import User
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

logger = logging.getLogger("sera.routers.auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class CreateUserRequest(BaseModel):
    username: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)
    role: str = Field(default="ANALYST", description="SUPER_ADMIN | SECURITY_OPERATOR | ANALYST")


async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """Dependency to extract & verify user from Bearer Token header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid.")

    username = payload.get("sub")
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()

        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User account is inactive or missing.")

        return user


@router.post("/login", summary="Admin & User Login")
async def login(req: LoginRequest):
    """Authenticate user credentials and issue a JWT token."""
    async with async_session_maker() as session:
        # Search by username or email
        result = await session.execute(
            select(User).where((User.username == req.username) | (User.email == req.username))
        )
        user = result.scalars().first()

        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username/email or password.")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated.")

        # Update last login timestamp
        user.last_login = datetime.utcnow()
        await session.commit()

        # Issue JWT token
        token = create_access_token({"sub": user.username, "role": user.role, "id": user.id})

        logger.info(f"[AUTH] Successful login for '{user.username}' ({user.role})")
        return {
            "token": token,
            "token_type": "bearer",
            "user": user.to_dict(),
            "message": f"Welcome back, {user.username}!"
        }


@router.get("/me", summary="Get Current Authenticated Profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {"user": user.to_dict()}


@router.get("/users", summary="List All Users (Admin)")
async def list_users(user: User = Depends(get_current_user)):
    if user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super Admin role required.")

    async with async_session_maker() as session:
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        return {"users": [u.to_dict() for u in users]}


@router.post("/users", summary="Create User (Admin)")
async def create_user(req: CreateUserRequest, user: User = Depends(get_current_user)):
    if user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super Admin role required.")

    async with async_session_maker() as session:
        # Check duplicate
        result = await session.execute(
            select(User).where((User.username == req.username) | (User.email == req.email))
        )
        if result.scalars().first():
            raise HTTPException(status_code=409, detail="Username or email already exists.")

        new_user = User(
            username=req.username,
            email=req.email,
            hashed_password=hash_password(req.password),
            role=req.role.upper(),
            is_active=True
        )
        session.add(new_user)
        await session.commit()

        logger.info(f"[AUTH] New user created: {new_user.username} ({new_user.role}) by {user.username}")
        return {"user": new_user.to_dict(), "message": f"User {new_user.username} created successfully."}
