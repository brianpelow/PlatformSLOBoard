# Contributing

## Development setup

```bash
git clone https://github.com/brianpelow/PlatformSLOBoard
cd PlatformSLOBoard
uv sync
uv run pytest
uv run platform-slo-board
```

## Standards

- All PRs require passing CI
- Test coverage must not decrease
- Update CHANGELOG.md for user-facing changes