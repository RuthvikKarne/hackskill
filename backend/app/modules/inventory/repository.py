"""Inventory Repository.

Handles DB access for InventoryItem models.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base import BaseRepository
from app.modules.inventory.models import InventoryItem


class InventoryRepository(BaseRepository[InventoryItem]):
    """Repository for InventoryItem model interactions."""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=InventoryItem, session=session)
