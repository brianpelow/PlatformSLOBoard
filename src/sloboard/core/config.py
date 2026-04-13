"""Configuration for PlatformSLOBoard."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field


class SLOBoardConfig(BaseModel):
    """Runtime configuration for PlatformSLOBoard."""

    dynatrace_url: str = Field("", description="Dynatrace environment URL")
    dynatrace_token: str = Field("", description="Dynatrace API token")
    pagerduty_token: str = Field("", description="PagerDuty API token")
    anthropic_api_key: str = Field("", description="Anthropic API key")
    industry: str = Field("fintech", description="Industry context")
    lookback_days: int = Field(30, description="Days of history to analyse")
    host: str = Field("0.0.0.0", description="API server host")
    port: int = Field(8000, description="API server port")

    @classmethod
    def from_env(cls) -> "SLOBoardConfig":
        return cls(
            dynatrace_url=os.environ.get("DYNATRACE_URL", ""),
            dynatrace_token=os.environ.get("DYNATRACE_TOKEN", ""),
            pagerduty_token=os.environ.get("PAGERDUTY_TOKEN", ""),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            industry=os.environ.get("SLO_INDUSTRY", "fintech"),
        )

    @property
    def has_dynatrace(self) -> bool:
        return bool(self.dynatrace_url and self.dynatrace_token)

    @property
    def has_pagerduty(self) -> bool:
        return bool(self.pagerduty_token)