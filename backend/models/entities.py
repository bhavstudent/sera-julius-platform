"""
SERA Platform — Entity Data Models
=====================================
An "entity" is any resolved identity in the system — a person,
organization, device, or location that SERA has identified
across multiple data sources.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from database import Base


# ============================================================
# SQLAlchemy Models (for database storage)
# ============================================================

def _gen_uuid() -> str:
    return str(uuid.uuid4())


class ThreatActorModel(Base):
    """SQLAlchemy model for threat actors/groups."""
    __tablename__ = "threat_actors"

    id = Column(String, primary_key=True, default=_gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    aliases = Column(JSON, default=list)
    description = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    motivation = Column(String(100), nullable=True)
    capabilities = Column(JSON, default=list)
    threat_level = Column(String(20), default="medium")
    confidence = Column(Float, default=0.5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(JSON, default=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "aliases": self.aliases or [],
            "description": self.description,
            "country": self.country,
            "industry": self.industry,
            "motivation": self.motivation,
            "capabilities": self.capabilities or [],
            "threat_level": self.threat_level,
            "confidence": self.confidence,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AssetModel(Base):
    """SQLAlchemy model for assets (systems, networks, applications)."""
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=_gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    hostname = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    owner = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    criticality = Column(String(20), default="medium")
    is_cloud = Column(Boolean, default=False)
    cloud_provider = Column(String(50), nullable=True)
    tags = Column(JSON, default=list)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "asset_type": self.asset_type,
            "ip_address": self.ip_address,
            "hostname": self.hostname,
            "domain": self.domain,
            "description": self.description,
            "owner": self.owner,
            "department": self.department,
            "criticality": self.criticality,
            "is_cloud": self.is_cloud,
            "cloud_provider": self.cloud_provider,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================================
# Pydantic Models (for API responses)
# ============================================================

class Entity(BaseModel):
    """A unified cross-domain identity."""
    entity_id: str = Field(default_factory=lambda: f"E-{uuid.uuid4().hex[:6]}")
    entity_type: str
    display_name: str
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    event_count: int = 0
    domains: list[str] = []
    current_embedding: list[float] = []
    entropy_baseline: float = 0.0
    current_entropy: float = 0.0
    transition_state: str = "stable"
    risk_score: float = 0.0


class EntityRelationship(BaseModel):
    """A connection between two entities."""
    source_entity: str
    target_entity: str
    relationship_type: str
    weight: float = 1.0
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class EntityProfile(BaseModel):
    """Full detailed profile of an entity."""
    entity: Entity
    recent_events: list[dict] = []
    relationships: list[EntityRelationship] = []
    entropy_history: list[dict] = []
    domain_breakdown: dict = {}