"""Hospitals Domain Events.

Events published by the hospitals module.
"""
import uuid

from app.core.events.base import BaseEvent

class HospitalCreatedEvent(BaseEvent):
    """Fired when a new hospital is created."""
    event_type: str = "hospitals.hospital.created"
    aggregate_type: str = "Hospital"
    
    @classmethod
    def create(cls, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "HospitalCreatedEvent":
        return cls(
            aggregate_id=hospital_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={},
        )
