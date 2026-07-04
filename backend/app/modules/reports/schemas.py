"""Reports Schemas.

Pydantic models for report generation and retrieval.
"""
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class ReportCreate(BaseModel):
    name: str
    report_type: str


class ReportResponse(BaseModel):
    id: uuid.UUID
    name: str
    report_type: str
    hospital_id: uuid.UUID
    created_at: datetime
    data: dict[str, Any]
    
    class Config:
        from_attributes = True
