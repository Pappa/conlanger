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

# ASCA sound change rule validation

A fork of `asca-rust` is being used to validate sound change rules. To install it locally:

```bash
cargo install --git https://github.com/Pappa/asca-rust --branch feature/validate --root ./bin
```

And run it:

```bash
./bin/bin/asca validate --help
```