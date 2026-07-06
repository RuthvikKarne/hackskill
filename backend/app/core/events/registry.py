<<<<<<< HEAD
"""EventRegistry — maps event types to their async handler callables.

The registry is populated once at application startup. Handlers are
ordinary async functions with the signature:

    async def handle_patient_registered(event: PatientRegisteredEvent) -> None:
        ...

Registration (in main.py lifespan):

    from app.core.events.registry import event_registry
    from app.modules.audit.handlers import handle_patient_registered

    event_registry.subscribe("patients.patient.registered", handle_patient_registered)

The InProcessEventBus queries the registry on every publish() call.

Thread safety:
    Registration is done once at startup before any requests are served,
    so there are no concurrent write races. Reads (dispatch) are inherently
    safe with Python dicts.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

from app.core.logging.logger import get_logger

log = get_logger(__name__)

# Handler type: async function that receives any event and returns None
EventHandler = Callable[..., Coroutine[Any, Any, None]]


class EventRegistry:
    """Registry mapping event_type strings to lists of async handlers.

    Each event type can have multiple subscribers. Handlers are invoked
    in registration order (though concurrently — see InProcessEventBus).

    Attributes:
        _handlers: Internal mapping of event_type → [handler, ...].
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register an async handler for a given event type.

        Args:
            event_type: Dot-namespaced event type string (e.g. "patients.patient.registered").
                Use "*" to subscribe to ALL events (for audit/logging handlers).
            handler: Async callable that processes the event.

        Example:
            event_registry.subscribe(
                "inventory.medicine.stock_critical_low",
                notify_pharmacist_handler,
            )
        """
        self._handlers[event_type].append(handler)
        log.debug(
            "event_handler_registered",
            event_type=event_type,
            handler=handler.__qualname__,
        )

    def get_handlers(self, event_type: str) -> list[EventHandler]:
        """Return all handlers registered for a given event type.

        Includes both event-type-specific handlers AND wildcard ("*") handlers.

        Args:
            event_type: The event type string from a published event.

        Returns:
            List of async handler callables. Empty list if none registered.
        """
        specific = list(self._handlers.get(event_type, []))
        wildcard = list(self._handlers.get("*", []))
        return specific + wildcard

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a specific handler from an event type.

        Primarily useful in tests to reset state between test cases.

        Args:
            event_type: The event type the handler was registered for.
            handler: The handler callable to remove.
        """
        handlers = self._handlers.get(event_type, [])
        try:
            handlers.remove(handler)
        except ValueError:
            pass  # Handler was not registered; ignore silently

    def clear(self) -> None:
        """Remove all registered handlers. Used in tests."""
        self._handlers.clear()

    @property
    def registered_event_types(self) -> list[str]:
        """Return a sorted list of all registered event type strings."""
        return sorted(self._handlers.keys())

    def __repr__(self) -> str:
        counts = {k: len(v) for k, v in self._handlers.items()}
        return f"EventRegistry({counts})"


# ── Module-level singleton ────────────────────────────────────────────────────

# All modules import this singleton to register / query handlers.
# Tests can call event_registry.clear() in fixtures to reset state.
event_registry = EventRegistry()
=======
"""Event subscriber registry.

Provides decorators and a registry to map event types to their handler functions.
"""
from __future__ import annotations

import collections
from typing import Awaitable, Callable

from app.core.events.base import BaseEvent

# Type alias for event handlers
EventHandler = Callable[[BaseEvent], Awaitable[None]]

class EventRegistry:
    """Registry to hold mappings from event types to their handlers."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = collections.defaultdict(list)

    def subscribe(self, event_type: str) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register a function as a handler for a specific event type.
        
        Usage:
            @registry.subscribe("inventory.stock.critical_low")
            async def handle_low_stock(event: BaseEvent) -> None:
                ...
        """
        def decorator(handler: EventHandler) -> EventHandler:
            self._subscribers[event_type].append(handler)
            return handler
        return decorator

    def get_handlers(self, event_type: str) -> list[EventHandler]:
        """Get all handlers registered for an event type."""
        return self._subscribers.get(event_type, [])

# Global registry instance
registry = EventRegistry()
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
