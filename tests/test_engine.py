"""Tests for SLO aggregation engine."""

from sloboard.core.engine import compute_service_reliability, compute_platform_summary, classify_slo_status
from sloboard.collectors.dynatrace import _mock_slos


def test_classify_slo_healthy() -> None:
    assert classify_slo_status(99.95, 99.9, 50.0, 0.5) == "healthy"


def test_classify_slo_warning() -> None:
    assert classify_slo_status(99.95, 99.9, 15.0, 2.5) == "warning"


def test_classify_slo_critical() -> None:
    assert classify_slo_status(99.95, 99.9, 1.0, 11.0) == "critical"


def test_classify_slo_breached() -> None:
    assert classify_slo_status(98.0, 99.9, 0.0, 15.0) == "breached"


def test_compute_service_reliability_no_slos() -> None:
    result = compute_service_reliability("unknown-service", [])
    assert result.reliability_score == 50
    assert result.slo_count == 0


def test_compute_service_reliability_with_slos() -> None:
    slos = _mock_slos()
    result = compute_service_reliability("payments-service", slos)
    assert result.slo_count > 0
    assert 0 <= result.reliability_score <= 100


def test_compute_platform_summary_empty() -> None:
    summary = compute_platform_summary([])
    assert summary.total_slos == 0
    assert summary.overall_score == 0


def test_compute_platform_summary_with_slos() -> None:
    slos = _mock_slos()
    summary = compute_platform_summary(slos, active_incidents=1)
    assert summary.total_slos == len(slos)
    assert 0 <= summary.overall_score <= 100
    assert summary.healthy + summary.warning + summary.critical + summary.breached == len(slos)