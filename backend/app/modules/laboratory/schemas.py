"""Laboratory Schemas.

Pydantic models for lab test tracking.
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LabTestCreate(BaseModel):
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    test_name: str


class LabTestResultUpdate(BaseModel):
    result_text: str
    status: str = "COMPLETED"


class LabTestResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    test_name: str
    status: str
    result_text: Optional[str]
    ordered_at: datetime
    completed_at: Optional[datetime]
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True
