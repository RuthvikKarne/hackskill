"""Patients Schemas.

Pydantic models for patient data validation and serialization.
"""
import uuid
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str = Field(..., description="MALE, FEMALE, OTHER")
    blood_type: Optional[str] = None
    contact_phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: str = "REGISTERED"


class PatientCreate(PatientBase):
    """Schema for registering a new patient."""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating patient demographics or status."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: Optional[str] = None
    blood_type: Optional[str] = None


class PatientResponse(PatientBase):
    """Schema for patient representation."""
    id: uuid.UUID
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True
