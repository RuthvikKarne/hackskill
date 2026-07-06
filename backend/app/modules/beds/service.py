"""Beds Service logic.

Handles business logic for bed tracking and patient assignments.
"""
import uuid
from datetime import datetime
from typing import Sequence

from fastapi import HTTPException, status

from app.core.events.bus import event_bus
from app.modules.beds.models import Bed, BedAssignment
from app.modules.beds.repository import BedRepository, BedAssignmentRepository
from app.modules.beds.schemas import BedCreate, BedAssignmentCreate
from app.modules.beds.events import BedAssignedEvent, BedReleasedEvent


class BedService:
    """Service layer for beds."""
    
    def __init__(self, bed_repo: BedRepository, assignment_repo: BedAssignmentRepository) -> None:
        self.bed_repo = bed_repo
        self.assignment_repo = assignment_repo

    async def get_all_beds(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Bed]:
        """Fetch all beds for a specific hospital."""
        # Typically filtered by ward.id -> hospital.id, requires a join in real impl.
        # Placeholder for basic get_all
        return await self.bed_repo.get_all(skip=skip, limit=limit)

    async def create_bed(self, data: BedCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> Bed:
        """Create a new bed."""
        bed = await self.bed_repo.create(
            bed_number=data.bed_number,
            status=data.status,
            ward_id=data.ward_id,
            created_by=actor_id
        )
        return bed

    async def assign_bed(self, data: BedAssignmentCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> BedAssignment:
        """Assign a patient to a bed."""
        bed = await self.bed_repo.get_by_id(data.bed_id)
        if not bed:
            raise HTTPException(status_code=404, detail="Bed not found")
            
        if bed.status != "AVAILABLE":
            raise HTTPException(status_code=400, detail="Bed is not available")
            
        # Create assignment
        assignment = await self.assignment_repo.create(
            bed_id=data.bed_id,
            patient_id=data.patient_id,
            status="ACTIVE",
            created_by=actor_id
        )
        
        # Update bed status
        await self.bed_repo.update(bed.id, status="OCCUPIED", current_assignment_id=assignment.id)
        
        # Emit event
        event = BedAssignedEvent.create(
            assignment_id=assignment.id,
            bed_id=bed.id,
            patient_id=data.patient_id,
            hospital_id=hospital_id,
            actor_id=actor_id
        )
        await event_bus.publish(event)
        
        return assignment
        
    async def release_bed(self, assignment_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> BedAssignment:
        """Release a bed assignment."""
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.status != "ACTIVE":
            raise HTTPException(status_code=404, detail="Active assignment not found")
            
        # Update assignment
        updated_assignment = await self.assignment_repo.update(
            assignment_id, 
            status="COMPLETED", 
            end_time=datetime.utcnow(),
            updated_by=actor_id
        )
        
        # Update bed status
        await self.bed_repo.update(
            updated_assignment.bed_id, 
            status="AVAILABLE", 
            current_assignment_id=None,
            updated_by=actor_id
        )
        
        # Emit event
        event = BedReleasedEvent.create(
            assignment_id=assignment.id,
            bed_id=updated_assignment.bed_id,
            patient_id=updated_assignment.patient_id,
            hospital_id=hospital_id,
            actor_id=actor_id
        )
        await event_bus.publish(event)
        
        return updated_assignment
