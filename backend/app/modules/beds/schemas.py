"""Beds Schemas.

Pydantic models for bed and bed assignment CRUD.
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BedBase(BaseModel):
    bed_number: str
    status: str = Field("AVAILABLE", description="AVAILABLE, OCCUPIED, MAINTENANCE")
    ward_id: uuid.UUID


class BedCreate(BedBase):
    pass


class BedResponse(BedBase):
    id: uuid.UUID
    current_assignment_id: Optional[uuid.UUID]
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True


class BedAssignmentCreate(BaseModel):
    bed_id: uuid.UUID
    patient_id: uuid.UUID


class BedAssignmentResponse(BaseModel):
    id: uuid.UUID
    bed_id: uuid.UUID
    patient_id: uuid.UUID
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True
