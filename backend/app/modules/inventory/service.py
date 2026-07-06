"""Inventory Service logic.

Handles business logic for inventory management and stock checking.
"""
import uuid
from typing import Sequence

from fastapi import HTTPException, status

from app.core.events.bus import event_bus
from app.modules.inventory.models import InventoryItem
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import InventoryItemCreate, InventoryItemUpdate
from app.modules.inventory.events import InventoryItemCreatedEvent, LowStockAlertEvent


class InventoryService:
    """Service layer for inventory."""
    
    def __init__(self, inventory_repo: InventoryRepository) -> None:
        self.repo = inventory_repo

    async def get_all_items(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[InventoryItem]:
        """Fetch all inventory items for a specific hospital."""
        return await self.repo.get_all(hospital_id=hospital_id, skip=skip, limit=limit)

    async def get_item(self, item_id: uuid.UUID) -> InventoryItem:
        """Fetch a single inventory item by ID."""
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        return item

    async def create_item(self, data: InventoryItemCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> InventoryItem:
        """Create a new inventory item."""
        item = await self.repo.create(
            name=data.name,
            category=data.category,
            quantity=data.quantity,
            unit=data.unit,
            low_stock_threshold=data.low_stock_threshold,
            location=data.location,
            hospital_id=hospital_id,
            created_by=actor_id
        )
        
        # Fire event
        event = InventoryItemCreatedEvent.create(
            item_id=item.id,
            hospital_id=hospital_id,
            actor_id=actor_id,
        )
        await event_bus.publish(event)
        
        # Check stock on creation
        await self._check_stock(item, hospital_id, actor_id)
        
        return item
        
    async def update_stock(self, item_id: uuid.UUID, new_quantity: int, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> InventoryItem:
        """Update the stock quantity for an item."""
        item = await self.get_item(item_id)
        
        if item.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify inventory of another hospital"
            )
            
        updated_item = await self.repo.update(item_id, quantity=new_quantity, updated_by=actor_id)
        
        # Check stock alert
        await self._check_stock(updated_item, hospital_id, actor_id)
        
        return updated_item
        
    async def _check_stock(self, item: InventoryItem, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        """Internal helper to emit an event if stock is low."""
        if item.quantity <= item.low_stock_threshold:
            event = LowStockAlertEvent.create(
                item_id=item.id,
                hospital_id=hospital_id,
                actor_id=actor_id,
                current_quantity=item.quantity,
                threshold=item.low_stock_threshold
            )
            await event_bus.publish(event)
