Type: task
Status: resolved
Blocked by: 61

# Implement optional outputs + `alt_idx` + instance RNG

Spawned from [grill 61](61-grill-optional-outputs.md) (owner confirmed 2026-08-12). Glossary: **Optional outputs** in `CONTEXT.md`.

## Problem

Index rules like `d → {∅,ð} / V_V` keep an opaque set in **stages**. ASCA rejects set-internal `∅` (`d > {∅,ð} / V_V` fails; `d > ∅ / V_V` and `d > ð / V_V` are valid). Compile must resolve unpaired output sets into concrete ASCA strings without splitting the YAML corpus rule, while tests and inventory exercise every alternative.

## What to build

### `SoundChangeRule`
1. **Detect** optional outputs: whole-field output `{…}` and input **not** a whole-field set. Do **not** treat paired `{a,b} → {c,d}` as optional outputs. Nested sets and uneven zip are out of scope ([67](67-spike-nested-sets.md), other clusters).
2. On instantiation, parse set members (Index/set order) and build `alternatives: list[SoundChangeRule]` — full peer instances; **leaves have no children** (`alternatives == []`).
3. Pick **one** alternative **uniformly** via `random.Random` as the parent’s compiled output/`value`. Accept optional ctor `seed` and/or caller-supplied `Random`. If omitted: unseeded `Random()` (nondeterministic parent pick only).
4. **Do not** use process-global `random.seed`.
5. `str()` renders the frozen choice (no re-sample).
6. Keep RNG plumbing reusable for later [sporadic sampling](68-sporadic-sampling.md) — do not implement apply/skip here.

### Inventory
1. Add column **`alt_idx`** immediately after `rule_idx` in inventory CSVs / `ValidationRow` / summary docs as needed.
2. When `alternatives` is non-empty: emit **only** alternative rows (`alt_idx` 0-based). Do **not** inventory the parent’s random pick.
3. When no alternatives: one row with **`alt_idx` empty**.
4. Changelog / uniqueness: match on `(source, alt_idx)` (today keys on `source` alone — update `ok_flip_changelog_rows` and tests).

### Tests
- Unit tests: detection gate; `alternatives` contents; seeded parent pick; each alternative validates independently; inventory `alt_idx` + changelog identity.

## Out of scope
- Nested sets → [67](67-spike-nested-sets.md)
- Sporadic apply/skip → [68](68-sporadic-sampling.md)
- Uneven paired sets / UnevenSet repair
- Splitting corpus YAML into one rule per alternative
- Ticket 60 parallel-column top-level `∅` (already handled)

## Acceptance criteria

- [x] Optional-output detection matches grill gate; paired sets unchanged
- [x] `SoundChangeRule.alternatives` populated; leaves have empty `alternatives`
- [x] Parent picks uniformly via instance `Random`; optional `seed` / `rng`; no global `random.seed`
- [x] `str(rule)` / series render uses frozen parent choice
- [x] Inventory: `alt_idx` column; alternatives-only rows when present; empty `alt_idx` otherwise
- [x] Changelog keys on `(source, alt_idx)`; tests updated
- [x] Targeted tests green; full gate (`uv run pytest`, ruff) when finishing
- [x] Re-run inventory; note before/after for `{∅` / LonelySet-style optional-output failures in **Answer**

## Answer

Implemented 2026-08-12.

### `SoundChangeRule` (`src/conlanger/tools/rules.py`)
- Optional-output detection via `_is_whole_field_set`: whole-field `{…}` output + input **not** a whole-field set. Paired `{a,b} → {c,d}`, nested sets, and empty members yield **no** alternatives (out of scope → [67](67-spike-nested-sets.md)).
- `alternatives: list[SoundChangeRule]` built as full leaf peers (Index/set order; each leaf `alternatives == []`).
- Instance RNG only: optional ctor `seed` / `rng`, falling back to `random.Random(seed)`; process-global `random.seed` is never touched. Parent freezes one uniform `randrange` pick as its `value`; `str()` re-renders that frozen choice (no re-sample).

### Inventory (`src/conlanger/tools/corpus_inventory.py`)
- `alt_idx` column added immediately after `rule_idx` in `ValidationRow`, `VALIDATION_CSV_COLUMNS`, and `CHANGELOG_CSV_COLUMNS`.
- `validate_corpus_rule` now returns `list[ValidationRow]`: alternatives-only rows with 0-based `alt_idx` when the rule has alternatives (parent's random pick is never inventoried), else a single row with empty `alt_idx`. `iter_validation_rows` flattens.
- Changelog uniqueness moved to `(source, alt_idx)` (`ok_flip_changelog_rows` + `_alt_idx_key`).

### Tests
- New `tests/conlanger/tools/test_optional_outputs.py`: detection gate, alternatives contents/leaf-ness, seeded + caller-`rng` picks, frozen render, global-RNG-state isolation, per-alternative ASCA validation.
- New inventory tests for alternative rows + `(source, alt_idx)` changelog; existing callers updated for the list return (`test_corpus_inventory.py`, `test_corpus_pipeline.py`).
- Full gate green: `uv run pytest` → **916 passed**, coverage **95.19%** (≥95); `ruff check` + `ruff format --check` clean.

### Inventory before/after (optional-output subset)
Measured over the **363** optional-output candidate rules in `data/diachronica/index_diachronica_parsed.yml` (800 alternatives; 62 with a null `∅`/`*` member):

- **Before** — whole set compiled to ASCA (committed `asca-rule-inventory.csv`): **234 ok / 129 fail**. The 129 failures are the set-internal `∅` / LonelySet-style rejections ASCA cannot represent (`d > {∅,ð}`).
- **After** — per-alternative rows: **727 / 800** alternatives validate; **327 / 363** candidates have every alternative valid. The residual 73 alternative failures are unrelated ASCA issues (nested/other clusters), not the `{∅` rejection.

Net: the in-scope single-step optional-output rejection class (`{∅`) is resolved by splitting into per-alternative `alt_idx` rows. A full `regenerate_corpus` run will now emit the `alt_idx` column and alternative rows across the whole inventory; it was not committed here to avoid unrelated corpus-diff churn.

## References

- [Grill 61](61-grill-optional-outputs.md)
- Spanish examples: `index_diachronica_original.html:8156–8157`
- [Ticket 19](19-correction-pass-sporadic-qualifier.md) — `sporadic: true` flag only
- [Ticket 60 parallel-column null](60-correction-pass-parallel-column-null.md)
