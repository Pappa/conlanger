Type: task
Status: ready-for-agent
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

- [ ] Optional-output detection matches grill gate; paired sets unchanged
- [ ] `SoundChangeRule.alternatives` populated; leaves have empty `alternatives`
- [ ] Parent picks uniformly via instance `Random`; optional `seed` / `rng`; no global `random.seed`
- [ ] `str(rule)` / series render uses frozen parent choice
- [ ] Inventory: `alt_idx` column; alternatives-only rows when present; empty `alt_idx` otherwise
- [ ] Changelog keys on `(source, alt_idx)`; tests updated
- [ ] Targeted tests green; full gate (`uv run pytest`, ruff) when finishing
- [ ] Re-run inventory; note before/after for `{∅` / LonelySet-style optional-output failures in **Answer**

## References

- [Grill 61](61-grill-optional-outputs.md)
- Spanish examples: `index_diachronica_original.html:8156–8157`
- [Ticket 19](19-correction-pass-sporadic-qualifier.md) — `sporadic: true` flag only
- [Ticket 60 parallel-column null](60-correction-pass-parallel-column-null.md)
