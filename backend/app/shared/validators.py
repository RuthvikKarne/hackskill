"""Shared Pydantic validators and base models for HRIP.

Provides reusable validators that every module schema can inherit from or
reference instead of duplicating validation logic.

Usage in a module schema:

    from app.shared.validators import HospitalScopedModel, validate_phone_number

    class PatientCreateRequest(HospitalScopedModel):
        full_name: str
        phone: str

        @field_validator("phone")
        @classmethod
        def check_phone(cls, v: str) -> str:
            return validate_phone_number(v)
"""
from __future__ import annotations

import re
from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


# ── Base model config ─────────────────────────────────────────────────────────


class HRIPBaseModel(BaseModel):
    """Base Pydantic model with strict config applied to all HRIP schemas.

    Settings:
        populate_by_name: Allows both alias and field name in input.
        str_strip_whitespace: Strips leading/trailing whitespace on all str fields.
        validate_assignment: Re-validates when a field is reassigned.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class HospitalScopedModel(HRIPBaseModel):
    """Base model for requests that carry hospital context.

    The hospital_id is typically injected from the JWT claims in the
    service layer, NOT from the request body. This model is used internally
    by services to pass validated, hospital-scoped data to repositories.

    Attributes:
        hospital_id: The UUID of the hospital this record belongs to.
    """

    hospital_id: UUID


# ── Field validators ──────────────────────────────────────────────────────────

# E.164 format: + followed by 7–15 digits
_PHONE_REGEX = re.compile(r"^\+?[1-9]\d{6,14}$")


def validate_phone_number(value: str) -> str:
    """Validate and normalise a phone number string.

    Accepts E.164 format: +<country_code><number>, 7–15 digits.

    Args:
        value: Raw phone number string.

    Returns:
        Cleaned phone number (whitespace removed).

    Raises:
        ValueError: If the phone number does not match E.164 format.
    """
    cleaned = re.sub(r"\s+", "", value)
    if not _PHONE_REGEX.match(cleaned):
        raise ValueError(
            "Phone number must be in E.164 format (e.g. +2347012345678)."
        )
    return cleaned


def validate_date_range(start: date, end: date) -> None:
    """Validate that a date range is logically consistent.

    Args:
        start: Start date.
        end:   End date.

    Raises:
        ValueError: If start is after end, or if the range exceeds 1 year.
    """
    if start > end:
        raise ValueError("Start date must be before or equal to end date.")
    if (end - start).days > 365:
        raise ValueError("Date range cannot exceed 1 year.")


def validate_uuid_list(values: list[str]) -> list[UUID]:
    """Validate a list of UUID strings and convert to UUID objects.

    Args:
        values: List of UUID strings from request input.

    Returns:
        List of UUID objects.

    Raises:
        ValueError: If any string is not a valid UUID.
    """
    result: list[UUID] = []
    for i, v in enumerate(values):
        try:
            result.append(UUID(v))
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"Item at index {i} is not a valid UUID: '{v}'") from exc
    return result


# ── Commonly reused field definitions ─────────────────────────────────────────


def non_empty_string(field_name: str = "value") -> field_validator:  # type: ignore[valid-type]
    """Return a Pydantic field_validator that rejects empty strings.

    Args:
        field_name: Field name for use in the error message.

    Usage:
        class MySchema(HRIPBaseModel):
            name: str
            _name_not_empty = non_empty_string("name")
    """
    def _validate(cls, v: str) -> str:
        if not v.strip():
            raise ValueError(f"{field_name} must not be empty.")
        return v

    return field_validator(field_name)(_validate)
