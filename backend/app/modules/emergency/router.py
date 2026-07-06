"""Emergency Router.

Exposes endpoints for incidents, ambulances, and calculations.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.emergency.repository import EmergencyIncidentRepository, AmbulanceRepository
from app.modules.emergency.schemas import (
    EmergencyIncidentCreate, EmergencyIncidentResponse, 
    AmbulanceCreate, AmbulanceResponse, ResourceCalculationResponse
)
from app.modules.emergency.service import EmergencyService
from app.shared.response import APIResponse, success_response
from app.shared.pagination import PaginatedResponse, paginate

router = APIRouter()


def get_emergency_service(db: AsyncSession = Depends(get_db_session)) -> EmergencyService:
    inc_repo = EmergencyIncidentRepository(db)
    amb_repo = AmbulanceRepository(db)
    return EmergencyService(inc_repo, amb_repo)


@router.get("/incidents", response_model=APIResponse[PaginatedResponse[EmergencyIncidentResponse]])
async def list_incidents(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    em_service: EmergencyService = Depends(get_emergency_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE"]))
) -> Any:
    """List all emergency incidents."""
    hospital_id = uuid.UUID(user["hospital_id"])
    incidents = await em_service.get_all_incidents(hospital_id, skip, limit)
    paginated = paginate(items=incidents, total=len(incidents), page=(skip // limit) + 1, size=limit)
    return success_response(data=paginated)


@router.post("/incidents", response_model=APIResponse[EmergencyIncidentResponse])
async def create_incident(
    request: Request,
    data: EmergencyIncidentCreate,
    em_service: EmergencyService = Depends(get_emergency_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR"]))
) -> Any:
    """Declare a new emergency incident."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    incident = await em_service.create_incident(data, hospital_id, actor_id)
    return success_response(data=incident, message="Incident declared successfully")


@router.get("/incidents/{incident_id}/resources", response_model=APIResponse[ResourceCalculationResponse])
async def calculate_incident_resources(
    incident_id: uuid.UUID,
    em_service: EmergencyService = Depends(get_emergency_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE"]))
) -> Any:
    """Calculate the required resources for a given incident."""
    resources = await em_service.calculate_resources(incident_id)
    return success_response(data=resources)


@router.post("/ambulances", response_model=APIResponse[AmbulanceResponse])
async def create_ambulance(
    request: Request,
    data: AmbulanceCreate,
    em_service: EmergencyService = Depends(get_emergency_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """Register or dispatch an ambulance."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    amb = await em_service.create_ambulance(data, hospital_id, actor_id)
    return success_response(data=amb, message="Ambulance created/dispatched")
