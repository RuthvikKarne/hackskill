"""Shared pytest fixtures for the HRIP backend test suite.

This file provides:
  - Test database setup and teardown
  - Async test client (httpx + FastAPI)
  - Authenticated test user fixtures per role
  - Event bus mock fixture

TODO Phase 1: Implement fixtures as infrastructure is built.
"""
from __future__ import annotations

import pytest


# TODO Phase 1:
# @pytest.fixture(scope="session")
# async def test_db():
#     """Create a fresh test database for the session."""
#     ...
#
# @pytest.fixture
# async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
#     """Async HTTP test client."""
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac
