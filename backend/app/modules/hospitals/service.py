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
