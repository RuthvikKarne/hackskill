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
