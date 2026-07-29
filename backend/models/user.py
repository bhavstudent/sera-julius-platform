"""
SERA User Model
================
SQLAlchemy model for Admin Authentication & Role-Based Access Control (RBAC).
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from database import Base


def _gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """Represents a system user (Admin, Operator, Analyst)."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_gen_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(32), nullable=False, default="ANALYST")
    # Roles: SUPER_ADMIN | SECURITY_OPERATOR | ANALYST

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
