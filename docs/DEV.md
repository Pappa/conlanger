# Local Development

## Quality gate

Single entrypoint (pytest, per-file coverage, ruff, import-linter):

```bash
uv run check
```

Install git hooks once per clone (runs the same gate on commit):

```bash
uv run pre-commit install
uv run pre-commit run --all-files   # optional smoke
```

Coverage threshold lives in `[tool.coverage.report] fail_under` in `pyproject.toml`; `uv run check` runs full `uv run pytest` first.

During edits, targeted commands:

```bash
uv run pytest <paths> --no-cov
uvx ruff check src tests --fix && uvx ruff format src tests
```

Run `uv run check` before push even when hooks are not installed. See [implement-closure.md](agents/implement-closure.md) when closing `.scratch/` tickets.

# ASCA sound change rule validation

Conlanger validates compiled rules with a **private fork** of [asca-rust](https://github.com/Pappa/asca-rust) at **0.10.3**. That release adds the `validate` subcommand (whole-rule and per-field checks) used by `validate_asca` and the validation inventory. **`uv run compile_rules`** does not need the ASCA binary; only **`uv run validate_rules`** does.

Install the fork into this repo’s `bin/` tree:

```bash
cargo install --git https://github.com/Pappa/asca-rust --tag v0.10.3-dev-validate --root ./lib
```

Verify:

```bash
export ASCA_BIN="$(pwd)/lib/bin/asca"
./lib/bin/asca --version   # asca 0.10.3
./lib/bin/asca validate --help
```

`uv run validate_rules` defaults to the repo-local binary at `lib/bin/asca` (`--use-asca-fork`, on by default). Set `ASCA_BIN` when the fork is not first on `PATH` (see `resolve_asca_bin` in [`appliers/asca.py`](../src/conlanger/appliers/asca.py)). If validate fails because `lib/bin/asca` is missing, run the **Install the fork** block above. Upstream crates.io **0.10.2** lacks `validate` and is not sufficient for inventory or field-isolation checks.