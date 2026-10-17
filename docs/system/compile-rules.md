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
| `--compiled-out` | `diagnostics/compile/asca_rules.yml` | Compiled rules v2 output |
| `--limit N` | off | Smoke cap (first N rules) |

Compile logic lives in `inventory_targets.resolve_inventory_targets` and `DiachronicSeries` / `SoundChangeRule` ([sound-change-applier.md](./sound-change-applier.md)).

## `asca_rules.yml` v2 (summary)

| Top-level | Value |
| --- | --- |
| `schema_version` | `2` |
| `sections` | Mirrors index section headers (`index`, `section`); omits `status: skipped` sections |

Per rule:

| Shape | Fields |
| --- | --- |
| Compile OK | `rule_id`, `source`, `targets[]` |
| Rule skipped | `status: skipped`, `rule` (`#\t` + raw) |
| Sporadic compile skip | `status: compile_skipped`, `rule` |
| Compile failure | `compile_error` (no `targets`) |

Each `targets[]` entry: `step_idx`, `alt_idx`, `rule` (ASCA line string recorded at compile time). `validate_rules` runs ASCA on that line only — no pydantic compile-model deserialization from disk. Compile still uses `DiachronicSeries` in memory inside `compile_rules`. No `valid` flags — inventory CSVs hold pass/fail.

v1 files (with `series` on each target) remain readable; re-run `compile_rules` to shrink on-disk artifacts.

**Entrypoint:** [`compile_rules.py`](../../src/conlanger/scripts/compile_rules.py) · **IO:** [`compiled_rules_yaml.py`](../../src/conlanger/tools/compiled_rules_yaml.py)
