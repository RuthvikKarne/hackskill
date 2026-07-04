"""Doctors Service logic.

Handles business logic for doctors and their patients.
"""
import uuid
from typing import Sequence

from fastapi import HTTPException, status

from app.core.events.bus import event_bus
from app.modules.doctors.models import DoctorProfile, DoctorPatientAssignment
from app.modules.doctors.repository import DoctorProfileRepository, DoctorPatientAssignmentRepository
from app.modules.doctors.schemas import DoctorProfileCreate, DoctorPatientAssignmentCreate
from app.modules.doctors.events import DoctorProfileCreatedEvent, PatientAssignedToDoctorEvent


class DoctorService:
    """Service layer for doctors."""
    
    def __init__(
        self, 
        profile_repo: DoctorProfileRepository, 
        assignment_repo: DoctorPatientAssignmentRepository
    ) -> None:
        self.profile_repo = profile_repo
        self.assignment_repo = assignment_repo

    async def get_all_doctors(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[DoctorProfile]:
        """Fetch all doctor profiles for a specific hospital."""
        return await self.profile_repo.get_all(skip=skip, limit=limit)

    async def create_profile(self, data: DoctorProfileCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> DoctorProfile:
        """Create a new doctor profile."""
        profile = await self.profile_repo.create(
            user_id=data.user_id,
            specialty=data.specialty,
            license_number=data.license_number,
            bio=data.bio,
            department_id=data.department_id,
            created_by=actor_id
        )
        
        event = DoctorProfileCreatedEvent.create(
            profile_id=profile.id,
            user_id=profile.user_id,
            hospital_id=hospital_id,
            actor_id=actor_id
        )
        await event_bus.publish(event)
        
        return profile

    async def assign_patient(self, data: DoctorPatientAssignmentCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> DoctorPatientAssignment:
        """Assign a patient to a doctor."""
        assignment = await self.assignment_repo.create(
            doctor_id=data.doctor_id,
            patient_id=data.patient_id,
            role=data.role,
            created_by=actor_id
        )
        
        event = PatientAssignedToDoctorEvent.create(
            assignment_id=assignment.id,
            doctor_id=assignment.doctor_id,
            patient_id=assignment.patient_id,
            hospital_id=hospital_id,
            actor_id=actor_id
        )
        await event_bus.publish(event)
        
        return assignment
