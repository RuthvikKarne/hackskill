"""Reports Service logic.

Handles business logic for generating reports.
"""
import uuid
from typing import Sequence

from fastapi import HTTPException

from app.modules.reports.models import Report
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import ReportCreate


class ReportService:
    """Service layer for report generation."""
    
    def __init__(self, repo: ReportRepository) -> None:
        self.repo = repo

    async def get_hospital_reports(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Report]:
        """Fetch past reports for a hospital."""
        return await self.repo.get_hospital_reports(hospital_id=hospital_id, skip=skip, limit=limit)

    async def get_report(self, report_id: uuid.UUID) -> Report:
        """Fetch a specific report."""
        report = await self.repo.get_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report

    async def generate_report(self, data: ReportCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> Report:
        """Generate a new report.
        
        In a real app, this would trigger an async celery task to gather data,
        format a PDF or large JSON, and save the result. Here we stub the result data.
        """
        
        # Stub data gathering based on type
        generated_data = {
            "summary": f"This is a mocked {data.report_type} report.",
            "metrics": {
                "total": 42,
                "status": "Healthy"
            }
        }
        
        return await self.repo.create(
            name=data.name,
            report_type=data.report_type,
            hospital_id=hospital_id,
            data=generated_data,
            created_by=actor_id
        )
