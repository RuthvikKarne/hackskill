"""Emergency Schemas.

Pydantic models for incidents, ambulances, and resource calculation.
"""
import uuid
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel


class EmergencyIncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str
    status: str = "ACTIVE"
    estimated_patients: int = 0
    location: str


class EmergencyIncidentCreate(EmergencyIncidentBase):
    pass


class EmergencyIncidentResponse(EmergencyIncidentBase):
    id: uuid.UUID
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True


class AmbulanceBase(BaseModel):
    vehicle_number: str
    status: str = "AVAILABLE"
    gps_location: Optional[str] = None
    incident_id: Optional[uuid.UUID] = None


class AmbulanceCreate(AmbulanceBase):
    pass


class AmbulanceResponse(AmbulanceBase):
    id: uuid.UUID
    hospital_id: uuid.UUID
    estimated_arrival_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ResourceCalculationResponse(BaseModel):
    incident_id: uuid.UUID
    beds_required: int
    doctors_required: int
    nurses_required: int
    blood_units_required: int
