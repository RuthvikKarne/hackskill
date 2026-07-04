"""Analytics Schemas.

Pydantic models for returning aggregated dashboard statistics.
"""
from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    """Aggregate statistics for a hospital dashboard."""
    total_patients: int
    available_beds: int
    low_stock_items: int
    pending_lab_tests: int
