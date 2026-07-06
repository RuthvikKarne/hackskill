<<<<<<< HEAD
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.session import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    beds_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    icu_beds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "type": self.type,
            "level": self.level,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "phone": self.phone,
            "email": self.email,
            "beds_capacity": self.beds_capacity,
            "icu_beds": self.icu_beds,
            "status": self.status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
=======
"""Hospitals database models.

Includes Hospital, Department, and Ward models.
"""
import uuid
from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import BaseModel


class Hospital(BaseModel):
    """A healthcare facility (tenant)."""
    __tablename__ = "hospitals"
    
    name: Mapped[str] = mapped_column(String(255), index=True)
    address: Mapped[str] = mapped_column(String(500))
    contact_email: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[str] = mapped_column(String(50))
    region: Mapped[str] = mapped_column(String(100), index=True)
    
    # Relationships
    departments: Mapped[List["Department"]] = relationship(
        back_populates="hospital", cascade="all, delete-orphan"
    )


class Department(BaseModel):
    """A department within a hospital (e.g., Cardiology, Emergency)."""
    __tablename__ = "departments"
    
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(String(255))
    
    # We redefine hospital_id to be a proper foreign key here
    hospital_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hospitals.id"), index=True)
    
    # Relationships
    hospital: Mapped["Hospital"] = relationship(back_populates="departments")
    wards: Mapped[List["Ward"]] = relationship(
        back_populates="department", cascade="all, delete-orphan"
    )


class Ward(BaseModel):
    """A ward within a department."""
    __tablename__ = "wards"
    
    name: Mapped[str] = mapped_column(String(100))
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), index=True)
    
    # Capacity tracking
    total_beds: Mapped[int] = mapped_column(default=0)
    
    # Relationships
    department: Mapped["Department"] = relationship(back_populates="wards")
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
