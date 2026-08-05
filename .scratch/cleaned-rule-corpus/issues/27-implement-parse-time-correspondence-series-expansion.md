Type: task
Status: needs-triage
Blocked by: 28

# Implement parse-time correspondence-series expansion

## What to build

Apply [Parse-time resolution for correspondence-series indices](26-parse-time-correspondence-series-indices.md) in `IndexDiachronicaParser`:

1. Load per-section maps from **`data/asca/series_mappings.csv`** produced by [Extract correspondence-series mappings from Index Diachronica HTML](28-extract-correspondence-series-mappings-from-html.md) (loaded like `group_mappings.csv` from `data/asca/`).
2. After existing parse-time transforms (symbols, glosses, stress, …), run correspondence-series expansion on corpus field values — **correspondence-series index** and **collective subscript** tokens only; do not expand **positional slots** or **identity subscripts** in this ticket.
3. Populate section `abbreviations` from the same map at parse where appropriate (schema alignment with ticket 03).
4. **`raw` unchanged**; expanded values in `input`/`output`/`env`/`exception`.
5. Unmapped tokens: leave literal; do not set `status: skipped`.
6. Re-run full inventory; record before/after for `unknown_character` subscript tokens.

Implement resolver and lookup in `src/conlanger/tools/` alongside `IndexDiachronicaParser`. **Do not use `legacy/`** — previous attempts only; no copying from `legacy/scripts/` or `legacy/data/`.

## Target cluster

`unknown_character` — subscript digits `₁`, `₀`, `₂`, `₃`, … (~100+ rules in current inventory summary)

## Acceptance criteria

- [ ] Parse-time expansion wired in `IndexDiachronicaParser` (not compile layer)
- [ ] Maps loaded from HTML-derived package CSV (ticket 28)
- [ ] `raw` preserves Index subscripts; corpus fields expanded when mapped
- [ ] Unmapped tokens left literal; no pre-emptive `status: skipped`
- [ ] Unit tests on representative mapped sections (e.g. Afro-Asiatic) and collective (`Hₓ`) where rows exist
- [ ] Full inventory re-run; before/after metrics in ticket **Answer**
- [ ] Fixtures updated for intentionally changed validation outcomes
- [ ] No imports from or dependencies on `legacy/`

## Blocked by

- [Extract correspondence-series mappings from Index Diachronica HTML](28-extract-correspondence-series-mappings-from-html.md)
