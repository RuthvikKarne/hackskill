"""Structured logging configuration.

Uses structlog to provide JSON-formatted, context-aware logging.
"""
import logging
import sys
from typing import Any

import structlog

def setup_logging(json_logs: bool = False, log_level: int = logging.INFO) -> None:
    """Configure structlog globally.
    
    Args:
        json_logs: If True, logs will be formatted as JSON (for production).
                   Otherwise, formatted as colorized text (for development).
        log_level: Minimum logging level.
    """
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)

    processors: list[Any] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
