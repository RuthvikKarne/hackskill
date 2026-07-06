"""Inventory Schemas.

Pydantic models for inventory item CRUD.
"""
import uuid
from typing import Optional
from pydantic import BaseModel, Field


class InventoryItemBase(BaseModel):
    name: str
    category: str = Field(..., description="Medication, Supply, or Equipment")
    quantity: int = Field(0, ge=0)
    unit: str
    low_stock_threshold: int = Field(10, ge=0)
    location: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = None
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    location: Optional[str] = None


class InventoryItemResponse(InventoryItemBase):
    id: uuid.UUID
    hospital_id: uuid.UUID
    
    class Config:
        from_attributes = True
