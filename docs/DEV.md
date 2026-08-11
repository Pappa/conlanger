# Local Development

Run Pytest via uv:

```bash
uv run pytest
```

Ruff:

```bash
uv run ruff check --fix
uv run ruff format && uv run ruff format --check src
```

Coverage threshold lives in `[tool.coverage.report] fail_under` in `pyproject.toml`; full `uv run pytest` enforces it.