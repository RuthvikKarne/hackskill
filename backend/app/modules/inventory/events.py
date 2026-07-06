"""Inventory Domain Events.

Events published by the inventory module.
"""
import uuid
from typing import Any

from app.core.events.base import BaseEvent


class InventoryItemCreatedEvent(BaseEvent):
    """Fired when a new inventory item is added to the system."""
    event_type: str = "inventory.item.created"
    aggregate_type: str = "InventoryItem"
    
    @classmethod
    def create(cls, item_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> "InventoryItemCreatedEvent":
        return cls(
            aggregate_id=item_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={},
        )


class LowStockAlertEvent(BaseEvent):
    """Fired when an inventory item drops below its stock threshold."""
    event_type: str = "inventory.item.low_stock"
    aggregate_type: str = "InventoryItem"
    
    @classmethod
    def create(cls, item_id: uuid.UUID, hospital_id: uuid.UUID, actor_id: uuid.UUID, current_quantity: int, threshold: int) -> "LowStockAlertEvent":
        return cls(
            aggregate_id=item_id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            payload={
                "current_quantity": current_quantity,
                "threshold": threshold
            },
        )
