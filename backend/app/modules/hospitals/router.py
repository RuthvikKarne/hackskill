"""Hospitals Router.

Exposes endpoints for hospital CRUD.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole, RequiresPermission
from app.modules.hospitals.schemas import HospitalCreate, HospitalResponse
from app.modules.hospitals.repository import HospitalRepository
from app.modules.hospitals.service import HospitalService
from app.shared.response import APIResponse, success_response
from app.shared.pagination import PaginatedResponse, paginate

router = APIRouter()


def get_hospital_service(db: AsyncSession = Depends(get_db_session)) -> HospitalService:
    repo = HospitalRepository(db)
    return HospitalService(repo)


@router.get("", response_model=APIResponse[PaginatedResponse[HospitalResponse]])
async def list_hospitals(
    skip: int = 0,
    limit: int = 100,
    hospital_service: HospitalService = Depends(get_hospital_service),
    # Only SYS_ADMIN can list all hospitals
    user: dict = Depends(RequiresRole(["SYS_ADMIN"]))
) -> Any:
    """List all hospitals."""
    hospitals = await hospital_service.get_all_hospitals(skip, limit)
    # Note: total count would be fetched in a real implementation
    paginated = paginate(items=hospitals, total=len(hospitals), page=(skip // limit) + 1, size=limit)
    return success_response(data=paginated)


@router.get("/{hospital_id}", response_model=APIResponse[HospitalResponse])
async def get_hospital(
    hospital_id: uuid.UUID,
    hospital_service: HospitalService = Depends(get_hospital_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE"]))
) -> Any:
    """Get hospital details."""
    hospital = await hospital_service.get_hospital(hospital_id)
    return success_response(data=hospital)


@router.post("", response_model=APIResponse[HospitalResponse])
async def create_hospital(
    request: Request,
    data: HospitalCreate,
    hospital_service: HospitalService = Depends(get_hospital_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN"]))
) -> Any:
    """Create a new hospital."""
    actor_id = uuid.UUID(user["sub"])
    hospital = await hospital_service.create_hospital(data, actor_id)
    return success_response(data=hospital, message="Hospital created successfully")
