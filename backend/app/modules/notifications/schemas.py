"""Notifications Schemas.

Pydantic models for fetching notifications.
"""
import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    message: str
    is_read: bool
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    hospital_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
