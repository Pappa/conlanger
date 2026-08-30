Type: task
Status: done

# Split `create_index` and `validate_rules` operator commands

Grill 2026-08-30 (`/grill-with-docs` on [map](../map.md)). Logical pipeline stays **parse → compile → validate** ([ADR-0013](../../../docs/adr/0013-parse-compile-validate.md)); operator surface becomes **two scripts**. Compile runs **in memory** inside `validate_rules` — no compiled ASCA or derived YAML written to disk. Follows [ticket 101](101-refactor-config-layout-and-injection.md) composition-root split.

## Problem

`create_index` today parses HTML, writes applier-neutral YAML, then compiles and validates every rule in the same process. That couples parse-only workflows to the ASCA binary, blurs stage boundaries in docs ([ticket 91](91-three-stage-pipeline-docs.md)), and loads `CompilerConfig` even when `--skip-validation` is used.

After [ticket 101](101-refactor-config-layout-and-injection.md), scripts are the only config loaders; this ticket completes the operator seam: parse regen vs inventory regen.

## What to build

### 1. `create_index` — parse only

- Load **`ParserConfig`** only (`load_parser_config()`).
- Parse HTML → write `data/diachronica/index_diachronica_parsed.yml` (unchanged default).
- Write parse diagnostics under **`.scratch/cleaned-rule-index/parse/`**:
  - `manual_mappings_matched_rules.csv` (moved out of `inventory/`)
  - `rule-comment-phrases.md` (moved from `.scratch/cleaned-rule-index/rule-comment-phrases.md`)
- Keep stderr warnings for unmatched manual mappings and corrections.
- **Remove** all validate/inventory flags and code paths: `--skip-validation`, `--field-isolation`, `--probe-words`, `--use-asca-fork`, `--reset-changelog`, `--limit` (validate), inventory CSV writes, `load_compiler_config()`, ASCA binary checks.
- **Hard cut** — no delegation shim for removed flags.

### 2. `validate_rules` — compile (in memory) + validate + inventory

- New script: `src/conlanger/scripts/validate_rules.py`; entry in `pyproject.toml`.
- Load **`CompilerConfig`** only (`load_compiler_config()`).
- Read parsed YAML via new **`read_cleaned_index(path)`** in `index_io.py` (symmetric with `write_cleaned_index`).
- Default paths (zero-arg use case), shared with `create_index`:
  - `--yaml-in` → `DEFAULT_YAML` (`data/diachronica/index_diachronica_parsed.yml`)
  - `--inventory-dir` → `DEFAULT_INVENTORY_DIR` (`.scratch/cleaned-rule-index/inventory/`)
- Move validate half of current `create_index.py`: `iter_inventory_with_field_isolation`, filtered CSVs, error clusters, optional `--field-isolation`, changelog, summary markdown, ASCA fork resolution, `--probe-words`, `--use-asca-fork`, `--reset-changelog`, `--limit`.
- Docstring: loads applier-neutral index, compiles to ASCA in memory for **compile validation** only, writes inventory.

### 3. Shared defaults

- New `src/conlanger/scripts/pipeline_defaults.py`: `ROOT`, `DEFAULT_HTML`, `DEFAULT_YAML`, `DEFAULT_INVENTORY_DIR`, `DEFAULT_PROBE`, parse-scratch paths. Both scripts import from here.

### 4. Tests

- Split `tests/conlanger/scripts/test_create_index.py`:
  - `test_create_index.py` — parse-only behaviour
  - `test_validate_rules.py` — compile+validate behaviour (move relevant tests)
- Add tests for `read_cleaned_index` round-trip if not covered.

### 5. Docs (same PR as code)

- [ADR-0013](../../../docs/adr/0013-parse-compile-validate.md) — consequence bullets: steady-state operator commands.
- [docs/system/validate.md](../../../docs/system/validate.md) — workflow starts at YAML; command `uv run validate_rules`.
- [docs/system/index-diachronica-parser.md](../../../docs/system/index-diachronica-parser.md) — parse command `uv run create_index`.
- [docs/SYSTEM.md](../../../docs/SYSTEM.md) — operator commands column if present.
- [map.md](../map.md) — runtime / operator-command notes.
- Grep-update doc/ticket references that say `uv run create_index` for **validation/inventory** (parse references stay).

## Operator workflow

```bash
uv run create_index && uv run validate_rules
```

- Parse-only correction pass: `uv run create_index`
- Compile-only correction pass (YAML unchanged): `uv run validate_rules`

No wrapper script in scope.

## Acceptance criteria

- [ ] `uv run create_index` writes YAML + parse diagnostics under `parse/`; does not touch `inventory/` or require `asca`
- [ ] `uv run validate_rules` (no args) reads default YAML and writes same inventory artifacts as pre-split `create_index`
- [ ] **Baseline gate:** `uv run create_index && uv run validate_rules` on committed tree → success/error inventory CSVs match pre-split run (ignore changelog timestamp / append-only churn). Revert git changes under `inventory/` between repeated acceptance runs if needed to avoid ok-flip noise
- [ ] Tests split; full gate green (`uv run pytest`, ruff, per-file coverage)
- [ ] Docs and map updated per §5

## Out of scope

- `sample_asca_guess_fixtures.py` (unchanged)
- Wrapper / `regen_all` script
- Compiled rule files or derived YAML on disk
- Brassica
- New ADR (doc tweak to ADR-0013 only)

## Agent Brief

**Category:** enhancement  
**Summary:** Split monolithic `create_index` into parse-only `create_index` and `validate_rules` (in-memory compile + inventory)

**Current behavior:** One CLI parses HTML, writes YAML, compiles each rule in memory, validates via ASCA, writes inventory CSVs. Parse diagnostics (`manual_mappings_matched_rules.csv`) land in `inventory/`.

**Desired behavior:** Two CLIs with shared defaults module. Parse CLI loads parser config only. Validate CLI loads compiler config, reads YAML from disk, runs existing inventory pipeline without re-parse. Steady state is both commands in sequence.

**Key interfaces:**
- `create_index`: `IndexDiachronicaParser`, `write_cleaned_index`, parse diagnostics → `.scratch/cleaned-rule-index/parse/`
- `validate_rules`: `read_cleaned_index`, `iter_inventory_with_field_isolation`, existing inventory writers
- `pipeline_defaults.py`: shared path constants
- `index_io.read_cleaned_index(path) -> dict`

**Acceptance criteria:** see checklist above.

**Out of scope:** see above.
