Type: task
Status: ready-for-agent
Blocked by: 26

# Implement parse-time correspondence-series expansion

## What to build

Apply [Parse-time resolution for correspondence-series indices](26-parse-time-correspondence-series-indices.md) in `IndexDiachronicaParser`:

1. Load per-section correspondence-series maps (migrate seed data from `legacy/data/series_mapping.yaml` into package data under `src/conlanger/data/`, e.g. `series_mappings.csv` with section-index column + token + ASCA target).
2. After existing parse-time transforms (symbols, glosses, stress, …), run `resolve_correspondence_series()` on corpus field values — **correspondence-series index** and **collective subscript** tokens only; do not expand **positional slots** or **identity subscripts** in this ticket.
3. Merge extracted mappings from section **citation** prose into section `abbreviations` where safe (Afro-Asiatic `s₁`–`s₃` pattern); hand-authored CSV rows for the rest.
4. **`raw` unchanged**; expanded values in `input`/`output`/`env`/`exception`.
5. Unmapped tokens: leave literal; do not set `status: skipped`.
6. Re-run full inventory; record before/after for `unknown_character` tokens `₁`, `₀`, `₂`, `₃` and correspondence-series examples.

Prior art: `legacy/scripts/parse_index_diachronica.py` — `resolve_series_labels()`, `effective_series_map()`, `SERIES_TOKEN_RE`.

## Target cluster

`unknown_character` — subscript digits `₁`, `₀`, `₂`, `₃`, … (~100+ rules in current inventory summary)

## Acceptance criteria

- [ ] Parse-time expansion wired in `IndexDiachronicaParser` (not compile layer)
- [ ] Seed mapping file under `src/conlanger/data/` with legacy YAML migrated
- [ ] `raw` preserves Index subscripts; corpus fields expanded when mapped
- [ ] Unmapped tokens left literal; no pre-emptive `status: skipped`
- [ ] Unit tests on representative Afro-Asiatic and collective (`sₓ` / `Hₓ`) cases
- [ ] Full inventory re-run; before/after metrics in ticket **Answer**
- [ ] Fixtures updated for intentionally changed validation outcomes

## Blocked by

- [Parse-time resolution for correspondence-series indices](26-parse-time-correspondence-series-indices.md)
