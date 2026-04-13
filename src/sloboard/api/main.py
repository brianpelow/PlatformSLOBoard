"""FastAPI application for PlatformSLOBoard."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from sloboard.core.config import SLOBoardConfig
from sloboard.core.engine import compute_service_reliability, compute_platform_summary, classify_slo_status
from sloboard.core.narrator import generate_reliability_narrative
from sloboard.collectors.dynatrace import DynatraceCollector
from sloboard.collectors.pagerduty import PagerDutyCollector
from sloboard.models.slo import SLODefinition, ServiceReliability, PlatformSummary

app = FastAPI(
    title="PlatformSLOBoard",
    description="Executive-grade SLO dashboard for regulated industries",
    version="0.1.0",
)

config = SLOBoardConfig.from_env()


class HealthResponse(BaseModel):
    status: str
    version: str
    industry: str


def _get_slos() -> list[SLODefinition]:
    collector = DynatraceCollector(
        base_url=config.dynatrace_url,
        token=config.dynatrace_token,
    )
    return collector.get_slos()


def _get_active_incidents() -> int:
    collector = PagerDutyCollector(token=config.pagerduty_token)
    return collector.get_active_count()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0", industry=config.industry)


@app.get("/slos")
def list_slos() -> dict:
    slos = _get_slos()
    return {
        "count": len(slos),
        "slos": [s.model_dump() for s in slos],
        "summary": {
            "healthy": sum(1 for s in slos if s.status == "healthy"),
            "warning": sum(1 for s in slos if s.status == "warning"),
            "critical": sum(1 for s in slos if s.status == "critical"),
            "breached": sum(1 for s in slos if s.status == "breached"),
        },
    }


@app.get("/slos/{name}")
def get_slo(name: str) -> dict:
    slos = _get_slos()
    slo = next((s for s in slos if s.name.lower().replace(" ", "-") == name.lower()), None)
    if not slo:
        raise HTTPException(status_code=404, detail=f"SLO not found: {name}")
    return slo.model_dump()


@app.get("/services")
def list_services() -> dict:
    slos = _get_slos()
    services = list({s.service for s in slos})
    results = []
    for service in sorted(services):
        reliability = compute_service_reliability(service, slos)
        results.append(reliability.model_dump())
    return {"count": len(results), "services": results}


@app.get("/services/{name}/reliability")
def get_service_reliability(name: str) -> ServiceReliability:
    slos = _get_slos()
    pd_collector = PagerDutyCollector(token=config.pagerduty_token)
    incidents = pd_collector.get_incidents(lookback_days=config.lookback_days)
    service_incidents = [i for i in incidents if name.lower() in i.service.lower()]
    mttr = sum(i.duration_hours for i in service_incidents if i.is_resolved)
    mttr_avg = mttr / max(len([i for i in service_incidents if i.is_resolved]), 1)
    return compute_service_reliability(name, slos, len(service_incidents), mttr_avg)


@app.get("/budget")
def get_error_budgets() -> dict:
    slos = _get_slos()
    return {
        "period_days": config.lookback_days,
        "budgets": [
            {
                "name": s.name,
                "service": s.service,
                "target": s.target,
                "evaluated": s.evaluated_percentage,
                "budget_remaining": s.error_budget_remaining,
                "budget_consumed": s.budget_consumed_pct,
                "burn_rate": s.burn_rate,
                "status": s.status,
            }
            for s in sorted(slos, key=lambda x: x.error_budget_remaining)
        ],
    }


@app.get("/summary")
def get_summary() -> dict:
    slos = _get_slos()
    active_incidents = _get_active_incidents()
    summary = compute_platform_summary(slos, active_incidents, config.industry, config.lookback_days)
    narrative = generate_reliability_narrative(summary, slos, config.industry)
    summary.narrative = narrative
    return summary.model_dump()


def run() -> None:
    import uvicorn
    uvicorn.run("sloboard.api.main:app", host=config.host, port=config.port, reload=False)


if __name__ == "__main__":
    run()