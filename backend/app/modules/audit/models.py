"""Audit database models.

Tracks critical actions across the system for security and compliance.
"""
import uuid
from typing import Optional, Any

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import BaseModel


class AuditLog(BaseModel):
    """A record of a system event or user action."""
    __tablename__ = "audit_logs"
    
    # What happened
    action: Mapped[str] = mapped_column(String(100), index=True)
    
    # Who did it
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), index=True)
    
    # What was affected
    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    
    # Where did it happen
    hospital_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("hospitals.id"), index=True)
    
    # Detailed payload
    # Note: JSON is used here to support SQLite in tests, though JSONB is better for PostgreSQL
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
