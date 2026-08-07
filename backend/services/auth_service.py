"""
Auth Service
============
Authentication service for user login, registration, and JWT management.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import UserModel

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", 24))


class AuthService:
    """
    Authentication service for user management and JWT handling.
    """
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserModel]:
        """Get a user by username."""
        result = await db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserModel]:
        """Get a user by email."""
        result = await db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
        role: str = "ANALYST"
    ) -> UserModel:
        """Create a new user."""
        # Check if user exists
        existing = await AuthService.get_user_by_username(db, username)
        if existing:
            raise ValueError(f"User with username '{username}' already exists")
        
        existing_email = await AuthService.get_user_by_email(db, email)
        if existing_email:
            raise ValueError(f"User with email '{email}' already exists")
        
        # Create user
        user = UserModel(
            username=username,
            email=email,
            role=role,
            is_active=True,
            created_at=datetime.utcnow()
        )
        user.hashed_password = AuthService._hash_password(password)
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"[AUTH] User created: {username} ({role})")
        return user
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[UserModel]:
        """Authenticate a user by username and password."""
        user = await AuthService.get_user_by_username(db, username)
        if not user:
            return None
        if not user.is_active:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
    
    @staticmethod
    def generate_token(user: UserModel) -> str:
        """Generate a JWT token for a user."""
        payload = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify a JWT token and return the payload."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}
    
    @staticmethod
    async def seed_default_admin(db: AsyncSession) -> None:
        """Seed a default admin user if none exists."""
        admin = await AuthService.get_user_by_username(db, "admin")
        if admin:
            logger.info("[AUTH] Default admin user already exists")
            return
        
        try:
            admin = await AuthService.create_user(
                db=db,
                username="admin",
                email="admin@sera.com",
                password="admin123",
                role="SUPER_ADMIN"
            )
            logger.info("[AUTH] Default admin user created: admin / admin123")
        except ValueError as e:
            logger.warning(f"[AUTH] Could not create admin: {e}")