"""Feature store for the HRIP AI Engine.

Provides typed feature bundles consumed by all ML services.
In Phase 6 this is an in-process in-memory store.
In production it would be backed by Redis or a dedicated feature store (Feast).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ── Feature Bundle Dataclasses ────────────────────────────────────────────────


@dataclass
class HospitalFeatures:
    """Feature bundle for a single hospital snapshot."""

    hospital_id: str
    occupancy_rate: float = 0.0          # 0.0 – 1.0
    icu_occupancy_rate: float = 0.0
    available_beds: int = 0
    total_beds: int = 0
    stock_shortage_ratio: float = 0.0    # 0.0 – 1.0
    average_wait_time_min: float = 0.0
    staff_shortage_ratio: float = 0.0    # 0.0 – 1.0
    doctor_patient_ratio: float = 0.0
    monthly_patient_volume: list[float] = field(default_factory=list)
    monthly_medicine_consumption: dict[str, list[float]] = field(default_factory=dict)
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DistrictFeatures:
    """Feature bundle for a district-level disease surveillance snapshot."""

    district_id: str
    confirmed_cases: int = 0
    suspected_cases: int = 0
    new_cases_today: int = 0
    case_fatality_rate: float = 0.0
    severity_score: float = 0.0
    weather_risk: float = 0.0            # humidity + temperature index
    population: int = 100_000
    historical_case_counts: list[int] = field(default_factory=list)
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ── In-Memory Feature Store ───────────────────────────────────────────────────


class FeatureStore:
    """Simple in-memory feature store with typed get/set operations.

    In production this wraps Redis or Feast. The interface is identical.
    """

    def __init__(self) -> None:
        self._hospital_features: dict[str, HospitalFeatures] = {}
        self._district_features: dict[str, DistrictFeatures] = {}
        self._raw: dict[str, Any] = {}

    # ── Hospital Features ─────────────────────────────────────────────────────

    def set_hospital_features(self, features: HospitalFeatures) -> None:
        """Upsert hospital feature bundle."""
        self._hospital_features[features.hospital_id] = features

    def get_hospital_features(self, hospital_id: str) -> HospitalFeatures | None:
        """Retrieve hospital feature bundle. Returns None if not found."""
        return self._hospital_features.get(hospital_id)

    def get_or_create_hospital_features(self, hospital_id: str) -> HospitalFeatures:
        """Get existing or create default hospital feature bundle."""
        if hospital_id not in self._hospital_features:
            self._hospital_features[hospital_id] = HospitalFeatures(hospital_id=hospital_id)
        return self._hospital_features[hospital_id]

    # ── District Features ─────────────────────────────────────────────────────

    def set_district_features(self, features: DistrictFeatures) -> None:
        """Upsert district feature bundle."""
        self._district_features[features.district_id] = features

    def get_district_features(self, district_id: str) -> DistrictFeatures | None:
        """Retrieve district feature bundle. Returns None if not found."""
        return self._district_features.get(district_id)

    def get_or_create_district_features(self, district_id: str) -> DistrictFeatures:
        """Get existing or create default district feature bundle."""
        if district_id not in self._district_features:
            self._district_features[district_id] = DistrictFeatures(district_id=district_id)
        return self._district_features[district_id]

    # ── Generic raw store ─────────────────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        """Set an arbitrary key-value pair."""
        self._raw[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get an arbitrary value by key."""
        return self._raw.get(key, default)

    def all_hospital_ids(self) -> list[str]:
        """Return all hospital IDs currently in the store."""
        return list(self._hospital_features.keys())

    def stats(self) -> dict[str, int]:
        """Return store size statistics."""
        return {
            "hospitals": len(self._hospital_features),
            "districts": len(self._district_features),
            "raw_keys": len(self._raw),
        }


# ── Module-level singleton ────────────────────────────────────────────────────

_feature_store: FeatureStore | None = None


def get_feature_store() -> FeatureStore:
    """Return the singleton feature store instance.

    Initialized by the FastAPI lifespan on startup.
    """
    global _feature_store
    if _feature_store is None:
        _feature_store = FeatureStore()
    return _feature_store


def init_feature_store() -> FeatureStore:
    """Initialize (or reset) the singleton feature store. Called at startup."""
    global _feature_store
    _feature_store = FeatureStore()
    return _feature_store
