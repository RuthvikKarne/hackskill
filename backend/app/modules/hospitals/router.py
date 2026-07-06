<<<<<<< HEAD
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db_session
from app.core.exceptions.base import PermissionDeniedError
from app.core.security.jwt import TokenPayload
from app.core.security.rbac import Permissions, Roles
from app.modules.hospitals.repository import HospitalRepository
from app.modules.hospitals.schemas import HospitalCreate, HospitalListResponse, HospitalOut, HospitalUpdate
from app.modules.hospitals.service import HospitalService
from app.shared.response import created_response, success_response

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


def get_hospital_service(session: AsyncSession = Depends(get_db_session)) -> HospitalService:
    repository = HospitalRepository(session)
    return HospitalService(repository)


def require_hospital_admin(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    if current_user.role not in {Roles.SYSTEM_ADMIN, Roles.HOSPITAL_ADMIN}:
        raise PermissionDeniedError(required_permission=Permissions.HOSPITALS_WRITE)
    return current_user


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_hospital(
    payload: HospitalCreate,
    service: HospitalService = Depends(get_hospital_service),
    _user: TokenPayload = Depends(require_hospital_admin),
    request: Request = None,
) -> JSONResponse:
    hospital = await service.create(payload)
    return created_response(
        data=hospital.model_dump(mode="json"),
        message="Hospital created successfully.",
        request=request,
    )


@router.get("")
async def list_hospitals(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: HospitalService = Depends(get_hospital_service),
    _user: TokenPayload = Depends(get_current_user),
    request: Request = None,
) -> JSONResponse:
    data = await service.list(page=page, page_size=page_size)
    return success_response(
        data={
            "items": [item.model_dump(mode="json") for item in data["items"]],
            "total": data["total"],
            "page": data["page"],
            "page_size": data["page_size"],
        },
        message="Hospitals retrieved successfully.",
        request=request,
    )


@router.get("/{hospital_id}")
async def get_hospital(
    hospital_id: UUID,
    service: HospitalService = Depends(get_hospital_service),
    _user: TokenPayload = Depends(get_current_user),
    request: Request = None,
) -> JSONResponse:
    hospital = await service.get(hospital_id)
    return success_response(data=hospital.model_dump(mode="json"), message="Hospital retrieved successfully.", request=request)


@router.patch("/{hospital_id}")
async def update_hospital(
    hospital_id: UUID,
    payload: HospitalUpdate,
    service: HospitalService = Depends(get_hospital_service),
    _user: TokenPayload = Depends(require_hospital_admin),
    request: Request = None,
) -> JSONResponse:
    hospital = await service.update(hospital_id, payload)
    return success_response(data=hospital.model_dump(mode="json"), message="Hospital updated successfully.", request=request)


@router.delete("/{hospital_id}")
async def delete_hospital(
    hospital_id: UUID,
    service: HospitalService = Depends(get_hospital_service),
    _user: TokenPayload = Depends(require_hospital_admin),
    request: Request = None,
) -> JSONResponse:
    result = await service.delete(hospital_id)
    return success_response(data=result, message="Hospital deleted successfully.", request=request)
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
