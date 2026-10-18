Type: task
Status: resolved
Blocked by:

# Task: validate compiled rules from ASCA lines only (drop `DiachronicSeries` YAML round-trip)

Spawned from grill pause on [167](167-grill-index-identity-exception-env-splice.md) (2026-10-17). **Symptom:** `compile_rules` writes a correct ASCA `rule:` line (e.g. West-Germanic-C → `{C,-r} > C:[+long] / _j` with `exception.compiled: null`), but `validate_rules` rebuilds via `inventory_target_from_yaml` → `deserialize_series` → `SoundChangeRule.__str__`, and `compiled_target_serde._field_model` sets `compiled = raw` when `compiled is None`, re-attaching `// C = r` and causing false `expected_number` failures.

Owner direction: full `DiachronicSeries` / `SoundChangeRule` serialization inside `asca_rules.yml` is no longer justified for validation — **`validate_rules` only needs enough structure to render a `.rsca` file for `asca validate` / `asca run`**, not to re-instantiate compile models from disk.

## Question

How should `asca_rules.yml` and `validate_rules` change so validation uses the **compiled ASCA syntax already produced at compile time**, without round-tripping pydantic compile types through YAML (and without re-joining fields from Index `raw` exception strings)?

## Scope

### In scope

1. **Validation path:** `iter_compiled_inventory_bundles` / `_asca_validation_row` (and `validate_asca` callers) must validate the same ASCA line(s) `compile_rules` recorded — at minimum the per-target `rule` string; no `deserialize_series` for inventory `ok`.
2. **Schema simplification (v2 or v1 amend):** Remove or stop writing the bloated `targets[].series` payload once validate no longer needs it; keep what operators need to diff (section headers, `rule_id`, `source`, `step_idx` / `alt_idx`, ASCA `rule` line(s), skipped / `compile_error` shapes). Propose concrete v2 in PR; bump `schema_version` if breaking.
3. **Regression tests:** West-Germanic-C, at least one Family A identity rule (e.g. Egypto-Berber-r_2 or Tocharian-A-V), skipped rule comment line, optional-output / multi-target if still supported.
4. **Docs:** Amend [ADR-0018](../../../docs/adr/0018-compiled-asca-rules-yaml.md) and [compile-rules.md](../../../docs/system/compile-rules.md); note that compile still uses `DiachronicSeries` in memory — only the **on-disk validate artifact** slimmed.
5. **Cleanup:** Delete or gate dead code in `compiled_target_serde.py` if `series` is removed; keep `compile_rules` compile path unchanged unless required for writing the slimmer file.

### Out of scope

- Index identity-exception compile policy ([167](167-grill-index-identity-exception-env-splice.md) / [168](168-task-index-identity-exception-residuals.md)) — except where this task fixes **false validation failures** caused by serde.
- Changing applier-neutral index YAML or compile transforms in `identity_exceptions.py`.
- Field-isolation blame rearchitecture (may continue to use compile models at compile time; if blame reads compiled YAML, align with new schema).

## Acceptance

- [x] `uv run compile_rules && uv run validate_rules` — West-Germanic-C (and other Family B identity rows previously failing with `// Host = RHS` in error CSV) **OK** when compile output is correct.
- [x] No validation code path sets `exception.compiled` from `exception.raw` for join purposes.
- [x] `asca_rules.yml` on disk materially smaller (no per-rule full `SoundChangeRule` dump) per agreed v3 schema.
- [x] Full test suite + quality gates; inventory regen with documented ok delta (expect identity `expected_number` cluster shrink without compile logic changes).

## Answer (2026-10-17)

- **`asca_rules.yml` v3** (`schema_version: 3`): per-rule `rule` / `steps` / `alternatives` ASCA lines only; `compile_rules` writes via `compiled_rule_shape.py`; v1/v2 `series` / `targets[]` still readable for transition ([ADR-0018](../../../docs/adr/0018-compiled-asca-rules-yaml.md), [compile-rules.md](../../../docs/system/compile-rules.md)).
- **`validate_rules`:** `iter_compiled_inventory_bundles` validates recorded `rule` strings directly (`inventory_target_from_yaml`); no `deserialize_series` → `SoundChangeRule.__str__` round-trip on the steady-state path.
- **Inventory:** West-Germanic-C and related identity rows flip **FAILED → OK** in changelog (2026-10-17); `expected_number` cluster shrinks without compile transform changes. Regression: `test_compiled_validation_uses_rule_line_without_series_round_trip` in `test_index_inventory.py`.

## Related

- [Grill: split `compile_rules` vs `validate_rules`](160-grill-split-compile-rules-and-compiled-yaml-pipeline.md) · [ADR-0018](../../../docs/adr/0018-compiled-asca-rules-yaml.md) · `compiled_target_serde.py` (`_field_model` fallback) · `inventory_target_from_yaml`
