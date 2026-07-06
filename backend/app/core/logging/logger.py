"""Structured logging configuration for HRIP backend.

Uses structlog with two output modes:
- Development: human-readable coloured console output
- Production: JSON lines consumed by log aggregators (Loki, CloudWatch, etc.)

Usage:
    from app.core.logging.logger import get_logger

    log = get_logger(__name__)
    log.info("patient_registered", patient_id=str(patient.id), hospital_id=str(hospital_id))

Request-scoped context (request_id, hospital_id, actor_id) is bound once in
RequestIDMiddleware and automatically appears on every subsequent log call
within that request, courtesy of structlog's AsyncLocalStorage context.
"""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger


# ── Custom processors ─────────────────────────────────────────────────────────


def _drop_color_message_key(
    _logger: WrappedLogger, _method: str, event_dict: EventDict
) -> EventDict:
    """Remove the uvicorn 'color_message' key before JSON serialisation."""
    event_dict.pop("color_message", None)
    return event_dict


def _add_log_level(
    _logger: WrappedLogger, method: str, event_dict: EventDict
) -> EventDict:
    """Normalise log level name in the event dict."""
    event_dict.setdefault("level", method.upper())
    return event_dict


# ── Setup ─────────────────────────────────────────────────────────────────────


def configure_logging(
    *,
    json_logs: bool = False,
    log_level: str = "INFO",
) -> None:
    """Configure structlog and the stdlib logging bridge.

    Args:
        json_logs: If True, emit JSON lines (production). Otherwise emit
            coloured console output (development).
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    This function is idempotent — safe to call multiple times.
    """
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        _add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        _drop_color_message_key,
    ]

    if json_logs:
        # Production: JSON output — Loki/CloudWatch friendly
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        # Development: coloured console with aligned columns
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run on every stdlib log record redirected through structlog
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound to the given module name.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A structlog BoundLogger. Log calls automatically pick up any
        context variables bound via ``structlog.contextvars.bind_contextvars``.

    Example:
        log = get_logger(__name__)
        log.info("event_name", key="value")
    """
    return structlog.get_logger(name)


def bind_request_context(
    *,
    request_id: str,
    actor_id: str | None = None,
    hospital_id: str | None = None,
) -> None:
    """Bind request-scoped values to the structlog context.

    Called once per request in RequestIDMiddleware. All subsequent log
    calls within the same async context will carry these fields.

    Args:
        request_id: UUID string generated per request.
        actor_id: UUID of the authenticated user (None for anonymous).
        hospital_id: UUID of the hospital from the JWT claims.
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        actor_id=actor_id or "anonymous",
        hospital_id=hospital_id or "none",
    )
