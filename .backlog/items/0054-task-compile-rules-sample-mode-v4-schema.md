Type: task
Status: needs-detail
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Pipeline vs validate compile output and v4 structured rule objects in asca_rules.yml.
Blocked by: 0053, 0055

## Problem Statement

`compile_rules` always fans out optional outputs and composed chains for validate/diagnostics and always uses a hard-coded compile RNG seed. Pipeline consumers need **one stochastic path** per rule (when configured), decomposed **input / output / env / exception** on disk, and a single compile code path driven by **compiler config**, not a parallel exporter.

## Description

Implement the resolved [**0053**](0053-decision-compile-sample-mode-and-yaml-fields.md) (after [0055](0055-task-compiler-config-merge-and-seed.md)).

**Compile behaviour**

- Depends on [0055](0055-task-compiler-config-merge-and-seed.md) for config precedence and `seed`.
- Add pipeline compiler config at `config/pipeline/compiler_config.yml` and wire `compile_rules` to load the chosen config package (details per **0053** — **not** the discarded `--sample` draft).
- Plumb merged `CompilerConfig` through `iter_index_compile_bundles` / `resolve_inventory_targets` (single-path vs enumerate per **0053**).

**Serialization (`schema_version: 4`)**

- Extend [`compiled_rule_shape.py`](../../src/conlanger/tools/compiled_rule_shape.py) and [`compiled_rules_yaml.py`](../../src/conlanger/tools/compiled_rules_yaml.py) to emit rule records with `input`, `output`, `env`, `exception`, and joined `rule`; `alternatives` as object lists; update `steps` / correlated branches consistently.
- Update [`compiled_rule_validation_specs`](../../src/conlanger/tools/compiled_rule_shape.py) to accept **v3 string** and **v4 object** rows.

**Docs**

- [compile-rules.md](../../docs/system/compile-rules.md), [validate.md](../../docs/system/validate.md), [asca-rules-yaml-schema.md](../../docs/system/asca-rules-yaml-schema.md) — per **0053** operator contract (no `--sample` unless decision reintroduces it).

**Tests**

- Single-path vs fan-out target counts; seed stability per config; sporadic `compile_skipped` only when pipeline sampling is on.
- v4 round-trip and validate_specs for object alternatives.

**Regeneration**

- Re-run validate-profile compile and commit `diagnostics/compile/asca_rules.yml` when behaviour/schema stabilises.

## Out of scope

- Filtering rules by `rule-inventory-error.csv`.
- CSV export.
- CompilerConfig merge / seed ([0055](0055-task-compiler-config-merge-and-seed.md)).

## Acceptance Criteria

_(Refresh when **0053** is **resolved**; placeholders below.)_

- [ ] Pipeline-profile compile writes v4 YAML with **one** branch per rule where optionals exist; same config `seed` yields identical output.
- [ ] Validate-profile compile writes fan-out equivalent to current expectations (modulo v4 object shape).
- [ ] `validate_rules` passes against v4 YAML from validate-profile compile.
- [ ] Docs describe asca vs pipeline config (no stale `--sample` unless **0053** chooses it).
- [ ] `uv run check` passes after regeneration.

## Comments