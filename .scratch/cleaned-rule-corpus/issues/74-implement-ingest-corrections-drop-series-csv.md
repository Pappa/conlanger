Type: task
Status: resolved
Blocked by:

# Implement ingest corrections overlay and drop parse-time series CSV

Spawned from [Grill: correspondence-series mapping source of truth (manual SoT vs rule I/O inference)](72-grill-series-mapping-manual-sot.md) (closed 2026-08-18). Series expansion ontology and config remain in [Grill: correspondence-series expansion config](73-grill-series-mapping-config-sot.md) — **do not** reintroduce parse-time `series_mappings.csv` here.

## What to build

### 1. Pre-lxml `<sub>` normalisation

- Load HTML as an in-memory string; **never** write the file.
- Whole-file replace `<sub>…</sub>` → Unicode via `to_subscript` before lxml parse.
- Nested markup inside `<sub>`: skip that tag (naive policy from grill).
- Retire subscript conversion in `extract_text_with_subs` tree walk; extract text only.

### 2. Index Diachronica corrections overlay

- Path: `data/diachronica/index_diachronica_corrections.yml`.
- Shape: flat YAML map `rule_id: Unicode_line` (no `<sub>` markup).
- When a `p.schg` has an `id` and the file has that key, the correction line **is `raw`** (after text extract from the element, before Manual mapping).
- Missing or empty file → no replacements.
- Keys in the file that match no rule id → warn once per regen (same spirit as unmatched Manual mapping patterns).

Migrate the existing nested draft (`sections` / `idx`) to flat **rule id** keys (lookup ids from HTML for the three draft rows).

### 3. Manual mapping order

Unchanged relative to corrections: Manual mapping runs on a **working copy** only; **`raw` is not rewritten** by Manual mapping. First match; `use_regex` means `from` is a pattern.

### 4. Drop parse-time correspondence-series **mapping** (retired CSV)

- Remove `apply_series_mappings` (correspondence-index → IPA) from `IndexDiachronicaParser`.
- Stop loading `series_mappings.csv` for parse.
- Do **not** populate section `abbreviations` from series CSV; omit `abbreviations` when empty.
- **Correspondence-series indices** (`h₁`, `s₁`, …) stay Index-shaped in index until compile ([75](75-implement-compiler-config-series-mappings.md)).

### 4b. Parse-time collective **series expansions** (`parser_config.yml`)

Per [grill 73](73-grill-series-mapping-config-sot.md): load `series_expansions` from `data/parser_config.yml` and apply at parse **after** Manual mapping on index field values (`stages`, env, exception). **`raw` unchanged.**

```yaml
series_expansions:
  Hₓ: [h₁, h₂, h₃]
  hₓ: [h₁, h₂, h₃]
  sₓ: [s₁, s₂, s₃]
```

- Global table only (no section scope).
- Standalone collective: `sₓ → ʃ` → `{s₁,s₂,s₃} → ʃ`.
- Inside a set: `{Hₓ,m̩,n̩} → a` → `{h₁,h₂,h₃,m̩,n̩} → a` (flatten members; no nested set).
- Separate rows for `Hₓ` and `hₓ` (same member list).

### 4c. Compile config deferred

- `data/compiler_config.yml` **series_mappings** and PIE laryngeal compile apply → [75](75-implement-compiler-config-series-mappings.md).
- `PIE_LARYNGEAL_ALIASES` stays in Python until 75 lands.

Retire or gate `update_series_mappings` script and `series_extract` integration from regen if they only served the deleted CSV path (tests may keep minimal fixtures).

### 5. **Rule id** replaces positional `rule_idx`

- Corpus rules carry `rule_id` (HTML `id` on `p.schg`).
- Inventory CSV, changelog, `manual_mappings_matched_rules.csv`, and `ManualMappingMatch` use `rule_id` instead of `rule_idx`.
- Update tests and any docs that still say `rule_idx` as the stored identifier.

### 6. Regen + inventory

- `uv run create_index` after implementation.
- Record before/after `ok` totals; inventory **ok** drop from removing I/O-inferred expansions is **expected and accepted** (grill 72).

## Explicitly out of scope

- Defined vs indeterminate correspondence-series expansions, config file shape, unknown-token skip policy — [ticket 73](73-grill-series-mapping-config-sot.md).
- Moving `PIE_LARYNGEAL_ALIASES` into a config file.
- Re-authoring series mapping rows or a replacement expansion mechanism.
- Positional / identity subscript compile passes.

## Acceptance criteria

- [x] Parse order matches grill 72: in-memory HTML → `<sub>` replace → lxml → corrections overlay → Manual mapping → rest of parse **without** series expansion.
- [x] `index_diachronica_corrections.yml` flat `rule_id` keys; draft rows migrated.
- [x] Corpus rules include `rule_id`; inventory/debug CSVs use `rule_id`.
- [x] Parse collective `series_expansions` from `parser_config.yml` (flatten sets; `raw` unchanged).
- [x] No runtime dependency on `series_mappings.csv` in parse path.
- [x] `section_abbreviations.yml` not regenerated; empty section `abbreviations` omitted.
- [x] Tests updated; targeted pytest green.
- [x] Full regen + inventory; before/after metrics in **Answer**.

## Answer

**Inventory (ASCA 0.10.2, 2026-08-18 regen)**

| Metric | Before | After |
| --- | ---: | ---: |
| OK / total | 7990 / 9640 (82.9%) | **7957 / 9640 (82.5%)** |
| Sections all OK | 268 / 714 (37.5%) | **271 / 714 (38.0%)** |

−33 ok rules from dropping parse-time I/O-inferred `series_mappings.csv` expansion (accepted per grill 72). Corrections overlay applied for `Blackfoot-nr`, `Blackfoot-ʔθ,ʔr`, `Dena’ina-ʃʷ,x-z,ʒʷ,ɣ`. Collective `series_expansions` (`Hₓ`, `hₓ`, `sₓ`) fan out at parse; correspondence-series indices stay literal until compile ([75](75-implement-compiler-config-series-mappings.md)). `update_series_mappings` CLI gated behind `--legacy-extraction`.

## References

- `CONTEXT.md` — **Index Diachronica correction**, **Rule id**, **Correspondence-series index**, **Collective subscript**
- ADR-0004 (amended 2026-08-18), ADR-0012 (corrections overlay)
- [Parse-time manual rule mappings](60-parse-time-manual-rule-mappings.md)
- `src/conlanger/tools/ingest/parser.py`, `src/conlanger/tools/index_inventory.py`, `src/conlanger/utils/file_io.py`
