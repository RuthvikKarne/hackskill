"""Emergency Domain Events.

Events published by the emergency module.
"""
import uuid
from typing import Any

from app.core.events.base import BaseEvent


class EmergencyDeclaredEvent(BaseEvent):
    """Fired when a mass casualty or major emergency is declared."""
    event_type: str = "emergency.incident.declared"
    aggregate_type: str = "EmergencyIncident"
    
    @classmethod
    def create(cls, incident_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID, severity: str) -> "EmergencyDeclaredEvent":
        return cls(
            aggregate_id=incident_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={"severity": severity},
        )


class AmbulanceDispatchedEvent(BaseEvent):
    """Fired when an ambulance is sent to an incident."""
    event_type: str = "emergency.ambulance.dispatched"
    aggregate_type: str = "Ambulance"
    
    @classmethod
    def create(cls, ambulance_id: uuid.UUID, incident_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "AmbulanceDispatchedEvent":
        return cls(
            aggregate_id=ambulance_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={"incident_id": str(incident_id)},
        )
