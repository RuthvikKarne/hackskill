"""Laboratory Service logic.

Handles business logic for lab tests and results.
"""
import uuid
from datetime import datetime
from typing import Sequence

from fastapi import HTTPException, status

from app.core.events.bus import event_bus
from app.modules.laboratory.models import LabTest
from app.modules.laboratory.repository import LabTestRepository
from app.modules.laboratory.schemas import LabTestCreate, LabTestResultUpdate
from app.modules.laboratory.events import LabTestOrderedEvent, LabTestCompletedEvent


class LaboratoryService:
    """Service layer for laboratory."""
    
    def __init__(self, lab_repo: LabTestRepository) -> None:
        self.repo = lab_repo

    async def get_all_tests(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[LabTest]:
        """Fetch all lab tests for a specific hospital."""
        return await self.repo.get_all(hospital_id=hospital_id, skip=skip, limit=limit)

    async def get_test(self, test_id: uuid.UUID) -> LabTest:
        """Fetch a single lab test by ID."""
        test = await self.repo.get_by_id(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab test not found"
            )
        return test

    async def order_test(self, data: LabTestCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> LabTest:
        """Order a new lab test."""
        test = await self.repo.create(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            test_name=data.test_name,
            hospital_id=hospital_id,
            created_by=actor_id
        )
        
        event = LabTestOrderedEvent.create(
            test_id=test.id,
            patient_id=test.patient_id,
            doctor_id=test.doctor_id,
            hospital_id=hospital_id,
            actor_id=actor_id
        )
        await event_bus.publish(event)
        
        return test

    async def update_result(self, test_id: uuid.UUID, data: LabTestResultUpdate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> LabTest:
        """Update a lab test with results and mark as completed."""
        test = await self.get_test(test_id)
        
        if test.hospital_id != hospital_id:
            raise HTTPException(status_code=403, detail="Cannot modify lab tests from another hospital")
            
        updated_test = await self.repo.update(
            test_id,
            result_text=data.result_text,
            status=data.status,
            completed_at=datetime.utcnow() if data.status == "COMPLETED" else None,
            updated_by=actor_id
        )
        
        if data.status == "COMPLETED":
            event = LabTestCompletedEvent.create(
                test_id=updated_test.id,
                patient_id=updated_test.patient_id,
                doctor_id=updated_test.doctor_id,
                hospital_id=hospital_id,
                actor_id=actor_id
            )
            await event_bus.publish(event)
            
        return updated_test
