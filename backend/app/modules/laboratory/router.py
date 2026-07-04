"""Laboratory Router.

Exposes endpoints for lab tests and results.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.laboratory.repository import LabTestRepository
from app.modules.laboratory.schemas import LabTestCreate, LabTestResultUpdate, LabTestResponse
from app.modules.laboratory.service import LaboratoryService
from app.shared.response import APIResponse, success_response
from app.shared.pagination import PaginatedResponse, paginate

router = APIRouter()


def get_lab_service(db: AsyncSession = Depends(get_db_session)) -> LaboratoryService:
    repo = LabTestRepository(db)
    return LaboratoryService(repo)


@router.get("", response_model=APIResponse[PaginatedResponse[LabTestResponse]])
async def list_lab_tests(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    lab_service: LaboratoryService = Depends(get_lab_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE", "LAB_TECH"]))
) -> Any:
    """List all lab tests within the actor's hospital."""
    hospital_id = uuid.UUID(user["hospital_id"])
    tests = await lab_service.get_all_tests(hospital_id, skip, limit)
    paginated = paginate(items=tests, total=len(tests), page=(skip // limit) + 1, size=limit)
    return success_response(data=paginated)


@router.post("", response_model=APIResponse[LabTestResponse])
async def order_lab_test(
    request: Request,
    data: LabTestCreate,
    lab_service: LaboratoryService = Depends(get_lab_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR"]))
) -> Any:
    """Order a new lab test for a patient."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    test = await lab_service.order_test(data, hospital_id, actor_id)
    return success_response(data=test, message="Lab test ordered successfully")


@router.patch("/{test_id}/result", response_model=APIResponse[LabTestResponse])
async def update_lab_result(
    test_id: uuid.UUID,
    data: LabTestResultUpdate,
    lab_service: LaboratoryService = Depends(get_lab_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "LAB_TECH"]))
) -> Any:
    """Update lab test results (usually by a Lab Technician)."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    updated_test = await lab_service.update_result(test_id, data, hospital_id, actor_id)
    return success_response(data=updated_test, message="Lab test results updated")
