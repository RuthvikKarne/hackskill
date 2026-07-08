"""Prometheus metrics instrumentation for the HRIP backend.

Uses prometheus-fastapi-instrumentator to expose:
  - HTTP request counts (by method, status, path)
  - HTTP request latency (histograms)
  - HTTP request size
  - HTTP response size
  - In-flight requests

Exposes /metrics endpoint (excluded from JWT auth middleware).
"""
from __future__ import annotations

from fastapi import FastAPI


def setup_metrics(app: FastAPI) -> None:
    """Instrument the FastAPI app with Prometheus metrics.

    Call this in create_app() before returning the app instance.
    This adds a GET /metrics endpoint that Prometheus scrapes.

    Args:
        app: The FastAPI application instance.
    """
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=[
                "/health",
                "/ready",
                "/metrics",
                "/api/docs",
                "/api/redoc",
                "/openapi.json",
            ],
            inprogress_name="hrip_backend_requests_inprogress",
            inprogress_labels=True,
        )

        instrumentator.instrument(app).expose(
            app,
            include_in_schema=False,
            endpoint="/metrics",
            tags=["Observability"],
        )

    except ImportError:
        # prometheus-fastapi-instrumentator not installed — skip silently
        # Add `prometheus-fastapi-instrumentator` to requirements.txt to enable
        import logging
        logging.getLogger(__name__).warning(
            "prometheus-fastapi-instrumentator not installed — metrics endpoint disabled. "
            "Run: pip install prometheus-fastapi-instrumentator"
        )
