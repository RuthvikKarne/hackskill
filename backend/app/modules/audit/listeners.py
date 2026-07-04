"""Audit Event Listeners.

Subscribes to EventBus to generate audit logs for critical actions.
"""
from app.core.database.session import AsyncSessionLocal
from app.core.events.base import BaseEvent
from app.core.events.bus import event_bus
from app.modules.audit.repository import AuditLogRepository
from app.modules.audit.service import AuditService


async def on_critical_event(event: BaseEvent) -> None:
    """Handle critical events and generate audit logs."""
    async with AsyncSessionLocal() as session:
        service = AuditService(AuditLogRepository(session))
        
        await service.create_log(
            action=event.event_type,
            actor_id=event.actor_id,
            entity_type=event.aggregate_type,
            entity_id=str(event.aggregate_id),
            hospital_id=event.hospital_id,
            details=event.payload
        )
        await session.commit()


def setup_listeners() -> None:
    """Register all listeners to the event bus for auditing."""
    # We could subscribe to a wildcard, but explicit subscription is safer.
    # In a real app, you might only audit specific events. Here we audit key ones.
    events_to_audit = [
        "auth.user.login",
        "auth.user.logout",
        "users.user.created",
        "patients.patient.registered",
        "inventory.item.created",
        "beds.bed.assigned",
        "beds.bed.released",
        "laboratory.test.ordered"
    ]
    
    for event_name in events_to_audit:
        event_bus.subscribe(event_name, on_critical_event)
