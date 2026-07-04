"""Beds database models.

Tracks hospital beds and their current patient assignments.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import BaseModel


class Bed(BaseModel):
    """A specific bed in a ward."""
    __tablename__ = "beds"
    
    bed_number: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50), default="AVAILABLE", index=True) # AVAILABLE, OCCUPIED, MAINTENANCE
    ward_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wards.id"), index=True)
    
    # Current assignment tracking
    current_assignment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("bed_assignments.id", use_alter=True))


class BedAssignment(BaseModel):
    """A record of a patient assigned to a bed."""
    __tablename__ = "bed_assignments"
    
    bed_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("beds.id"), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True) # ACTIVE, COMPLETED, CANCELLED
