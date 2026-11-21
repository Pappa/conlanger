Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Pipeline vs validate compile output and v4 structured rule objects in asca_rules.yml.
Blocked by:

## Problem Statement

`compile_rules` always fans out optional outputs and composed chains regardless of stochastic picks. Operators cannot rely on bare `CompilerConfig` defaults for pipeline-style output, and on-disk compile rows lack decomposed ASCA fields. Validate and pipeline need explicit config files, not implicit defaults tied to one YAML path.

## Description

Implement [0053-decision-compile-sample-mode-and-yaml-fields.md](0053-decision-compile-sample-mode-and-yaml-fields.md). Depends on [0055](0055-task-compiler-config-merge-and-seed.md) (config merge and `seed`).

**Compile behaviour**

- Add **`sample_alternatives`** to `CompilerConfig` and plumb through `resolve_inventory_targets` (`true` = single path, `false` = enumerate).
- **`compile_rules`:** no default YAML load; optional **`--compiler-config`**. Scalar CLI overrides per 0055.
- Create **`config/pipeline/compiler_config.yml`** with duplicated **`position_templates`**, **`series_mappings`**, and **`group_mappings.yml`** sibling (copy from asca tree).
- Update **`config/compile/asca/compiler_config.yml`** with **`sample_alternatives: false`** (fan-out for validate).

**Serialization (`schema_version: 4`)**

- [`compiled_rule_shape.py`](../../src/conlanger/tools/compiled_rule_shape.py) / [`compiled_rules_yaml.py`](../../src/conlanger/tools/compiled_rules_yaml.py): objects with `input`, `output`, `env`, `exception`, `rule`; object `alternatives`.
- [`compiled_rule_validation_specs`](../../src/conlanger/tools/compiled_rule_shape.py): v3 strings and v4 objects.

**Docs**

- [compile-rules.md](../../docs/system/compile-rules.md), [validate.md](../../docs/system/validate.md), [asca-rules-yaml-schema.md](../../docs/system/asca-rules-yaml-schema.md), [ADR-0018](../../docs/adr/0018-compiled-asca-rules-yaml.md) as needed.

**Regeneration**

- `uv run compile_rules --compiler-config config/compile/asca/compiler_config.yml` then commit `diagnostics/compile/asca_rules.yml`.

**Rename “bundle” (compiler / inventory seam)**

Today **`IndexRuleInventoryBundle`** is one index rule plus **`targets`** (compile paths) and often **`rows`** (validate CSV rows). The name reflects an old compile+validate combine, not what it is.

| Current | Proposed |
|---------|----------|
| `IndexRuleInventoryBundle` | `CompiledIndexRule` |
| `targets` field | `compile_targets` |
| `rows` field | `validation_rows` |
| `compile_index_rule_bundle` | `compile_index_rule` |
| `iter_index_compile_bundles` | `iter_compiled_index_rules` |
| `iter_compiled_inventory_bundles` | `iter_validated_compiled_rules` |
| `_CompileRuleBundle` | `_CompiledRuleInput` (protocol in `compiled_rules_yaml.py`) |
| `bundles_for_row_prefix` | `trim_compiled_rules_for_row_limit` (or equivalent) |

Keep **`bundle`** only for feature-mapping kind in parser config. Update tests, docs (`validate.md`), and [0053](0053-decision-compile-sample-mode-and-yaml-fields.md) **Answer** wording when touched.

## Out of scope

- `rule-inventory-error.csv` filtering.
- CSV export.

## Acceptance Criteria

- [ ] With **no** `--compiler-config`, `compile_rules` uses Pydantic defaults only (`sample_alternatives` true) and writes v4 YAML with **one** branch per rule where optionals exist (same `seed` via CLI/config ⇒ identical output when seeded).
- [ ] With **asca** config, compile fan-out matches current validate target counts (modulo v4 object shape).
- [ ] Pipeline config path produces single-path output; sporadic skip yields `compile_skipped` when `sample_sporadic`/`sample_dialect` are true (defaults or explicit).
- [ ] `validate_rules` passes against v4 YAML from asca-profile compile.
- [ ] Docs: bare compile vs `--compiler-config` for asca (validate) and pipeline profiles.
- [ ] `uv run check` passes after regeneration.
- [ ] Compiler/inventory public names use **`CompiledIndexRule`** / **`iter_compiled_index_rules`** (no `*Bundle*` on this seam except parser `mapping_kind: bundle`).

## Comments