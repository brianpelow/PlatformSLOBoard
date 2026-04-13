"""Dynatrace SLO collector."""

from __future__ import annotations

from typing import Any
import httpx
from sloboard.models.slo import SLODefinition


class DynatraceCollector:
    """Collects SLO data from Dynatrace API v2."""

    def __init__(self, base_url: str, token: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Api-Token {self.token}", "Content-Type": "application/json"}

    def get_slos(self) -> list[SLODefinition]:
        """Fetch all SLOs from Dynatrace."""
        if not self.token:
            return _mock_slos()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v2/slo",
                    headers=self._headers(),
                    params={"pageSize": 50},
                )
                response.raise_for_status()
                data = response.json()
                return [_parse_slo(s) for s in data.get("slo", [])]
        except Exception:
            return _mock_slos()

    def get_slo_by_name(self, name: str) -> SLODefinition | None:
        """Fetch a specific SLO by name."""
        slos = self.get_slos()
        return next((s for s in slos if s.name.lower() == name.lower()), None)


def _parse_slo(data: dict[str, Any]) -> SLODefinition:
    evaluated = float(data.get("evaluatedPercentage", 0))
    target = float(data.get("target", 99.9))
    budget = float(data.get("errorBudgetRemaining", 0))
    burn = float(data.get("burnRateValue", 0))

    if evaluated >= target and budget > 20:
        status = "healthy"
    elif evaluated >= target and budget > 5:
        status = "warning"
    elif evaluated >= target * 0.99:
        status = "critical"
    else:
        status = "breached"

    return SLODefinition(
        name=data.get("name", ""),
        service=data.get("filter", "").split("entityId(")[1].rstrip(")") if "entityId(" in data.get("filter", "") else "unknown",
        target=target,
        evaluated_percentage=round(evaluated, 4),
        error_budget_remaining=round(budget, 2),
        burn_rate=round(burn, 2),
        status=status,
    )


def _mock_slos() -> list[SLODefinition]:
    return [
        SLODefinition(name="Payments API Availability", service="payments-service",
            target=99.9, evaluated_percentage=99.94, error_budget_remaining=42.0,
            burn_rate=0.8, status="healthy"),
        SLODefinition(name="Payments API Latency P99", service="payments-service",
            target=99.5, evaluated_percentage=99.51, error_budget_remaining=18.0,
            burn_rate=2.1, status="warning"),
        SLODefinition(name="FX Rate Service Availability", service="fx-rate-service",
            target=99.9, evaluated_percentage=99.71, error_budget_remaining=8.0,
            burn_rate=3.8, status="critical"),
        SLODefinition(name="Trading Engine Throughput", service="trading-engine",
            target=99.0, evaluated_percentage=99.12, error_budget_remaining=55.0,
            burn_rate=0.5, status="healthy"),
        SLODefinition(name="Audit Service Availability", service="audit-service",
            target=99.99, evaluated_percentage=99.98, error_budget_remaining=25.0,
            burn_rate=1.2, status="healthy"),
        SLODefinition(name="Auth Service Latency P95", service="auth-service",
            target=99.5, evaluated_percentage=98.90, error_budget_remaining=0.0,
            burn_rate=12.5, status="breached"),
    ]