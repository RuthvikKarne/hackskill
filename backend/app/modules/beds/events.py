"""Beds Domain Events.

Events published by the beds module.
"""
import uuid
from typing import Any

from app.core.events.base import BaseEvent

class BedAssignedEvent(BaseEvent):
    """Fired when a patient is assigned to a bed."""
    event_type: str = "beds.bed.assigned"
    aggregate_type: str = "BedAssignment"
    
    @classmethod
    def create(cls, assignment_id: uuid.UUID, bed_id: uuid.UUID, patient_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "BedAssignedEvent":
        return cls(
            aggregate_id=assignment_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={
                "bed_id": str(bed_id),
                "patient_id": str(patient_id)
            },
        )


class BedReleasedEvent(BaseEvent):
    """Fired when a patient is discharged/moved from a bed."""
    event_type: str = "beds.bed.released"
    aggregate_type: str = "BedAssignment"
    
    @classmethod
    def create(cls, assignment_id: uuid.UUID, bed_id: uuid.UUID, patient_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "BedReleasedEvent":
        return cls(
            aggregate_id=assignment_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={
                "bed_id": str(bed_id),
                "patient_id": str(patient_id)
            },
        )
