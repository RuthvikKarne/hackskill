"""Patients Service logic.

Handles business logic for patient registration and tracking.
"""
import uuid
from typing import Sequence

from fastapi import HTTPException, status

from app.core.events.bus import event_bus
from app.modules.patients.models import Patient
from app.modules.patients.repository import PatientRepository
from app.modules.patients.schemas import PatientCreate, PatientUpdate
from app.modules.patients.events import PatientRegisteredEvent


class PatientService:
    """Service layer for patients."""
    
    def __init__(self, patient_repo: PatientRepository) -> None:
        self.repo = patient_repo

    async def get_all_patients(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Patient]:
        """Fetch all active patients for a specific hospital."""
        return await self.repo.get_all(hospital_id=hospital_id, skip=skip, limit=limit)

    async def get_patient(self, patient_id: uuid.UUID) -> Patient:
        """Fetch a single patient by ID."""
        patient = await self.repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        return patient

    async def create_patient(self, data: PatientCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> Patient:
        """Register a new patient."""
        # Create patient
        patient = await self.repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_type=data.blood_type,
            contact_phone=data.contact_phone,
            emergency_contact=data.emergency_contact,
            status=data.status,
            hospital_id=hospital_id,
            created_by=actor_id
        )
        
        # Fire event
        event = PatientRegisteredEvent.create(
            patient_id=patient.id,
            hospital_id=hospital_id,
            actor_id=actor_id,
        )
        await event_bus.publish(event)
        
        return patient
