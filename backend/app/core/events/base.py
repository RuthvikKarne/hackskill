"""BaseEvent — the immutable domain event contract.

Every domain event published through the Event Bus must be a dataclass
that inherits from BaseEvent. This gives us:
- A consistent schema for all events (tracing, auditing, replay).
- Forward-compatible versioning (v field).
- Multi-tenant context always present (hospital_id).
- Actor tracking always present (actor_id).

Usage (in a module's events.py):

    from dataclasses import dataclass, field
    from app.core.events.base import BaseEvent

    @dataclass(frozen=True)
    class PatientRegisteredEvent(BaseEvent):
        event_type: str = field(default="patients.patient.registered", init=False)
        # Event-specific fields:
        patient_name: str = ""
        ward_id: str = ""

Publishing:

    from app.core.events.bus import get_event_bus

    event = PatientRegisteredEvent(
        aggregate_id=patient.id,
        hospital_id=hospital_id,
        actor_id=current_user.id,
        payload={"name": patient.full_name},
    )
    await get_event_bus().publish(event)
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class BaseEvent(abc.ABC):
    """Immutable domain event. All module events inherit from this.

    Fields:
        event_id:       Unique event identifier (UUID4, auto-generated).
        event_type:     Dot-namespaced type string, e.g. "inventory.stock.critical_low".
                        Must be overridden by each subclass using field(default=...).
        aggregate_id:   UUID of the primary entity (patient_id, bed_id, etc.).
        aggregate_type: Class name of the entity (e.g. "Patient", "Medicine").
        hospital_id:    Multi-tenant context — always present.
        actor_id:       UUID of the user who triggered the action.
        timestamp:      UTC timestamp when the event was created (auto-set).
        payload:        Event-specific data as a plain dict (keep flat).
        version:        Schema version. Increment when payload shape changes.
    """

    aggregate_id: UUID
    hospital_id: UUID
    actor_id: UUID
    aggregate_type: str = ""
    payload: dict = field(default_factory=dict)
    version: int = 1
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    @abc.abstractmethod
    def event_type(self) -> str:
        """Dot-namespaced event type string.

        Subclasses must define this as a class-level default or property.
        Convention: "<module>.<entity>.<action>", e.g.:
            "inventory.medicine.stock_critical_low"
            "patients.patient.admitted"
            "beds.bed.status_changed"
        """

    def to_dict(self) -> dict:
        """Serialise the event to a plain dict (for logging and Kafka payloads).

        Returns:
            Dict with all event fields, UUIDs as strings, datetime as ISO string.
        """
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.aggregate_id),
            "aggregate_type": self.aggregate_type,
            "hospital_id": str(self.hospital_id),
            "actor_id": str(self.actor_id),
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "version": self.version,
        }
