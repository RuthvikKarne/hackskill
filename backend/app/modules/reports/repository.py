"""Reports Repository.

Handles DB access for Report models.
"""
import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.reports.models import Report


class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Report, session=session)

    async def get_hospital_reports(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Report]:
        """Fetch generated reports for a specific hospital, ordered by newest first."""
        stmt = (
            select(self.model)
            .where(self.model.hospital_id == hospital_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
