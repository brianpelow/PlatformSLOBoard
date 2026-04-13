"""Tests for SLO data models."""

from sloboard.models.slo import SLODefinition, ServiceReliability, PlatformSummary


def test_slo_is_healthy() -> None:
    slo = SLODefinition(name="test", service="svc", target=99.9,
        evaluated_percentage=99.95, error_budget_remaining=50.0,
        burn_rate=0.5, status="healthy")
    assert slo.is_healthy is True


def test_slo_is_not_healthy() -> None:
    slo = SLODefinition(name="test", service="svc", target=99.9,
        evaluated_percentage=99.5, error_budget_remaining=5.0,
        burn_rate=8.0, status="critical")
    assert slo.is_healthy is False


def test_slo_budget_consumed() -> None:
    slo = SLODefinition(name="test", service="svc",
        error_budget_remaining=30.0, status="healthy")
    assert slo.budget_consumed_pct == 70.0


def test_service_reliability_health_ratio_full() -> None:
    rel = ServiceReliability(service="svc", slo_count=4, healthy_slos=4)
    assert rel.health_ratio == 1.0


def test_service_reliability_health_ratio_partial() -> None:
    rel = ServiceReliability(service="svc", slo_count=4, healthy_slos=2)
    assert rel.health_ratio == 0.5


def test_platform_summary_defaults() -> None:
    summary = PlatformSummary()
    assert summary.overall_score == 0
    assert summary.total_slos == 0
    assert summary.active_incidents == 0