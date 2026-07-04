"""Authentication Domain Events.

Events published by the auth module.
"""
from typing import Any
import uuid

from app.core.events.base import BaseEvent

class UserLoggedInEvent(BaseEvent):
    """Fired when a user successfully logs in."""
    event_type: str = "auth.user.logged_in"
    aggregate_type: str = "User"
    
    @classmethod
    def create(cls, user_id: uuid.UUID, hospital_id: uuid.UUID, ip_address: str | None) -> "UserLoggedInEvent":
        """Factory for UserLoggedInEvent."""
        return cls(
            aggregate_id=user_id,
            hospital_id=hospital_id,
            actor_id=user_id,
            payload={"ip_address": ip_address},
        )
