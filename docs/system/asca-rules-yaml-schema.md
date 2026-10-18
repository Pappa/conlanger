# Compiled `asca_rules.yml` schema (v3)

On-disk ASCA compile output written by `uv run compile_rules`. **Not** source of truth for the rule index ([ADR-0018](../adr/0018-compiled-asca-rules-yaml.md), [ADR-0002](../adr/0002-applier-neutral-yaml-rule-index.md)). Operators regenerate after index changes, then run `uv run validate_rules`.

**Code:** [`compiled_rules_yaml.py`](../../src/conlanger/tools/compiled_rules_yaml.py), [`compiled_rule_shape.py`](../../src/conlanger/tools/compiled_rule_shape.py). Operator summary: [compile-rules.md](./compile-rules.md).

## Top level

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | `3` | Required; v1/v2 remain readable for transition |
| `sections` | list | Mirrors index section headers; omits `status: skipped` sections |

Each section object:

| Field | Type | Notes |
| --- | --- | --- |
| `index` | string | Section index key (e.g. `6.1.1`) |
| `section` | string | Human section title |
| `rules` | list | Compiled rule entries (below) |

## Per-rule shapes

Every entry includes `rule_id` and `source` (`file:line` provenance).

| Shape | Fields | When |
| --- | --- | --- |
| Single line | `rule: <ASCA string>` | One successful compile target |
| Optional outputs (one stage) | `alternatives: [<ASCA>, …]` | Fan-out on one stage; no top-level `rule` |
| Multi-stage chain | `steps: [<ASCA>, …]` | Adjacent **stages** expanded to ordered lines |
| Correlated branches | `alternatives: [{steps: [<ASCA>, …]}, …]` | Same optional path through a chain (e.g. `r → {r,h} → {∅,h}`) |
| Skipped | `status: skipped`, `rule: "#\t…"` | Index hold-out |
| Sporadic compile skip | `status: compile_skipped`, `rule: …` | Compiler policy skip |
| Compile failure | `compile_error: <message>` | No `rule` / `steps` / `alternatives` |

On successful rows, exactly one of `rule`, `alternatives`, or `steps` is present. Inventory CSVs hold pass/fail — not `valid` flags on this file ([ticket 160/161](../../.scratch/rule-index/issues/160-grill-split-compile-rules-and-compiled-yaml-pipeline.md)).

`validate_rules` validates each recorded ASCA line; list position supplies `step_idx` / `alt_idx` where needed.
