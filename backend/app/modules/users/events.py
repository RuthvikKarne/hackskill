"""Users Domain Events.

Events published by the users module.
"""
import uuid
from typing import Any

from app.core.events.base import BaseEvent

class UserCreatedEvent(BaseEvent):
    """Fired when a new user is created in the system."""
    event_type: str = "users.user.created"
    aggregate_type: str = "User"
    
    @classmethod
    def create(cls, user_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID, role_id: uuid.UUID) -> "UserCreatedEvent":
        return cls(
            aggregate_id=user_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={"role_id": str(role_id)},
        )
