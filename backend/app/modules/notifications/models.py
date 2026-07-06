"""Notifications database models.

Stores system notifications for users (e.g. low stock alerts, test results).
"""
import uuid
from typing import Optional

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import BaseModel


class Notification(BaseModel):
    """An alert or message meant for a specific user."""
    __tablename__ = "notifications"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    message: Mapped[str] = mapped_column(String(500))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Metadata to link back to the triggering entity (e.g., "LabTest", "123")
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(100))
    related_entity_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Allows filtering by hospital
    hospital_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hospitals.id"), index=True)
