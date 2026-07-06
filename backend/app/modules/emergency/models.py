"""Emergency database models.

Tracks large scale incidents and ambulance dispatches.
"""
import uuid
from typing import Optional, Any
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import BaseModel


class EmergencyIncident(BaseModel):
    """A mass casualty or critical emergency event."""
    __tablename__ = "emergency_incidents"
    
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    severity: Mapped[str] = mapped_column(String(50), index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True)  # ACTIVE, RESOLVED
    
    estimated_patients: Mapped[int] = mapped_column(Integer, default=0)
    location: Mapped[str] = mapped_column(String(255))
    
    hospital_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hospitals.id"), index=True)


class Ambulance(BaseModel):
    """An ambulance dispatched to an incident."""
    __tablename__ = "ambulances"
    
    vehicle_number: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(50), default="AVAILABLE", index=True) # AVAILABLE, DISPATCHED, EN_ROUTE, ARRIVED
    
    incident_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("emergency_incidents.id"), index=True)
    hospital_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hospitals.id"), index=True)
    
    # Store lat/lng as JSON for simplicity, or just a string "lat,lng"
    gps_location: Mapped[Optional[str]] = mapped_column(String(100))
    estimated_arrival_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
