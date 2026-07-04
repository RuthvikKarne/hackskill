"""Doctors Repository.

Handles DB access for DoctorProfile and DoctorPatientAssignment.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.doctors.models import DoctorProfile, DoctorPatientAssignment


class DoctorProfileRepository(BaseRepository[DoctorProfile]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=DoctorProfile, session=session)


class DoctorPatientAssignmentRepository(BaseRepository[DoctorPatientAssignment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=DoctorPatientAssignment, session=session)
