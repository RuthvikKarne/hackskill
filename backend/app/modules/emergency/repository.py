"""Emergency Repository.

Handles DB access for Incident and Ambulance models.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.emergency.models import EmergencyIncident, Ambulance


class EmergencyIncidentRepository(BaseRepository[EmergencyIncident]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=EmergencyIncident, session=session)


class AmbulanceRepository(BaseRepository[Ambulance]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Ambulance, session=session)
