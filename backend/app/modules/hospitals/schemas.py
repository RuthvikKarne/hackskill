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
