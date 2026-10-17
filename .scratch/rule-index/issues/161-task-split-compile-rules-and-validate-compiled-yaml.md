Type: task
Status: ready-for-agent
Blocked by: None

# Task: `compile_rules` script and validation-only `validate_rules` from compiled YAML

Spawned from [Grill: split `compile_rules` vs `validate_rules` and compiled YAML pipeline](160-grill-split-compile-rules-and-compiled-yaml-pipeline.md) (resolved 2026-10-17).

## Question

Implement the three-command operator pipeline and compiled `asca_rules.yml` contract locked in grill **160**.

## Answer (from 160)

See [160 Answer](160-grill-split-compile-rules-and-compiled-yaml-pipeline.md#answer).

## Acceptance

### `compile_rules`

- [ ] New entrypoint `uv run compile_rules` (`src/conlanger/scripts/compile_rules.py`, `pyproject.toml`).
- [ ] Reads applier-neutral index (`--yaml-in`, default `DEFAULT_YAML`); loads `CompilerConfig` only (no ASCA binary).
- [ ] Compiles every index rule via shared target resolution (extract/refactor today’s `_resolve_inventory_targets` out of validate-only path).
- [ ] Writes `diagnostics/compile/asca_rules.yml` by default (`--compiled-out`, `DEFAULT_COMPILED_YAML` in `pipeline_defaults.py`).
- [ ] Embeds per-rule `source` from index at compile time.

### `asca_rules.yml` schema (v1)

- [ ] Top-level `schema_version: 1` and `sections:` (section `index` / `section`; omit section-level `status: skipped` sections).
- [ ] Per rule: `rule_id`, optional `source`, optional `status` (`skipped` | `compile_skipped`), optional `compile_error`, optional single `rule` line for skip shapes.
- [ ] Compile success: `targets: [{step_idx, alt_idx, rule, series}]` where `series.parts` round-trips `DiachronicSeries.from_parts` for `validate_asca` (no `valid` keys). Tests: each target’s `rule` string matches deserialised `SoundChangeRule` line used for validation.
- [ ] Regenerated `diagnostics/compile/asca_rules.yml` **committed** when pipeline is run for PRs (same policy as inventory outputs).
- [ ] No `index` hash / freshness field in v1 schema; document operator order in ADR + validate doc.
- [ ] Refactor `compiled_rules_yaml.py` to emit v1 from compile targets, not from `ValidationRow`s.

### `validate_rules`

- [ ] Reads compiled YAML only (`--compiled-in`, default `DEFAULT_COMPILED_YAML`); does **not** read index YAML, **no `--yaml-in`**, and does not load `CompilerConfig` for compile.
- [ ] Inventory + optional field isolation unchanged in CSV schema; row generation from deserialized targets (`_asca_validation_row`, `build_field_isolation_row`).
- [ ] Remove writing compiled YAML from validate; drop `--no-write-compiled-rules` / compile-dir write flags (replace with read default).
- [ ] Correction summary still uses `ParserConfig.corrections` + `rule_id` from rows (no index file).

### ADRs and docs (required — same PR as code)

Pipeline split changes operator surfaces and where compile output lives on disk; **project ADRs and system docs need explicit updates**, not only a map note.

**ADRs (amend or add)**

- [ ] [ADR-0013](../../../docs/adr/0013-parse-compile-validate.md) — operator commands (`create_index` → `compile_rules` → `validate_rules`); compile as on-disk stage output (`asca_rules.yml`), not only in-memory inside validate; inventory still under validate.
- [ ] [ADR-0003](../../../docs/adr/0003-validate-after-applier-compile.md) — if consequences still say validate “compiles” from index YAML, align with validate reading compiled YAML (gate unchanged: still post-compile).
- [ ] **New ADR** — compiled `asca_rules.yml` artifact: role (not SoT), path, `schema_version` v1, git-tracked regeneration, relationship to applier-neutral index ([ADR-0002](../../../docs/adr/0002-applier-neutral-yaml-rule-index.md)); supersession of **103** “no compiled artifacts on disk” for steady state.

**System and operator docs**

- [ ] [docs/SYSTEM.md](../../../docs/SYSTEM.md) — pipeline table: compile row operator command + artifact path (not “in-memory inside `validate_rules`”).
- [ ] [docs/system/validate.md](../../../docs/system/validate.md) — steady-state workflow, mermaid, default paths, flags (`--compiled-in` not `--yaml-in` / `--no-write-compiled-rules`), correction loop steps, entrypoint table.
- [ ] [docs/system/sound-change-applier.md](../../../docs/system/sound-change-applier.md) — `uv run compile_rules` as compile-stage operator entry; link to `asca_rules.yml` v1 schema (section or pointer to validate doc).
- [ ] [docs/system/index-diachronica-parser.md](../../../docs/system/index-diachronica-parser.md) — parse-only vs downstream compile (if operator commands mentioned).
- [ ] [docs/DEV.md](../../../docs/DEV.md) — local workflow / ASCA binary required for `validate_rules` only.
- [ ] New or updated **compile-stage doc** if warranted (e.g. `docs/system/compile-rules.md` or a dedicated section in applier doc) describing `asca_rules.yml` v1 fields.
- [ ] [map.md](../map.md) — runtime / Notes already charted; sync after implementation.

**Grep hygiene (update stale two-command / in-memory compile prose)**

- [ ] `docs/` and root [CONTEXT.md](../../../CONTEXT.md) / [AGENTS.md](../../../AGENTS.md) if they reference `create_index && validate_rules` or validate-time compile.
- [ ] Do **not** bulk-edit closed `.scratch/rule-index/issues/*` tickets; optional one-line note in [103](103-split-create-index-and-validate-rules.md) Answer that steady state was amended by 160/161.

### Tests

- [ ] `compile_rules` smoke; v1 YAML round-trip; `validate_rules` reads compiled file (mock or fixture); update `test_compiled_rules_yaml.py` / `test_validate_rules.py`.

### Baseline

- [ ] Full pipeline `uv run create_index && uv run compile_rules && uv run validate_rules`: inventory ok/fail/skipped counts match pre-split `create_index && validate_rules` on same tree (allow changelog timestamp churn only).

## Related

- [103](103-split-create-index-and-validate-rules.md) · [151](151-grill-validate-rules-asca-rules-yaml-diagnostic.md) · [158](158-task-inventory-validate-all-compile-targets.md) · [159](159-task-write-compile-asca-rules-yml.md)
