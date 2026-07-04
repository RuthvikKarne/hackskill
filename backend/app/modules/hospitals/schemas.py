"""Hospitals Schemas.

Pydantic models for hospital requests and responses.
"""
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class HospitalBase(BaseModel):
    name: str = Field(..., description="Hospital Name")
    address: str
    contact_email: str
    contact_phone: str
    region: str


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    region: Optional[str] = None


class HospitalResponse(HospitalBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


class DepartmentBase(BaseModel):
    name: str
    description: str


class DepartmentCreate(DepartmentBase):
    hospital_id: uuid.UUID


class DepartmentResponse(DepartmentBase):
    id: uuid.UUID
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True


class WardBase(BaseModel):
    name: str
    total_beds: int


class WardCreate(WardBase):
    department_id: uuid.UUID


class WardResponse(WardBase):
    id: uuid.UUID
    department_id: uuid.UUID
    
    class Config:
        from_attributes = True
