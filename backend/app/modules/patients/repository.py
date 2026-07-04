"""Patients Repository.

Handles DB access for Patient models.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.patients.models import Patient


class PatientRepository(BaseRepository[Patient]):
    """Repository for Patient model interactions."""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Patient, session=session)
