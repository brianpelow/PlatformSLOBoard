"""Tests for Dynatrace and PagerDuty collectors."""

from sloboard.collectors.dynatrace import DynatraceCollector, _mock_slos
from sloboard.collectors.pagerduty import PagerDutyCollector, _mock_incidents


def test_dynatrace_returns_mock_when_no_token() -> None:
    collector = DynatraceCollector(base_url="", token="")
    slos = collector.get_slos()
    assert len(slos) > 0


def test_mock_slos_have_valid_status() -> None:
    slos = _mock_slos()
    for slo in slos:
        assert slo.status in ("healthy", "warning", "critical", "breached")


def test_mock_slos_have_required_fields() -> None:
    slos = _mock_slos()
    for slo in slos:
        assert slo.name
        assert slo.service
        assert slo.target > 0


def test_pagerduty_returns_mock_when_no_token() -> None:
    collector = PagerDutyCollector(token="")
    incidents = collector.get_incidents()
    assert len(incidents) > 0


def test_mock_incidents_have_required_fields() -> None:
    incidents = _mock_incidents()
    for i in incidents:
        assert i.id
        assert i.title
        assert i.service


def test_incident_duration_resolved() -> None:
    incidents = _mock_incidents()
    resolved = [i for i in incidents if i.is_resolved]
    assert len(resolved) > 0
    for i in resolved:
        assert i.duration_hours > 0


def test_pagerduty_active_count() -> None:
    collector = PagerDutyCollector(token="")
    count = collector.get_active_count()
    assert isinstance(count, int)
    assert count >= 0