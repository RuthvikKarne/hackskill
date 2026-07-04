"""Patients Router.

Exposes endpoints for patient CRUD.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.patients.repository import PatientRepository
from app.modules.patients.schemas import PatientCreate, PatientResponse
from app.modules.patients.service import PatientService
from app.shared.response import APIResponse, success_response
from app.shared.pagination import PaginatedResponse, paginate

router = APIRouter()


def get_patient_service(db: AsyncSession = Depends(get_db_session)) -> PatientService:
    repo = PatientRepository(db)
    return PatientService(repo)


@router.get("", response_model=APIResponse[PaginatedResponse[PatientResponse]])
async def list_patients(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    patient_service: PatientService = Depends(get_patient_service),
    # Hospital staff can view patients
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE"]))
) -> Any:
    """List all patients within the actor's hospital."""
    hospital_id = uuid.UUID(user["hospital_id"])
    patients = await patient_service.get_all_patients(hospital_id, skip, limit)
    paginated = paginate(items=patients, total=len(patients), page=(skip // limit) + 1, size=limit)
    return success_response(data=paginated)


@router.post("", response_model=APIResponse[PatientResponse])
async def register_patient(
    request: Request,
    data: PatientCreate,
    patient_service: PatientService = Depends(get_patient_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "NURSE", "DOCTOR"]))
) -> Any:
    """Register a new patient."""
    actor_id = uuid.UUID(user["sub"])
    actor_hospital_id = uuid.UUID(user["hospital_id"])
    
    new_patient = await patient_service.create_patient(data, actor_hospital_id, actor_id)
    return success_response(data=new_patient, message="Patient registered successfully")


@router.get("/{patient_id}", response_model=APIResponse[PatientResponse])
async def get_patient(
    patient_id: uuid.UUID,
    patient_service: PatientService = Depends(get_patient_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "DOCTOR", "NURSE"]))
) -> Any:
    """Get patient details."""
    fetched_patient = await patient_service.get_patient(patient_id)
    return success_response(data=fetched_patient)
