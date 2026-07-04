"""In-process Event Bus.

Handles asynchronous dispatching of domain events to registered subscribers.
Designed to be easily swapped with a Kafka-backed bus in the future.
"""
from __future__ import annotations

import asyncio
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
