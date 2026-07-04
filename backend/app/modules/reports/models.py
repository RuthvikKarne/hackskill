"""Reports database models.

Stores generated system reports (e.g. daily admissions, inventory usage).
"""
import uuid
from typing import Optional, Any

from sqlalchemy import String, ForeignKey
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import BaseModel


class Report(BaseModel):
    """A generated report."""
    __tablename__ = "reports"
    
    name: Mapped[str] = mapped_column(String(255), index=True)
    report_type: Mapped[str] = mapped_column(String(50), index=True) # E.g., ADMISSIONS, INVENTORY, LAB_TESTS
    
    hospital_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hospitals.id"), index=True)
    
    # Store the actual report data as JSON for simplicity (could also be an S3 URI to a PDF/CSV)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
