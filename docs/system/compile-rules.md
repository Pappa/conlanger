# Compile rules (`compile_rules`)

Stage 2 of the sound-change rule pipeline: **parse → compile → validate** ([ADR-0013](../adr/0013-parse-compile-validate.md)).

**`uv run compile_rules`** loads the applier-neutral index YAML, compiles each rule to ASCA targets in memory (no ASCA binary), and writes **`diagnostics/compile/asca_rules.yml`** ([ADR-0018](../adr/0018-compiled-asca-rules-yaml.md)).

## Operator usage

```bash
uv run create_index && uv run compile_rules && uv run validate_rules
```

| Flag | Default | Role |
| --- | --- | --- |
| `--yaml-in` | `data/diachronica/index_diachronica.yml` | Applier-neutral index |
| `--compiled-out` | `diagnostics/compile/asca_rules.yml` | Compiled rules v3 output |
| `--limit N` | off | Smoke cap (first N rules) |

Compile logic lives in `inventory_targets.resolve_inventory_targets` and `DiachronicSeries` / `SoundChangeRule` ([sound-change-applier.md](./sound-change-applier.md)).

## `asca_rules.yml` v3 (summary)

Full field reference: [asca-rules-yaml-schema.md](./asca-rules-yaml-schema.md).

| Top-level | Value |
| --- | --- |
| `schema_version` | `3` |
| `sections` | Mirrors index section headers (`index`, `section`); omits `status: skipped` sections |

Per rule:

| Shape | Fields |
| --- | --- |
| Single compile target | `rule_id`, `source`, `rule` (one ASCA line) |
| Optional outputs (one stage) | `rule_id`, `source`, `alternatives` (list of ASCA lines) |
| Multi-stage chain | `rule_id`, `source`, `steps` (list of ASCA lines; optional outputs on one stage only use an `alternatives:` block as that step) |
| Correlated multi-stage branches | `rule_id`, `source`, `alternatives` (list of `{steps: […]}` — one branch per optional path through the chain, e.g. `r → {r,h} → {∅,h}`) |
| Rule skipped | `status: skipped`, `rule` (`#\t` + raw) |
| Sporadic compile skip | `status: compile_skipped`, `rule` |
| Compile failure | `compile_error` (no `rule` / `steps` / `alternatives`) |

Exactly one of `rule`, `alternatives`, or `steps` is present on successful compile rows. `validate_rules` runs ASCA on each recorded line (with `alt_idx` / `step_idx` derived from list position). No pydantic compile-model deserialization from disk. v2 `targets[]` and v1 `series` remain readable for transition.

No `valid` flags — inventory CSVs hold pass/fail.

**Entrypoint:** [`compile_rules.py`](../../src/conlanger/scripts/compile_rules.py) · **IO:** [`compiled_rules_yaml.py`](../../src/conlanger/tools/compiled_rules_yaml.py)
