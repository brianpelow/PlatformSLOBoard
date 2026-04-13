# PlatformSLOBoard

> Executive-grade platform SLO dashboard aggregating PagerDuty and Dynatrace reliability signals.

![CI](https://github.com/brianpelow/PlatformSLOBoard/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)

## Overview

`PlatformSLOBoard` is a FastAPI service that aggregates SLO data from Dynatrace
and incident data from PagerDuty into a single executive-grade reliability
dashboard. It computes error budget burn rates, classifies SLO health status,
and generates AI-powered reliability narratives for leadership reporting.

Built for platform and SRE teams in regulated financial services and
manufacturing where SLO compliance is a contractual and regulatory obligation.

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Service health check |
| `GET /slos` | All SLOs with current status and burn rates |
| `GET /slos/{name}` | Detailed SLO status with incident correlation |
| `GET /services` | Service reliability overview |
| `GET /services/{name}/reliability` | Per-service reliability score |
| `GET /summary` | Executive reliability summary with AI narrative |
| `GET /budget` | Error budget consumption across all SLOs |

## Quick start

```bash
pip install PlatformSLOBoard

export DYNATRACE_URL=https://your-env.live.dynatrace.com
export DYNATRACE_TOKEN=your_token
export PAGERDUTY_TOKEN=your_token

platform-slo-board
# API available at http://localhost:8000
```

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `DYNATRACE_URL` | Dynatrace environment URL | No |
| `DYNATRACE_TOKEN` | Dynatrace API token | No |
| `PAGERDUTY_TOKEN` | PagerDuty API token | No |
| `ANTHROPIC_API_KEY` | For AI narratives | No |
| `SLO_INDUSTRY` | Industry context | No |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).