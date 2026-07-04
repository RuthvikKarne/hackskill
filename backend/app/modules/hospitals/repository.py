"""Hospitals Repository.

Handles DB access for Hospital, Department, and Ward models.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.hospitals.models import Hospital, Department, Ward


class HospitalRepository(BaseRepository[Hospital]):
    """Repository for Hospital model interactions."""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Hospital, session=session)


class DepartmentRepository(BaseRepository[Department]):
    """Repository for Department model interactions."""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Department, session=session)


class WardRepository(BaseRepository[Ward]):
    """Repository for Ward model interactions."""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Ward, session=session)
