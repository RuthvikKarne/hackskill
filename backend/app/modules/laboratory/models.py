"""Laboratory database models.

Tracks lab tests ordered by doctors for patients.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import BaseModel


class LabTest(BaseModel):
    """A laboratory test order."""
    __tablename__ = "lab_tests"
    
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctor_profiles.id"), index=True)
    
    test_name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True) # PENDING, IN_PROGRESS, COMPLETED, CANCELLED
    
    result_text: Mapped[Optional[str]] = mapped_column(Text)
    
    ordered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
