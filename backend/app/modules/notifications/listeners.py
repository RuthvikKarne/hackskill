"""Notifications Event Listeners.

Subscribes to EventBus to generate notifications.
"""
from typing import Any

from app.core.database.session import AsyncSessionLocal
from app.core.events.base import BaseEvent
from app.core.events.bus import event_bus
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.service import NotificationService


async def on_low_stock_alert(event: BaseEvent) -> None:
    """Handle low stock alerts from the inventory module."""
    # Note: A real system would lookup the SYS_ADMIN/HOSPITAL_ADMIN for the hospital
    # For simplicity, we assume we just need to create it for the actor who triggered it
    # or a specific admin group. Here, we create one for the actor for demonstration.
    async with AsyncSessionLocal() as session:
        service = NotificationService(NotificationRepository(session))
        
        current_qty = event.payload.get("current_quantity")
        threshold = event.payload.get("threshold")
        msg = f"Low stock alert for item {event.aggregate_id}: {current_qty} remaining (Threshold: {threshold})"
        
        await service.create_notification(
            user_id=event.actor_id,  # Should be the relevant admin/nurse
            hospital_id=event.hospital_id,
            message=msg,
            related_entity_type="InventoryItem",
            related_entity_id=str(event.aggregate_id)
        )
        await session.commit()


async def on_lab_test_completed(event: BaseEvent) -> None:
    """Handle lab test completion."""
    async with AsyncSessionLocal() as session:
        service = NotificationService(NotificationRepository(session))
        
        doctor_id = event.payload.get("doctor_id")
        # In a real app, you would look up the user_id linked to this doctor_id.
        # Since actor_id is the lab tech who completed it, the target is the doctor.
        # We will use actor_id as a fallback for this demo setup.
        
        msg = f"Lab test {event.aggregate_id} for patient {event.payload.get('patient_id')} is completed."
        
        await service.create_notification(
            user_id=event.actor_id, # Should be the doctor
            hospital_id=event.hospital_id,
            message=msg,
            related_entity_type="LabTest",
            related_entity_id=str(event.aggregate_id)
        )
        await session.commit()


def setup_listeners() -> None:
    """Register all listeners to the event bus."""
    event_bus.subscribe("inventory.item.low_stock", on_low_stock_alert)
    event_bus.subscribe("laboratory.test.completed", on_lab_test_completed)
