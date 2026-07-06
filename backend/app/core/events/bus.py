<<<<<<< HEAD
"""InProcessEventBus — async in-process event dispatcher.

Dispatches domain events to all registered handlers concurrently using
asyncio.gather(). A failure in one handler does NOT block other handlers
or the publishing service (errors are logged and isolated).

Kafka-ready interface:
    The publish() method signature is identical to what a Kafka producer
    adapter would expose. Swapping to Kafka in Phase 2 requires only
    replacing this class — no business code changes.

Lifecycle:
    startup  → init_event_bus() called in main.py lifespan
    runtime  → services call await get_event_bus().publish(event)
    tests    → replace with MockEventBus via override_event_bus()

Usage (in a service):

    from app.core.events.bus import get_event_bus
    from app.modules.inventory.events import StockCriticalLowEvent

    event = StockCriticalLowEvent(
        aggregate_id=medicine.id,
        hospital_id=hospital_id,
        actor_id=actor_id,
        payload={"medicine_name": medicine.name, "current_stock": 5},
    )
    await get_event_bus().publish(event)
=======
"""In-process Event Bus.

Handles asynchronous dispatching of domain events to registered subscribers.
Designed to be easily swapped with a Kafka-backed bus in the future.
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
"""
from __future__ import annotations

import asyncio
<<<<<<< HEAD
from typing import Protocol

from app.core.events.base import BaseEvent
from app.core.events.registry import EventRegistry, event_registry
from app.core.logging.logger import get_logger

log = get_logger(__name__)


# ── Interface (Kafka-compatible protocol) ─────────────────────────────────────


class EventBusProtocol(Protocol):
    """Protocol that any event bus implementation must satisfy.

    Kafka adapter, in-process bus, and test mock all implement this.
    Services depend on this protocol, not on the concrete class.
    """

    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to all registered handlers.

        Args:
            event: The domain event to publish.
        """
        ...


# ── In-process implementation ─────────────────────────────────────────────────


class InProcessEventBus:
    """Async in-process event bus.

    Dispatches events synchronously within the same Python process.
    All handlers run concurrently via asyncio.gather() with error isolation.

    Args:
        registry: The EventRegistry that maps event types to handlers.
            Defaults to the module-level singleton.
    """

    def __init__(self, registry: EventRegistry | None = None) -> None:
        self._registry = registry or event_registry

    async def publish(self, event: BaseEvent) -> None:
        """Dispatch an event to all registered handlers concurrently.

        Handler errors are caught, logged, and isolated — a failing handler
        does not prevent other handlers from running or the caller from
        continuing.

        Args:
            event: The domain event to publish.
        """
        handlers = self._registry.get_handlers(event.event_type)

        if not handlers:
            log.debug(
                "event_published_no_handlers",
                event_type=event.event_type,
                event_id=str(event.event_id),
            )
            return

        log.debug(
            "event_dispatching",
            event_type=event.event_type,
            event_id=str(event.event_id),
            handler_count=len(handlers),
        )

        # Build coroutines with individual error wrapping
        async def _safe_call(handler, evt: BaseEvent) -> None:
            try:
                await handler(evt)
            except Exception as exc:
                log.error(
                    "event_handler_failed",
                    event_type=evt.event_type,
                    event_id=str(evt.event_id),
                    handler=handler.__qualname__,
                    error=str(exc),
                    exc_info=True,
                )
                # Do NOT re-raise — handler failure must not break the publisher

        await asyncio.gather(
            *(_safe_call(h, event) for h in handlers),
            return_exceptions=False,
        )

        log.info(
            "event_published",
            event_type=event.event_type,
            event_id=str(event.event_id),
            hospital_id=str(event.hospital_id),
            aggregate_id=str(event.aggregate_id),
        )


# ── Module-level singleton ────────────────────────────────────────────────────

_bus: InProcessEventBus | None = None


def init_event_bus(registry: EventRegistry | None = None) -> None:
    """Create the module-level event bus singleton.

    Called once in main.py lifespan startup — after all handlers have been
    registered with event_registry.subscribe().

    Args:
        registry: Optional custom registry. Defaults to the module singleton.
    """
    global _bus
    _bus = InProcessEventBus(registry=registry)
    log.info("event_bus_initialized", bus_type="in-process")


def get_event_bus() -> InProcessEventBus:
    """Return the active event bus.

    Used in FastAPI dependencies and service constructors.

    Raises:
        RuntimeError: If init_event_bus() has not been called.
    """
    if _bus is None:
        raise RuntimeError("Event bus is not initialised. Call init_event_bus() first.")
    return _bus


def override_event_bus(bus: InProcessEventBus) -> None:
    """Replace the module-level bus for testing.

    Args:
        bus: A test-scoped bus instance (e.g. MockEventBus or InProcessEventBus
            with a fresh EventRegistry).
    """
    global _bus
    _bus = bus
=======
import logging

from app.core.events.base import BaseEvent
from app.core.events.registry import registry

logger = logging.getLogger(__name__)

class EventBus:
    """In-process asynchronous event bus dispatcher."""
    
    @staticmethod
    async def publish(event: BaseEvent) -> None:
        """Publish an event to all registered subscribers.
        
        Args:
            event: The domain event to publish.
        """
        handlers = registry.get_handlers(event.event_type)
        if not handlers:
            logger.debug("No subscribers found for event: %s", event.event_type)
            return

        # Fire and forget handlers concurrently
        tasks = []
        for handler in handlers:
            tasks.append(asyncio.create_task(EventBus._safe_execute(handler, event)))
        
        # Wait for all handlers to complete. 
        # In a real Kafka setup, this would just be an ack to the broker.
        await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    async def _safe_execute(handler, event: BaseEvent) -> None:
        """Execute a handler safely, catching and logging any exceptions."""
        try:
            await handler(event)
        except Exception as e:
            logger.exception("Error executing handler %s for event %s: %s", 
                             handler.__name__, event.event_type, e)

# Global event bus instance
event_bus = EventBus()
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
