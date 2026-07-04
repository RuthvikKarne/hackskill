"""Audit Schemas.

Pydantic models for fetching audit logs.
"""
import uuid
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    action: str
    actor_id: Optional[uuid.UUID]
    entity_type: str
    entity_id: str
    hospital_id: Optional[uuid.UUID]
    details: dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True
