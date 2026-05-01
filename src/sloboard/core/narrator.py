"""AI-powered reliability narrative generation."""

from __future__ import annotations

import os
from sloboard.models.slo import PlatformSummary, SLODefinition


def generate_reliability_narrative(
    summary: PlatformSummary,
    slos: list[SLODefinition],
    industry: str = "fintech",
) -> str:
    """Generate an executive reliability narrative using Claude."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_narrative(summary, slos, industry)

    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        breached = [s for s in slos if s.status == "breached"]
        critical = [s for s in slos if s.status == "critical"]
        at_risk = breached + critical

        at_risk_text = "\n".join(
            f"- {s.name} ({s.service}): {s.evaluated_percentage:.2f}% vs {s.target}% target, burn rate {s.burn_rate:.1f}x"
            for s in at_risk[:5]
        ) or "None"

        prompt = f"""You are a platform engineering director writing a weekly reliability briefing for {industry} executive leadership.

Platform reliability score: {summary.overall_score}/100
SLOs tracked: {summary.total_slos}
Healthy: {summary.healthy} | Warning: {summary.warning} | Critical: {summary.critical} | Breached: {summary.breached}
Active incidents: {summary.active_incidents}
Period: last {summary.period_days} days

SLOs at risk:
{at_risk_text}

Write a 3-paragraph executive briefing that:
1. States the overall platform reliability posture and headline number
2. Calls out the most critical SLO risks with specific data and business impact
3. Recommends immediate actions and sets expectations for the next period

Use language appropriate for a CTO or CFO audience in a regulated {industry} environment.
Be specific, concise, and action-oriented. Reference compliance implications where relevant."""

        message = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.choices[0].message.content

    except Exception:
        return _fallback_narrative(summary, slos, industry)


def _fallback_narrative(
    summary: PlatformSummary,
    slos: list[SLODefinition],
    industry: str,
) -> str:
    status = "strong" if summary.overall_score >= 80 else "moderate" if summary.overall_score >= 60 else "at risk"
    breached = [s for s in slos if s.status == "breached"]
    critical = [s for s in slos if s.status == "critical"]

    return f"""## Platform Reliability Briefing

**Overall platform reliability is {status}** with a score of {summary.overall_score}/100.
Of {summary.total_slos} tracked SLOs, {summary.healthy} are healthy, {summary.warning} are in warning,
{summary.critical} are critical, and {summary.breached} have breached their targets.
There are currently {summary.active_incidents} active incidents.

{"**Immediate attention required**: " + ", ".join(s.name for s in breached) + " have breached SLO targets. This requires immediate engineering response and may trigger contractual notification obligations." if breached else "No SLOs are currently breached."}
{"**At risk**: " + ", ".join(s.name for s in critical) + " are burning error budget at elevated rates." if critical else ""}

**Recommended actions**: {"Engage incident response for breached SLOs immediately. " if breached else ""}
Review error budget burn rates for warning-status SLOs and ensure runbooks are current.
All SLO breaches in {industry} environments must be documented per compliance requirements.
"""