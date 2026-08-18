Type: task
Status: ready-for-agent
Blocked by: 74

# Implement compiler_config.yml series mappings at compile

Spawned from [Grill: correspondence-series expansion config](73-grill-series-mapping-config-sot.md) (closed 2026-08-18). Parse-time **series expansions** (collectives) ship in [74](74-implement-ingest-corrections-drop-series-csv.md) via `parser_config.yml`.

## What to build

### 1. `data/compiler_config.yml`

New package file for **compile-time** configuration (distinct from `data/parser_config.yml` parse settings).

```yaml
series_mappings:
  global:
    h₁: h
    h₂: x
    h₃: ɣʷ
  sections:
    - section: "17.10"
      h₁: h
      h₂: x
      h₃: ɣʷ
```

- **`global`** — applies everywhere unless a section row overrides the same token.
- **`sections`** — list of objects: required `section` index string + token→target map entries at the same level.
- Lookup: longest-prefix match on section index (same as retired `series_mappings.csv`); section row beats `global` for that token.
- Optional user overlay path in loader API (merge deferred; package file wins until overlay exists — grill 73 Q13).

### 2. Compile apply pass

- Load `compiler_config.yml` in regen / `DiachronicSeries` compile path.
- New step **before** `expand_index_subscript_references` (positional/identity): expand **correspondence-series indices** in joined rule strings via hierarchical lookup.
- Replace `PIE_LARYNGEAL_ALIASES` / `apply_asca_aliases` laryngeal substring replace with config-driven **series_mappings** global rows (same targets: `h₁→h`, `h₂→x`, `h₃→ɣʷ`).
- Apply on compile-expanded rule strings (stages spine + env/exception), not on `raw`.
- Unmapped indices: leave literal; validation fails (no pre-emptive skip).

### 3. Retire old paths

- Remove `data/asca/series_mappings.csv` from compile/parse runtime (74 drops parse path).
- Delete or gate `update_series_mappings` / `series_extract` regen integration if obsolete.
- Remove `PIE_LARYNGEAL_ALIASES` dict from Python once config rows cover laryngeals.

### 4. Authoring policy (grill 73)

Mapping rows may come from citation/inventory prose, conventional reconstructions, or owner judgment with audit notes — **never** rule I/O inference or opaque placeholders (`s₁→f1`).

Seed `global` PIE laryngeals; section overrides only where Index prose requires. Do not auto-reimport I/O-inferred rows from retired CSV.

## Explicitly out of scope

- `series_expansions` collectives at parse ([74](74-implement-ingest-corrections-drop-series-csv.md)).
- User overlay merge implementation (API stub only).
- `section_abbreviations.yml` regeneration.

## Acceptance criteria

- [ ] `load_compiler_config()` + hierarchical lookup tests
- [ ] Compile pipeline applies mappings; laryngeals from YAML not Python
- [ ] Inventory before/after in **Answer**
- [ ] Tests green; no runtime dependency on `series_mappings.csv`

## References

- [Grill 73 answer](73-grill-series-mapping-config-sot.md)
- ADR-0004 (amended 2026-08-18)
- `src/conlanger/tools/compile/asca/pipeline.py`
