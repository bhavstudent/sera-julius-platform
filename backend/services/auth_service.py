"""
SERA Authentication Service
============================
JWT token generation/verification, password hashing, and default admin seeding.
"""

import os
import logging
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from sqlalchemy import select
from database import async_session_maker
from models.user import User

logger = logging.getLogger("sera.auth_service")

# Secret key for JWT signing
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sera-super-secret-jwt-key-2026-hyper-secure")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = "sera_salt_2026"
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hmac.compare_digest(hash_password(plain_password), hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT-style bearer token (base64 + HMAC signature)."""
    import base64
    import json

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})

    # Encode header & payload
    header = {"alg": "HS256", "typ": "JWT"}
    header_bytes = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_bytes = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")

    signature_input = f"{header_bytes}.{payload_bytes}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    sig_bytes = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    return f"{header_bytes}.{payload_bytes}.{sig_bytes}"


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify token."""
    import base64
    import json

    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        sig_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(SECRET_KEY.encode(), sig_input, hashlib.sha256).digest()

        # Add padding back for base64 decode
        rem = len(sig_b64) % 4
        if rem:
            sig_b64 += "=" * (4 - rem)
        actual_sig = base64.urlsafe_b64decode(sig_b64)

        if not hmac.compare_digest(actual_sig, expected_sig):
            return None

        # Decode payload
        rem_p = len(payload_b64) % 4
        if rem_p:
            payload_b64 += "=" * (4 - rem_p)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())

        # Check expiry
        if payload.get("exp", 0) < int(datetime.now(timezone.utc).timestamp()):
            return None

        return payload
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        return None


async def seed_default_admin():
    """Ensure a default SUPER_ADMIN user exists on startup."""
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        existing = result.scalars().first()

        if not existing:
            admin_user = User(
                username="admin",
                email="admin@sera.internal",
                hashed_password=hash_password("AdminPass2026!"),
                role="SUPER_ADMIN",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            logger.info("[AUTH] Default admin user created: username='admin', password='AdminPass2026!'")
        else:
            logger.info("[AUTH] Admin user already exists.")
