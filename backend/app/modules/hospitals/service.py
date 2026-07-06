<<<<<<< HEAD
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.core.exceptions.base import ValidationError
from app.modules.hospitals.models import Hospital
from app.modules.hospitals.repository import HospitalRepository
from app.modules.hospitals.schemas import HospitalCreate, HospitalOut, HospitalUpdate


class HospitalService:
    def __init__(self, repository: HospitalRepository) -> None:
        self.repository = repository

    def _validate_payload(self, payload: HospitalCreate | HospitalUpdate) -> None:
        if isinstance(payload, HospitalCreate):
            if payload.beds_capacity < payload.icu_beds:
                raise ValidationError(
                    message="ICU beds cannot exceed total bed capacity.",
                    fields={"icu_beds": "cannot exceed beds_capacity"},
                )
            return

        if payload.icu_beds is not None and payload.beds_capacity is not None:
            if payload.icu_beds > payload.beds_capacity:
                raise ValidationError(
                    message="ICU beds cannot exceed total bed capacity.",
                    fields={"icu_beds": "cannot exceed beds_capacity"},
                )

    async def create(self, data: HospitalCreate) -> HospitalOut:
        self._validate_payload(data)
        hospital = await self.repository.create(data.model_dump())
        return HospitalOut.model_validate(hospital)

    async def list(self, *, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        items, total = await self.repository.list(page=page, page_size=page_size)
        return {
            "items": [HospitalOut.model_validate(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get(self, hospital_id: UUID) -> HospitalOut:
        hospital = await self.repository.get_by_id(hospital_id)
        if hospital is None:
            from app.core.exceptions.base import NotFoundError
            raise NotFoundError(resource="Hospital", resource_id=hospital_id)
        return HospitalOut.model_validate(hospital)

    async def update(self, hospital_id: UUID, data: HospitalUpdate) -> HospitalOut:
        self._validate_payload(data)
        payload = data.model_dump(exclude_unset=True)
        hospital = await self.repository.update(hospital_id, payload)
        return HospitalOut.model_validate(hospital)

    async def delete(self, hospital_id: UUID) -> dict[str, bool]:
        await self.repository.delete(hospital_id)
        return {"deleted": True}
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
