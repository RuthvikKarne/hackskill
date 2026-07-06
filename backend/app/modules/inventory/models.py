"""Inventory database models.

Tracks hospital inventory items like medications, supplies, and equipment.
"""
from typing import Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import BaseModel


class InventoryItem(BaseModel):
    """An item in the hospital's inventory."""
    __tablename__ = "inventory_items"
    
    name: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)  # Medication, Supply, Equipment
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    unit: Mapped[str] = mapped_column(String(50))  # e.g., 'boxes', 'vials', 'pieces'
    
    # Alerting threshold
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10)
    
    # Location within hospital
    location: Mapped[Optional[str]] = mapped_column(String(255))
