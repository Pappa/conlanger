Type: spike
Status: resolved
Blocked by: 06

# Spike: ASCA feature-matrix expansions for Index class letters

## Question

For Index class letters whose meaning diverges from ASCA inbuilt groupings (e.g. `R` resonant, `Q` uvular/click, `M` diphthong, `H` laryngeal, `J` approximant), what ASCA feature-matrix or grouping strings correctly express the Index intent — and which rows in `data/asca/group_mappings.csv` should be updated?

## Notes

- Resolve with `/research` against ASCA 0.10.2 docs and inventory failure clusters.
- Current `group_mappings.csv` rows are best-guess placeholders; this spike replaces them with validated expansions where possible.
- Out of scope: series indices, section-local prose conventions (Athabaskan `TŠ`, etc.), meta-notation — those stay validation-cluster driven per ticket 06.

## Answer

Findings: [research/asca-class-letter-mappings.md](../research/asca-class-letter-mappings.md)

### Summary

- **Six letters omit from CSV** — **C, O, F, L, N, V** align with ASCA inbuilt groupings; pass through unchanged.
- **Seventeen rows updated** in `data/asca/group_mappings.csv` — key changes: **A** → `O:[+delrel]`; **J** → `{L,G}`; **K**/**Ḱ** → `C:`-hosted matrices; **Q** → uvular ∪ click set; **R** → `[+son,-syll]`; **Z** → `[+cont]`.
- **M (diphthong) removed** — no faithful ASCA class; handle via validation clusters.

### Implementation note

Current `IndexDiachronicaParser.apply_group_mappings` still uses `str.maketrans` (single-char, one pass). Expansions containing nested letters (e.g. `{L,G}`) are not re-translated — documented in research. Runtime `DiachronicSeries` may replace this.
