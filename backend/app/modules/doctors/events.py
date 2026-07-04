"""Doctors Domain Events.

Events published by the doctors module.
"""
import uuid
from typing import Any

from app.core.events.base import BaseEvent


class DoctorProfileCreatedEvent(BaseEvent):
    """Fired when a doctor profile is registered."""
    event_type: str = "doctors.profile.created"
    aggregate_type: str = "DoctorProfile"
    
    @classmethod
    def create(cls, profile_id: uuid.UUID, user_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "DoctorProfileCreatedEvent":
        return cls(
            aggregate_id=profile_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={"user_id": str(user_id)},
        )


class PatientAssignedToDoctorEvent(BaseEvent):
    """Fired when a patient is assigned to a doctor."""
    event_type: str = "doctors.patient.assigned"
    aggregate_type: str = "DoctorPatientAssignment"
    
    @classmethod
    def create(cls, assignment_id: uuid.UUID, doctor_id: uuid.UUID, patient_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "PatientAssignedToDoctorEvent":
        return cls(
            aggregate_id=assignment_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={
                "doctor_id": str(doctor_id),
                "patient_id": str(patient_id)
            },
        )
