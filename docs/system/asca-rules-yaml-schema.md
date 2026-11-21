# Compiled `asca_rules.yml` schema (v4)

On-disk ASCA compile output written by `uv run compile_rules`. **Not** source of truth for the rule index ([ADR-0018](../adr/0018-compiled-asca-rules-yaml.md), [ADR-0002](../adr/0002-applier-neutral-yaml-rule-index.md)). Operators regenerate after index changes, then run `uv run validate_rules`.

**Code:** [`compiled_rules_yaml.py`](../../src/conlanger/tools/compiled_rules_yaml.py), [`compiled_rule_shape.py`](../../src/conlanger/tools/compiled_rule_shape.py). Operator summary: [compile-rules.md](./compile-rules.md).

## Top level

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | `4` | Required; v1–v3 remain readable for transition |
| `sections` | list | Mirrors index section headers; omits `status: skipped` sections |

Each section object:

| Field | Type | Notes |
| --- | --- | --- |
| `index` | string | Section index key (e.g. `6.1.1`) |
| `section` | string | Human section title |
| `rules` | list | Compiled rule entries (below) |

## Compiled rule object (v4)

Each ASCA line is a mapping with:

| Field | Type | Notes |
| --- | --- | --- |
| `input` | string | Compiled input (when present) |
| `output` | string | Compiled output (when present) |
| `env` | string | Compiled environment (optional) |
| `exception` | string | Compiled exception (optional) |
| `rule` | string | Joined ASCA line (validation uses this) |

## Per-rule shapes

Every entry includes `rule_id` and `source` (`file:line` provenance).

| Shape | Fields | When |
| --- | --- | --- |
| Single line | field object keys at top level | One successful compile target |
| Optional outputs (one stage) | `alternatives: [object, …]` | Fan-out on one stage |
| Multi-stage chain | `steps: [object \| {alternatives: […]}, …]` | Adjacent stages |
| Correlated branches | `alternatives: [{steps: [object, …]}, …]` | Same optional path through a chain |
| Skipped | `status: skipped`, `rule: "#\t…"` | Index hold-out (string `rule`) |
| Sporadic compile skip | `status: compile_skipped`, `rule: …` | Compiler policy skip |
| Compile failure | `compile_error: <message>` | No compile lines |

On successful rows, exactly one of a top-level field object (no `steps`/`alternatives` keys), `alternatives`, or `steps` is used. Inventory CSVs hold pass/fail — not `valid` flags on this file.

`validate_rules` validates each recorded `rule` string; list position supplies `step_idx` / `alt_idx` where needed. v3 string-only rows remain supported during transition.