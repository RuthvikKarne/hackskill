"""Hospitals Service logic.

Handles business logic for hospitals, departments, and wards.
"""
import uuid
from typing import Sequence

from fastapi import HTTPException, status

from app.core.events.bus import event_bus
from app.modules.hospitals.models import Hospital
from app.modules.hospitals.schemas import HospitalCreate
from app.modules.hospitals.repository import HospitalRepository
from app.modules.hospitals.events import HospitalCreatedEvent


class HospitalService:
    """Service layer for hospitals."""
    
    def __init__(self, hospital_repo: HospitalRepository) -> None:
        self.repo = hospital_repo

    async def get_all_hospitals(self, skip: int = 0, limit: int = 100) -> Sequence[Hospital]:
        """Fetch all active hospitals (usually SYS_ADMIN only)."""
        # Note: Since hospitals represent tenants, get_all without a hospital_id filter
        # requires overriding the base repository or accessing the session directly.
        # For this prototype, we'll use a direct query.
        from sqlalchemy import select
        stmt = select(Hospital).where(Hospital.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await self.repo.session.execute(stmt)
        return result.scalars().all()

    async def get_hospital(self, hospital_id: uuid.UUID) -> Hospital:
        """Fetch a single hospital by ID."""
        hospital = await self.repo.get_by_id(hospital_id)
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        return hospital

    async def create_hospital(self, data: HospitalCreate, actor_id: uuid.UUID) -> Hospital:
        """Create a new hospital."""
        hospital_dict = data.model_dump()
        # hospital_id is usually a self-reference for the hospital tenant itself
        new_id = uuid.uuid4()
        hospital_dict["id"] = new_id
        hospital_dict["hospital_id"] = new_id
        hospital_dict["created_by"] = actor_id
        
        hospital = await self.repo.create(**hospital_dict)
        
        event = HospitalCreatedEvent.create(hospital_id=hospital.id, actor_id=actor_id)
        await event_bus.publish(event)
        
        return hospital
