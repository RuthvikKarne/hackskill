"""Analytics Service logic.

Handles business logic for aggregating hospital statistics.
"""
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.patients.models import Patient
from app.modules.beds.models import Bed
from app.modules.inventory.models import InventoryItem
from app.modules.laboratory.models import LabTest
from app.modules.analytics.schemas import DashboardStatsResponse


class AnalyticsService:
    """Service layer for analytics and reporting."""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dashboard_stats(self, hospital_id: uuid.UUID) -> DashboardStatsResponse:
        """Fetch aggregated metrics for a hospital dashboard."""
        
        # 1. Total active patients
        stmt_patients = select(func.count(Patient.id)).where(
            Patient.hospital_id == hospital_id,
            Patient.status.in_(["REGISTERED", "ADMITTED"])
        )
        total_patients = (await self.session.execute(stmt_patients)).scalar() or 0
        
        # 2. Available beds
        # Since beds don't have hospital_id directly (they are linked to wards -> departments -> hospital),
        # for simplicity in this demo, we'll assume they have hospital_id on the base model via multitenancy.
        # Actually, let's look up how it was modeled. Bed has ward_id, but the BaseModel automatically adds hospital_id!
        stmt_beds = select(func.count(Bed.id)).where(
            Bed.hospital_id == hospital_id,
            Bed.status == "AVAILABLE"
        )
        available_beds = (await self.session.execute(stmt_beds)).scalar() or 0
        
        # 3. Low stock inventory items
        stmt_inventory = select(func.count(InventoryItem.id)).where(
            InventoryItem.hospital_id == hospital_id,
            InventoryItem.quantity <= InventoryItem.low_stock_threshold
        )
        low_stock_items = (await self.session.execute(stmt_inventory)).scalar() or 0
        
        # 4. Pending lab tests
        stmt_labs = select(func.count(LabTest.id)).where(
            LabTest.hospital_id == hospital_id,
            LabTest.status == "PENDING"
        )
        pending_lab_tests = (await self.session.execute(stmt_labs)).scalar() or 0
        
        return DashboardStatsResponse(
            total_patients=total_patients,
            available_beds=available_beds,
            low_stock_items=low_stock_items,
            pending_lab_tests=pending_lab_tests
        )
