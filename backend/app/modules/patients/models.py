"""Patients database models.

Includes Patient ORM for storing demographics and medical identifiers.
"""
from datetime import date
from typing import Optional

from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import BaseModel


class Patient(BaseModel):
    """A patient registered in the hospital."""
    __tablename__ = "patients"
    
    # Demographics
    first_name: Mapped[str] = mapped_column(String(100), index=True)
    last_name: Mapped[str] = mapped_column(String(100), index=True)
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String(20))
    
    # Medical Identifiers
    blood_type: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Contact Info
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(255))
    
    # State tracking
    status: Mapped[str] = mapped_column(String(50), default="REGISTERED", index=True)
