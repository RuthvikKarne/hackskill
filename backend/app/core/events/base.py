"""Base event definition.

Defines the structure for all domain events in the system.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """The base schema for all domain events.
    
    All events published to the event bus must inherit from this class.
    """
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str
    aggregate_id: uuid.UUID
    aggregate_type: str
    hospital_id: uuid.UUID
    actor_id: uuid.UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any]
    version: int = 1
