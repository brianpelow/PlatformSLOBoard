"""PagerDuty incident collector for SLO correlation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import httpx


@dataclass
class IncidentSummary:
    """Summary of a PagerDuty incident."""

    id: str
    title: str
    service: str
    status: str
    severity: str
    created_at: str
    resolved_at: str = ""

    @property
    def is_resolved(self) -> bool:
        return self.status == "resolved"

    @property
    def duration_hours(self) -> float:
        if not self.resolved_at or not self.created_at:
            return 0.0
        try:
            from datetime import datetime
            fmt = "%Y-%m-%dT%H:%M:%SZ"
            created = datetime.strptime(self.created_at, fmt)
            resolved = datetime.strptime(self.resolved_at, fmt)
            return round((resolved - created).total_seconds() / 3600, 2)
        except Exception:
            return 0.0


class PagerDutyCollector:
    """Collects incident data from PagerDuty."""

    BASE_URL = "https://api.pagerduty.com"

    def __init__(self, token: str, timeout: int = 30) -> None:
        self.token = token
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Token token={self.token}",
            "Accept": "application/vnd.pagerduty+json;version=2",
        }

    def get_incidents(self, lookback_days: int = 30) -> list[IncidentSummary]:
        """Fetch recent incidents."""
        if not self.token:
            return _mock_incidents()
        try:
            from datetime import datetime, timedelta, timezone
            since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.BASE_URL}/incidents",
                    headers=self._headers(),
                    params={"since": since, "limit": 50, "statuses[]": ["triggered", "acknowledged", "resolved"]},
                )
                response.raise_for_status()
                return [_parse_incident(i) for i in response.json().get("incidents", [])]
        except Exception:
            return _mock_incidents()

    def get_active_count(self) -> int:
        """Get count of currently active incidents."""
        incidents = self.get_incidents(lookback_days=1)
        return sum(1 for i in incidents if not i.is_resolved)


def _parse_incident(data: dict[str, Any]) -> IncidentSummary:
    return IncidentSummary(
        id=data.get("id", ""),
        title=data.get("title", ""),
        service=data.get("service", {}).get("summary", ""),
        status=data.get("status", ""),
        severity=data.get("severity", "unknown"),
        created_at=data.get("created_at", ""),
        resolved_at=data.get("resolved_at") or "",
    )


def _mock_incidents() -> list[IncidentSummary]:
    return [
        IncidentSummary(id="INC001", title="Auth service latency spike",
            service="auth-service", status="resolved", severity="high",
            created_at="2026-04-10T14:00:00Z", resolved_at="2026-04-10T15:45:00Z"),
        IncidentSummary(id="INC002", title="FX rate feed degraded",
            service="fx-rate-service", status="resolved", severity="medium",
            created_at="2026-04-09T08:00:00Z", resolved_at="2026-04-09T09:30:00Z"),
        IncidentSummary(id="INC003", title="Payment processing slow",
            service="payments-service", status="triggered", severity="high",
            created_at="2026-04-12T01:00:00Z", resolved_at=""),
    ]