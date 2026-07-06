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
