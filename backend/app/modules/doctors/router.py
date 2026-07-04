"""Doctors Router.

Exposes endpoints for doctor profiles and patient assignments.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.doctors.repository import DoctorProfileRepository, DoctorPatientAssignmentRepository
from app.modules.doctors.schemas import DoctorProfileCreate, DoctorProfileResponse, DoctorPatientAssignmentCreate, DoctorPatientAssignmentResponse
from app.modules.doctors.service import DoctorService
from app.shared.response import APIResponse, success_response
from app.shared.pagination import PaginatedResponse, paginate

router = APIRouter()


def get_doctor_service(db: AsyncSession = Depends(get_db_session)) -> DoctorService:
    profile_repo = DoctorProfileRepository(db)
    assignment_repo = DoctorPatientAssignmentRepository(db)
    return DoctorService(profile_repo, assignment_repo)


@router.get("", response_model=APIResponse[PaginatedResponse[DoctorProfileResponse]])
async def list_doctors(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    doctor_service: DoctorService = Depends(get_doctor_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "NURSE", "DOCTOR"]))
) -> Any:
    """List all doctors within the actor's hospital."""
    hospital_id = uuid.UUID(user["hospital_id"])
    doctors = await doctor_service.get_all_doctors(hospital_id, skip, limit)
    paginated = paginate(items=doctors, total=len(doctors), page=(skip // limit) + 1, size=limit)
    return success_response(data=paginated)


@router.post("", response_model=APIResponse[DoctorProfileResponse])
async def create_doctor_profile(
    request: Request,
    data: DoctorProfileCreate,
    doctor_service: DoctorService = Depends(get_doctor_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """Create a new doctor profile (links to an existing user)."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    new_profile = await doctor_service.create_profile(data, hospital_id, actor_id)
    return success_response(data=new_profile, message="Doctor profile created successfully")


@router.post("/assign", response_model=APIResponse[DoctorPatientAssignmentResponse])
async def assign_patient(
    request: Request,
    data: DoctorPatientAssignmentCreate,
    doctor_service: DoctorService = Depends(get_doctor_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR"]))
) -> Any:
    """Assign a patient to a doctor."""
    actor_id = uuid.UUID(user["sub"])
    hospital_id = uuid.UUID(user["hospital_id"])
    
    assignment = await doctor_service.assign_patient(data, hospital_id, actor_id)
    return success_response(data=assignment, message="Patient assigned to doctor successfully")
