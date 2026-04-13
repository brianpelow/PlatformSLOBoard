"""SLO data models."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class SLODefinition(BaseModel):
    """An SLO definition with target and current performance."""

    name: str
    service: str
    target: float = Field(99.9, description="SLO target percentage")
    evaluated_percentage: float = Field(0.0, description="Current performance")
    error_budget_remaining: float = Field(0.0, description="Remaining error budget percent")
    burn_rate: float = Field(0.0, description="Current burn rate multiplier")
    status: str = Field("healthy", description="healthy/warning/critical/breached")
    period_days: int = Field(30)

    @property
    def is_healthy(self) -> bool:
        return self.status == "healthy"

    @property
    def budget_consumed_pct(self) -> float:
        return round(100.0 - self.error_budget_remaining, 2)


class ServiceReliability(BaseModel):
    """Reliability summary for a single service."""

    service: str
    reliability_score: int = Field(0, description="0-100 reliability score")
    slo_count: int = Field(0)
    healthy_slos: int = Field(0)
    warning_slos: int = Field(0)
    critical_slos: int = Field(0)
    breached_slos: int = Field(0)
    incident_count: int = Field(0)
    mttr_hours: float = Field(0.0)

    @property
    def health_ratio(self) -> float:
        if self.slo_count == 0:
            return 1.0
        return self.healthy_slos / self.slo_count


class PlatformSummary(BaseModel):
    """Executive platform reliability summary."""

    total_slos: int = Field(0)
    healthy: int = Field(0)
    warning: int = Field(0)
    critical: int = Field(0)
    breached: int = Field(0)
    overall_score: int = Field(0, description="0-100 platform reliability score")
    active_incidents: int = Field(0)
    narrative: Optional[str] = None
    period_days: int = Field(30)
    industry: str = "fintech"