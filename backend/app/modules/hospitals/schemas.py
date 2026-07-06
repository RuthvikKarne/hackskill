<<<<<<< HEAD
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class HospitalCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Annotated[str, Field(min_length=2, max_length=255)]
    code: Annotated[str, Field(min_length=2, max_length=50)]
    type: Annotated[str, Field(min_length=2, max_length=50)]
    level: Annotated[str, Field(min_length=2, max_length=50)]
    address: Annotated[str, Field(min_length=2, max_length=255)]
    city: Annotated[str, Field(min_length=2, max_length=100)]
    state: Annotated[str, Field(min_length=2, max_length=100)]
    country: Annotated[str, Field(min_length=2, max_length=100)]
    phone: Annotated[str, Field(min_length=5, max_length=30)]
    email: EmailStr
    beds_capacity: Annotated[int, Field(ge=0)]
    icu_beds: Annotated[int, Field(ge=0)]
    status: Annotated[str, Field(default="active")]
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        normalized = value.upper().replace(" ", "-")
        if len(normalized) < 2:
            raise ValueError("code must be at least 2 characters")
        return normalized


class HospitalUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = None
    code: str | None = None
    type: str | None = None
    level: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    beds_capacity: int | None = Field(default=None, ge=0)
    icu_beds: int | None = Field(default=None, ge=0)
    status: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    is_active: bool | None = None


class HospitalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    type: str
    level: str
    address: str
    city: str
    state: str
    country: str
    phone: str
    email: str
    beds_capacity: int
    icu_beds: int
    status: str
    latitude: float | None
    longitude: float | None
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class HospitalListResponse(BaseModel):
    items: list[HospitalOut]
    total: int
    page: int
    page_size: int
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
