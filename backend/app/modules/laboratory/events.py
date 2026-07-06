"""Laboratory Domain Events.

Events published by the laboratory module.
"""
import uuid
from typing import Any

from app.core.events.base import BaseEvent


class LabTestOrderedEvent(BaseEvent):
    """Fired when a doctor orders a lab test."""
    event_type: str = "laboratory.test.ordered"
    aggregate_type: str = "LabTest"
    
    @classmethod
    def create(cls, test_id: uuid.UUID, patient_id: uuid.UUID, doctor_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "LabTestOrderedEvent":
        return cls(
            aggregate_id=test_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={
                "patient_id": str(patient_id),
                "doctor_id": str(doctor_id)
            },
        )


class LabTestCompletedEvent(BaseEvent):
    """Fired when a lab test is completed and results are available."""
    event_type: str = "laboratory.test.completed"
    aggregate_type: str = "LabTest"
    
    @classmethod
    def create(cls, test_id: uuid.UUID, patient_id: uuid.UUID, doctor_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "LabTestCompletedEvent":
        return cls(
            aggregate_id=test_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={
                "patient_id": str(patient_id),
                "doctor_id": str(doctor_id)
            },
        )
