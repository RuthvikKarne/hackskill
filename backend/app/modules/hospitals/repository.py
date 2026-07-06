from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.base import ConflictError, NotFoundError
from app.modules.hospitals.models import Hospital


class HospitalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, hospital_id: UUID) -> Hospital | None:
        result = await self.session.execute(
            select(Hospital).where(Hospital.id == hospital_id, Hospital.deleted_at.is_(None))
        )
        return result.scalars().first()

    async def list(self, *, page: int = 1, page_size: int = 20) -> tuple[list[Hospital], int]:
        offset = (page - 1) * page_size
        count_result = await self.session.execute(
            select(Hospital).where(Hospital.deleted_at.is_(None)).order_by(Hospital.created_at.desc())
        )
        all_items = list(count_result.scalars().all())
        total = len(all_items)

        result = await self.session.execute(
            select(Hospital)
            .where(Hospital.deleted_at.is_(None))
            .order_by(Hospital.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def create(self, data: dict[str, Any]) -> Hospital:
        existing = await self.session.execute(
            select(Hospital).where(Hospital.code == data["code"], Hospital.deleted_at.is_(None))
        )
        if existing.scalars().first():
            raise ConflictError(resource="Hospital", field="code", value=data["code"])

        hospital = Hospital(**data)
        self.session.add(hospital)
        await self.session.flush()
        return hospital

    async def update(self, hospital_id: UUID, data: dict[str, Any]) -> Hospital:
        hospital = await self.get_by_id(hospital_id)
        if hospital is None:
            raise NotFoundError(resource="Hospital", resource_id=hospital_id)

        if "code" in data and data["code"] != hospital.code:
            existing = await self.session.execute(
                select(Hospital).where(Hospital.code == data["code"], Hospital.id != hospital_id)
            )
            if existing.scalars().first():
                raise ConflictError(resource="Hospital", field="code", value=data["code"])

        for key, value in data.items():
            setattr(hospital, key, value)
        hospital.updated_at = __import__("datetime").datetime.utcnow()
        await self.session.flush()
        return hospital

    async def delete(self, hospital_id: UUID) -> bool:
        hospital = await self.get_by_id(hospital_id)
        if hospital is None:
            raise NotFoundError(resource="Hospital", resource_id=hospital_id)

        hospital.deleted_at = __import__("datetime").datetime.utcnow()
        hospital.is_active = False
        hospital.updated_at = __import__("datetime").datetime.utcnow()
        await self.session.flush()
        return True
