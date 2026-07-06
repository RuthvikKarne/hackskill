"""Doctors Schemas.

Pydantic models for doctor profiles.
"""
import uuid
from typing import Optional
from pydantic import BaseModel


class DoctorProfileBase(BaseModel):
    specialty: str
    license_number: str
    bio: Optional[str] = None
    department_id: Optional[uuid.UUID] = None


class DoctorProfileCreate(DoctorProfileBase):
    user_id: uuid.UUID


class DoctorProfileResponse(DoctorProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True


class DoctorPatientAssignmentCreate(BaseModel):
    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    role: str = "PRIMARY"


class DoctorPatientAssignmentResponse(BaseModel):
    id: uuid.UUID
    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    role: str
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True
