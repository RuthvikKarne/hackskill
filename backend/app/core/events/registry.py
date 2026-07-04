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
