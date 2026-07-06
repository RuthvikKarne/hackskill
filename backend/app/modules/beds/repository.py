"""Beds Repository.

Handles DB access for Bed and BedAssignment models.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.beds.models import Bed, BedAssignment


class BedRepository(BaseRepository[Bed]):
    """Repository for Bed model interactions."""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Bed, session=session)


class BedAssignmentRepository(BaseRepository[BedAssignment]):
    """Repository for BedAssignment model interactions."""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=BedAssignment, session=session)
