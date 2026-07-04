"""Beds Router.

Exposes endpoints for bed CRUD and patient assignments.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.beds.repository import BedRepository, BedAssignmentRepository
from app.modules.beds.schemas import BedCreate, BedResponse, BedAssignmentCreate, BedAssignmentResponse
from app.modules.beds.service import BedService
from app.shared.response import APIResponse, success_response
from app.shared.pagination import PaginatedResponse, paginate

router = APIRouter()


def get_bed_service(db: AsyncSession = Depends(get_db_session)) -> BedService:
    bed_repo = BedRepository(db)
    assignment_repo = BedAssignmentRepository(db)
    return BedService(bed_repo, assignment_repo)


@router.get("", response_model=APIResponse[PaginatedResponse[BedResponse]])
async def list_beds(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    bed_service: BedService = Depends(get_bed_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "NURSE", "DOCTOR"]))
) -> Any:
    """List all beds within the actor's hospital."""
    hospital_id = uuid.UUID(user["hospital_id"])
    beds = await bed_service.get_all_beds(hospital_id, skip, limit)
    paginated = paginate(items=beds, total=len(beds), page=(skip // limit) + 1, size=limit)
    return success_response(data=paginated)


@router.post("", response_model=APIResponse[BedResponse])
async def create_bed(
    request: Request,
    data: BedCreate,
    bed_service: BedService = Depends(get_bed_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """Create a new bed in a ward."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    new_bed = await bed_service.create_bed(data, hospital_id, actor_id)
    return success_response(data=new_bed, message="Bed created successfully")


@router.post("/assign", response_model=APIResponse[BedAssignmentResponse])
async def assign_bed(
    request: Request,
    data: BedAssignmentCreate,
    bed_service: BedService = Depends(get_bed_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "NURSE", "DOCTOR"]))
) -> Any:
    """Assign a patient to an available bed."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    assignment = await bed_service.assign_bed(data, hospital_id, actor_id)
    return success_response(data=assignment, message="Bed assigned successfully")


@router.post("/assignments/{assignment_id}/release", response_model=APIResponse[BedAssignmentResponse])
async def release_bed(
    assignment_id: uuid.UUID,
    bed_service: BedService = Depends(get_bed_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "NURSE", "DOCTOR"]))
) -> Any:
    """Release a patient from a bed."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    assignment = await bed_service.release_bed(assignment_id, hospital_id, actor_id)
    return success_response(data=assignment, message="Bed released successfully")
