"""SLO aggregation and scoring engine."""

from __future__ import annotations

from sloboard.models.slo import SLODefinition, ServiceReliability, PlatformSummary


STATUS_SCORES = {"healthy": 100, "warning": 70, "critical": 40, "breached": 0}


def compute_service_reliability(
    service: str,
    slos: list[SLODefinition],
    incident_count: int = 0,
    mttr_hours: float = 0.0,
) -> ServiceReliability:
    """Compute reliability score for a single service."""
    service_slos = [s for s in slos if s.service == service]

    if not service_slos:
        return ServiceReliability(service=service, slo_count=0, reliability_score=50)

    healthy = sum(1 for s in service_slos if s.status == "healthy")
    warning = sum(1 for s in service_slos if s.status == "warning")
    critical = sum(1 for s in service_slos if s.status == "critical")
    breached = sum(1 for s in service_slos if s.status == "breached")

    slo_score = int(sum(STATUS_SCORES.get(s.status, 50) for s in service_slos) / len(service_slos))

    incident_penalty = min(30, incident_count * 5)
    mttr_penalty = 0
    if mttr_hours > 4:
        mttr_penalty = 10
    elif mttr_hours > 1:
        mttr_penalty = 5

    reliability_score = max(0, slo_score - incident_penalty - mttr_penalty)

    return ServiceReliability(
        service=service,
        reliability_score=reliability_score,
        slo_count=len(service_slos),
        healthy_slos=healthy,
        warning_slos=warning,
        critical_slos=critical,
        breached_slos=breached,
        incident_count=incident_count,
        mttr_hours=mttr_hours,
    )


def compute_platform_summary(
    slos: list[SLODefinition],
    active_incidents: int = 0,
    industry: str = "fintech",
    period_days: int = 30,
) -> PlatformSummary:
    """Compute executive platform reliability summary."""
    if not slos:
        return PlatformSummary(industry=industry, period_days=period_days)

    healthy = sum(1 for s in slos if s.status == "healthy")
    warning = sum(1 for s in slos if s.status == "warning")
    critical = sum(1 for s in slos if s.status == "critical")
    breached = sum(1 for s in slos if s.status == "breached")

    base_score = int(sum(STATUS_SCORES.get(s.status, 50) for s in slos) / len(slos))
    incident_penalty = min(20, active_incidents * 5)
    overall_score = max(0, base_score - incident_penalty)

    return PlatformSummary(
        total_slos=len(slos),
        healthy=healthy,
        warning=warning,
        critical=critical,
        breached=breached,
        overall_score=overall_score,
        active_incidents=active_incidents,
        period_days=period_days,
        industry=industry,
    )


def classify_slo_status(
    evaluated_pct: float,
    target: float,
    budget_remaining: float,
    burn_rate: float,
) -> str:
    """Classify SLO health status from raw metrics."""
    if evaluated_pct < target * 0.99:
        return "breached"
    elif burn_rate >= 10 or budget_remaining <= 2:
        return "critical"
    elif burn_rate >= 2 or budget_remaining <= 20:
        return "warning"
    return "healthy"