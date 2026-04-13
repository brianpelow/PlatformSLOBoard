"""Tests for SLOBoardConfig."""

from sloboard.core.config import SLOBoardConfig


def test_config_defaults() -> None:
    config = SLOBoardConfig()
    assert config.industry == "fintech"
    assert config.lookback_days == 30
    assert config.port == 8000
    assert config.dynatrace_url == ""


def test_config_custom() -> None:
    config = SLOBoardConfig(
        dynatrace_url="https://test.live.dynatrace.com",
        dynatrace_token="test-token",
        industry="manufacturing",
    )
    assert config.has_dynatrace is True
    assert config.industry == "manufacturing"


def test_has_dynatrace_false() -> None:
    config = SLOBoardConfig()
    assert config.has_dynatrace is False


def test_has_pagerduty_false() -> None:
    config = SLOBoardConfig()
    assert config.has_pagerduty is False


def test_has_pagerduty_true() -> None:
    config = SLOBoardConfig(pagerduty_token="test-token")
    assert config.has_pagerduty is True