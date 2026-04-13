"""Nightly agent — automated maintenance for PlatformSLOBoard."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

REPO_ROOT = Path(__file__).parent.parent


def snapshot_slo_status() -> None:
    """Compute and save current mock SLO status snapshot."""
    from sloboard.collectors.dynatrace import _mock_slos
    from sloboard.core.engine import compute_platform_summary
    slos = _mock_slos()
    summary = compute_platform_summary(slos, active_incidents=1, industry="fintech")
    snapshot = {
        "generated_at": datetime.utcnow().isoformat(),
        "date": date.today().isoformat(),
        "overall_score": summary.overall_score,
        "total_slos": summary.total_slos,
        "healthy": summary.healthy,
        "warning": summary.warning,
        "critical": summary.critical,
        "breached": summary.breached,
        "slos": [s.model_dump() for s in slos],
    }
    out = REPO_ROOT / "docs" / "slo-snapshot.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2))
    print(f"[agent] SLO snapshot saved — score: {summary.overall_score}/100 -> {out}")


def refresh_changelog() -> None:
    changelog = REPO_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return
    today = date.today().isoformat()
    content = changelog.read_text()
    if today not in content:
        content = content.replace("## [Unreleased]", f"## [Unreleased]\n\n_Last checked: {today}_", 1)
        changelog.write_text(content)
    print("[agent] Refreshed CHANGELOG timestamp")


if __name__ == "__main__":
    print(f"[agent] Starting nightly agent - {date.today().isoformat()}")
    snapshot_slo_status()
    refresh_changelog()
    print("[agent] Done.")