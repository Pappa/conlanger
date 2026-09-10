# Local Development

Run Pytest via uv:

```bash
uv run pytest
```

Ruff:

```bash
uv run ruff check --fix
uv run ruff format && uv run ruff format --check
```

Coverage threshold lives in `[tool.coverage.report] fail_under` in `pyproject.toml`; full `uv run pytest` enforces it.

# ASCA sound change rule validation

Conlanger validates compiled rules with a **private fork** of [asca-rust](https://github.com/Pappa/asca-rust) at **0.10.3**. That release adds the `validate` subcommand (whole-rule and per-field checks) used by `validate_asca` and the validation inventory.

Install the fork into this repo’s `bin/` tree:

```bash
cargo install --git https://github.com/Pappa/asca-rust --tag 0.10.3 --root ./bin
```

Verify:

```bash
export ASCA_BIN="$(pwd)/bin/bin/asca"
./bin/bin/asca --version   # asca 0.10.3
./bin/bin/asca validate --help
```

`uv run validate_rules` defaults to the repo-local binary at `bin/bin/asca` (`--use-asca-fork`, on by default). Set `ASCA_BIN` when the fork is not first on `PATH` (see `resolve_asca_bin` in [`appliers/asca.py`](../src/conlanger/appliers/asca.py)). Upstream crates.io **0.10.2** lacks `validate` and is not sufficient for inventory or field-isolation checks.