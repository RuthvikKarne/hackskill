"""Patients Domain Events.

Events published by the patients module.
"""
import uuid
from typing import Any

from app.core.events.base import BaseEvent

class PatientRegisteredEvent(BaseEvent):
    """Fired when a new patient is registered in the hospital."""
    event_type: str = "patients.patient.registered"
    aggregate_type: str = "Patient"
    
    @classmethod
    def create(cls, patient_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "PatientRegisteredEvent":
        return cls(
            aggregate_id=patient_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={},
        )
