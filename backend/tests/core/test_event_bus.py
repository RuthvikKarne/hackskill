"""Unit tests for the in-process Event Bus.

Tests cover:
    - Handler registration via EventRegistry
    - Event dispatch to all registered handlers
    - Error isolation (one handler failing doesn't block others)
    - Wildcard ("*") subscription
    - Concurrent dispatch (asyncio.gather)
    - Mock event bus assertion pattern
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.events.base import BaseEvent
from app.core.events.bus import InProcessEventBus
from app.core.events.registry import EventRegistry


# ── Test event fixtures ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class TestPatientRegisteredEvent(BaseEvent):
    """Minimal test event."""

    patient_name: str = ""

    @property
    def event_type(self) -> str:
        return "test.patient.registered"


@dataclass(frozen=True)
class TestInventoryEvent(BaseEvent):
    """Second test event type for multi-subscription tests."""

    @property
    def event_type(self) -> str:
        return "test.inventory.updated"


def make_event(**kwargs) -> TestPatientRegisteredEvent:
    """Build a test event with sensible defaults."""
    return TestPatientRegisteredEvent(
        aggregate_id=kwargs.get("aggregate_id", uuid4()),
        hospital_id=kwargs.get("hospital_id", uuid4()),
        actor_id=kwargs.get("actor_id", uuid4()),
        patient_name=kwargs.get("patient_name", "Test Patient"),
    )


# ── EventRegistry tests ───────────────────────────────────────────────────────


class TestEventRegistry:
    def test_subscribe_registers_handler(self):
        registry = EventRegistry()
        handler = AsyncMock()
        registry.subscribe("test.event", handler)
        assert handler in registry.get_handlers("test.event")

    def test_multiple_handlers_per_event_type(self):
        registry = EventRegistry()
        h1, h2 = AsyncMock(), AsyncMock()
        registry.subscribe("test.event", h1)
        registry.subscribe("test.event", h2)
        handlers = registry.get_handlers("test.event")
        assert h1 in handlers
        assert h2 in handlers
        assert len(handlers) == 2

    def test_wildcard_handler_included_in_all(self):
        registry = EventRegistry()
        wildcard = AsyncMock()
        specific = AsyncMock()
        registry.subscribe("*", wildcard)
        registry.subscribe("test.event", specific)
        handlers = registry.get_handlers("test.event")
        assert wildcard in handlers
        assert specific in handlers

    def test_wildcard_only_returns_wildcard(self):
        registry = EventRegistry()
        wildcard = AsyncMock()
        registry.subscribe("*", wildcard)
        handlers = registry.get_handlers("some.other.event")
        assert wildcard in handlers

    def test_unknown_event_type_returns_empty(self):
        registry = EventRegistry()
        assert registry.get_handlers("nonexistent.event") == []

    def test_unsubscribe_removes_handler(self):
        registry = EventRegistry()
        handler = AsyncMock()
        registry.subscribe("test.event", handler)
        registry.unsubscribe("test.event", handler)
        assert handler not in registry.get_handlers("test.event")

    def test_unsubscribe_nonexistent_is_noop(self):
        registry = EventRegistry()
        handler = AsyncMock()
        # Should not raise
        registry.unsubscribe("test.event", handler)

    def test_clear_removes_all_handlers(self):
        registry = EventRegistry()
        registry.subscribe("a.event", AsyncMock())
        registry.subscribe("b.event", AsyncMock())
        registry.clear()
        assert registry.get_handlers("a.event") == []
        assert registry.get_handlers("b.event") == []

    def test_registered_event_types_sorted(self):
        registry = EventRegistry()
        registry.subscribe("z.event", AsyncMock())
        registry.subscribe("a.event", AsyncMock())
        assert registry.registered_event_types == ["a.event", "z.event"]


# ── InProcessEventBus tests ───────────────────────────────────────────────────


class TestInProcessEventBus:
    @pytest.mark.asyncio
    async def test_publish_calls_registered_handler(self):
        registry = EventRegistry()
        handler = AsyncMock()
        registry.subscribe("test.patient.registered", handler)
        bus = InProcessEventBus(registry=registry)

        event = make_event()
        await bus.publish(event)

        handler.assert_awaited_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_calls_all_handlers(self):
        registry = EventRegistry()
        h1, h2, h3 = AsyncMock(), AsyncMock(), AsyncMock()
        for h in (h1, h2, h3):
            registry.subscribe("test.patient.registered", h)
        bus = InProcessEventBus(registry=registry)

        event = make_event()
        await bus.publish(event)

        for h in (h1, h2, h3):
            h.assert_awaited_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_no_handlers_does_not_raise(self):
        registry = EventRegistry()
        bus = InProcessEventBus(registry=registry)
        event = make_event()
        # Should not raise even with no handlers
        await bus.publish(event)

    @pytest.mark.asyncio
    async def test_handler_error_does_not_block_other_handlers(self):
        """A failing handler must not stop other handlers from running."""
        registry = EventRegistry()
        failing_handler = AsyncMock(side_effect=RuntimeError("handler crash"))
        good_handler = AsyncMock()
        registry.subscribe("test.patient.registered", failing_handler)
        registry.subscribe("test.patient.registered", good_handler)

        bus = InProcessEventBus(registry=registry)
        event = make_event()

        # Should not raise even though one handler fails
        await bus.publish(event)

        # Good handler must still have been called
        good_handler.assert_awaited_once_with(event)

    @pytest.mark.asyncio
    async def test_wildcard_handler_receives_all_events(self):
        registry = EventRegistry()
        wildcard = AsyncMock()
        registry.subscribe("*", wildcard)
        bus = InProcessEventBus(registry=registry)

        e1 = make_event()
        e2 = TestInventoryEvent(aggregate_id=uuid4(), hospital_id=uuid4(), actor_id=uuid4())

        await bus.publish(e1)
        await bus.publish(e2)

        assert wildcard.await_count == 2

    @pytest.mark.asyncio
    async def test_handlers_run_concurrently(self):
        """Verify asyncio.gather is used (handlers start without waiting for each other)."""
        start_times = []

        async def slow_handler(event):
            start_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.01)

        registry = EventRegistry()
        for _ in range(3):
            registry.subscribe("test.patient.registered", slow_handler)

        bus = InProcessEventBus(registry=registry)
        event = make_event()

        t_start = asyncio.get_event_loop().time()
        await bus.publish(event)
        t_end = asyncio.get_event_loop().time()

        # 3 handlers * 10ms each — if sequential: ~30ms; if concurrent: ~10ms
        assert (t_end - t_start) < 0.025, "Handlers should run concurrently"

    @pytest.mark.asyncio
    async def test_publish_uses_mock_bus_in_fixture(self, mock_event_bus):
        """Test the conftest mock_event_bus fixture pattern."""
        event = make_event()
        await mock_event_bus.publish(event)
        mock_event_bus.publish.assert_awaited_once_with(event)
