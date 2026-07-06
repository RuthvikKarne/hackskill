"""Doctors database models.

Tracks doctor profiles and their assigned patients.
"""
import uuid
from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import BaseModel


class DoctorProfile(BaseModel):
    """Doctor specific profile linked to a User."""
    __tablename__ = "doctor_profiles"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True, unique=True)
    specialty: Mapped[str] = mapped_column(String(100), index=True)
    license_number: Mapped[str] = mapped_column(String(100), unique=True)
    bio: Mapped[Optional[str]] = mapped_column(String(1000))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id"))


class DoctorPatientAssignment(BaseModel):
    """Assigns a patient to a primary or consulting doctor."""
    __tablename__ = "doctor_patient_assignments"
    
    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctor_profiles.id"), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    role: Mapped[str] = mapped_column(String(50), default="PRIMARY") # PRIMARY, CONSULTING
