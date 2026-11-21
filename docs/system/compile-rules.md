# Compile rules (`compile_rules`)

Stage 2 of the sound-change rule pipeline: **parse → compile → validate** ([ADR-0013](../adr/0013-parse-compile-validate.md)).

**`uv run compile_rules`** loads the applier-neutral index YAML, compiles each rule to ASCA targets in memory (no ASCA binary), and writes **`diagnostics/compile/asca_rules.yml`** ([ADR-0018](../adr/0018-compiled-asca-rules-yaml.md)).

## Operator usage

```bash
uv run create_index
# Validate profile (fan-out, reproducible seed, no sporadic sampling)
uv run compile_rules --compiler-config config/compile/asca/compiler_config.yml
uv run validate_rules

# Pipeline / ML (class defaults: single stochastic path, sporadic sampling on)
uv run compile_rules
# or explicit mappings:
uv run compile_rules --compiler-config config/pipeline/compiler_config.yml
```

| Flag | Default | Role |
| --- | --- | --- |
| `--yaml-in` | `data/diachronica/index_diachronica.yml` | Applier-neutral index |
| `--compiled-out` | `diagnostics/compile/asca_rules.yml` | Compiled rules v4 output |
| `--compiler-config` | *(none)* | YAML package (`compiler_config.yml` + `group_mappings.yml` beside it). Omitted ⇒ Pydantic defaults only |
| `--sample-alternatives` | from config / default | `true` = one stochastic branch; `false` = validate fan-out |
| `--sample-sporadic` / `--sample-dialect` | from config / default | CLI overrides for sporadic/dialect compile skip |
| `--seed` | from config / default | CLI override for compile RNG |
| `--limit N` | off | Smoke cap (first N rules) |

**`sample_alternatives`:** when `true`, optional outputs and composed chains keep the RNG-picked branch only (pipeline). When `false`, `resolve_inventory_targets` enumerates all branches (validate inventory row counts).

Compile logic lives in `inventory_targets.resolve_inventory_targets` and `DiachronicSeries` / `SoundChangeRule` ([sound-change-applier.md](./sound-change-applier.md)).

## `asca_rules.yml` v4 (summary)

Full field reference: [asca-rules-yaml-schema.md](./asca-rules-yaml-schema.md).

| Top-level | Value |
| --- | --- |
| `schema_version` | `4` |
| `sections` | Mirrors index section headers (`index`, `section`); omits `status: skipped` sections |

Per rule, each compile line is an **object** with decomposed ASCA fields (`input`, `output`, optional `env` / `exception`) plus joined `rule`. Successful rows use exactly one of:

| Shape | Fields |
| --- | --- |
| Single compile target | `rule_id`, `source`, `input`, `output`, …, `rule` |
| Optional outputs (one stage) | `rule_id`, `source`, `alternatives` (list of field objects) |
| Multi-stage chain | `rule_id`, `source`, `steps` (list of field objects or `{alternatives: […]}`) |
| Correlated multi-stage branches | `rule_id`, `source`, `alternatives` (list of `{steps: [objects…]}`) |
| Rule skipped | `status: skipped`, `rule` (`#\t` + raw string) |
| Sporadic compile skip | `status: compile_skipped`, `rule` |
| Compile failure | `compile_error` (no compile lines) |

`validate_rules` runs ASCA on each object’s `rule` string (v3 string rows remain readable). No pydantic compile-model deserialization from disk.

No `valid` flags — inventory CSVs hold pass/fail.

**Entrypoint:** [`compile_rules.py`](../../src/conlanger/scripts/compile_rules.py) · **IO:** [`compiled_rules_yaml.py`](../../src/conlanger/tools/compiled_rules_yaml.py)