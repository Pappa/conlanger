Type: task
Status: done
Blocked by: None

# Extract correspondence-series mappings from Index Diachronica HTML

## Question

Where do per-section **correspondence-series** and **collective subscript** expansions come from — and how are they authored as package data for parse-time resolution?

## Notes

- Policy: [Parse-time resolution for correspondence-series indices](26-parse-time-correspondence-series-indices.md); ADR [0004](../../../docs/adr/0004-series-indices-per-section-maps.md).
- **Do not use `legacy/`** — previous attempts only. Implement from **`data/diachronica/`** (HTML SoT and reference files) and **`data/asca/`** (runtime CSV mappings, alongside `group_mappings.csv`), plus `src/conlanger/` code.
- **Source of truth for map rows:** `data/diachronica/index_diachronica_original.html` — section citations, phonology tables, and other prose that defines what indexed tokens (e.g. `s₁`, `h₂`, `Hₓ`) denote in that section family. See also `data/diachronica/sound_change_abbreviations.txt` for global Index key.
- Glossary: `CONTEXT.md` — **Correspondence-series index**, **Correspondence series**, **Collective subscript** (not **positional slot** / **identity subscript**).
- Cross-check: ~210 corpus rules carry subscripts; [inventory summary](../inventory/asca-rule-inventory-summary.md) `unknown_character` for `₁`, `₀`, `₂`, `₃`.
- Examples in HTML:
  - Afro-Asiatic citation: `s₁, s₂, s₃, h₁, h₂` as fricatives (`index_diachronica_original.html` ~933).
  - Laryngeal series in tables (PIE `h₁ h₂ h₃` rows).
  - Output-side disambiguation: `s₁ s₂ s₃ → ʃ z tʃ` (Aari) implies series member → segment mappings inferable from rule context where citation is silent.
- Follow-on: [Implement parse-time correspondence-series expansion](27-implement-parse-time-correspondence-series-expansion.md).

## What to build

1. **Survey** HTML for sections using **correspondence-series indices** / **collective subscripts** (not positional `C₁` / identity `V₀`).
2. **Extract** section-scoped token → ASCA-parseable target mappings into **`data/asca/series_mappings.csv`** (same tree as `group_mappings.csv`) with columns at minimum: `section_index`, `token`, `asca_target`; optional `source` (`file:line`), `notes`.
3. **Hierarchical lookup:** longest-prefix section match; optional global `*` fallback only where Index key defines a family-wide default.
4. **Infer** mappings from rule I/O where section prose lists series members but does not give IPA (e.g. chain `s₁ s₂ s₃ → ʃ z tʃ`) — document inference method; prefer explicit citation over guess; leave unmapped when ambiguous.
5. Emit **coverage report** (sections with subscript rules vs rows authored; unmapped tokens list) under `.scratch/cleaned-rule-corpus/` for later correction passes.

## Acceptance criteria

- [x] `series_mappings.csv` (or equivalent) populated from HTML evidence only
- [x] Coverage report lists mapped vs unmapped tokens by section
- [x] At least Afro-Asiatic (`6.x`) and one laryngeal-series family covered with cited HTML sources
- [x] No imports, copies, or references to `legacy/` in new code or data artifacts
- [x] Unit tests on extraction helpers where logic is non-trivial

## Deliverables

- `data/asca/series_mappings.csv` — 60 rows from HTML citations, inventory tables, and rule I/O inference
- `src/conlanger/tools/series_mappings.py` — extraction, lookup, audit, coverage report
- `scripts/extract_series_mappings.py` — regenerate CSV + report
- `tests/conlanger/tools/test_series_mappings.py` — 34 unit tests
- `.scratch/cleaned-rule-corpus/series-mappings-coverage.md` — coverage report (77.2% in-scope rule tokens mapped)
- `.scratch/cleaned-rule-corpus/series-mappings-coverage-backlog.md` — follow-up backlog

## Follow-up (optional)

Coverage baseline and backlog for raising in-scope rule coverage beyond ~77%: [series-mappings-coverage-backlog.md](../series-mappings-coverage-backlog.md).
