"""Laboratory Repository.

Handles DB access for LabTest models.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.laboratory.models import LabTest


class LabTestRepository(BaseRepository[LabTest]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=LabTest, session=session)
