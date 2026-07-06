from app.services.disease_surveillance.service import DiseaseSurveillanceService
from app.services.risk_intelligence.service import RiskIntelligenceService


def test_disease_surveillance_service_scores_high_risk_outbreaks() -> None:
    service = DiseaseSurveillanceService()

    result = service.analyze_district_risk(
        district_id="district-1",
        confirmed_cases=120,
        suspected_cases=75,
        new_cases_today=28,
        severity_score=0.95,
        weather_risk=0.8,
        population=250000,
    )

    assert result["risk_level"] == "critical"
    assert result["risk_score"] >= 0.8
    assert result["recommendations"]
    assert "surge" in result["recommendations"][0].lower()


def test_risk_intelligence_service_flags_hospital_shortages() -> None:
    service = RiskIntelligenceService()

    result = service.assess_hospital_risk(
        hospital_id="hospital-1",
        occupancy_rate=0.93,
        stock_shortage_ratio=0.72,
        average_wait_time=75,
        staff_shortage_ratio=0.4,
        severity_score=0.85,
    )

    assert result["risk_level"] == "critical"
    assert result["risk_score"] >= 0.75
    assert result["recommendations"]
    assert any("bed" in item.lower() or "stock" in item.lower() for item in result["recommendations"])
