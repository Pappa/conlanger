Type: spike
Status: resolved
Blocked by: None

# Spike: Index feature matrices → ASCA targets

## Question

For high-volume **`unknown_feature`** tokens in the validation inventory (251 rules; 39 distinct matrix feature names), how should Index **feature matrix** names inside `[...]` map to ASCA — single feature shorthands, multi-feature bundles, or “unrepresentable without rule rewrite” — and what **`feature_mappings.csv`** schema is needed beyond ticket 07’s 1:1 synonym assumption?

## Notes

- Policy: [Normalise segment feature matrices for appliers](07-normalise-segment-features.md) — ingest normalisation inside `[...]` only; `raw` unchanged; unmapped → validation fail (ADR-0010).
- Baseline triage: [research/unknown-feature-suggestions-assessment.md](../research/unknown-feature-suggestions-assessment.md) — Levenshtein “Did you mean …?” hints are **not** authoritative; only ~25% of failures have acceptable suggestions.
- Inventory: [rule-inventory-summary.md](../inventory/rule-inventory-summary.md) — full `unknown_feature` token list with ASCA suggestions.
- **Primary ASCA sources (0.10.2):**
  - [`src/diacritics.json`](https://raw.githubusercontent.com/Girv98/asca-rust/36c3c623fb9f501a358ae087764e77b92d0037bf/src/diacritics.json) — named categories → distinctive-feature **payloads** (voiced, glottalized, palatalised, strident, …).
  - [Feature shorthands](https://github.com/Girv98/asca-rust/0.10.2/doc/doc.md#feature-shorthands) — accepted matrix feature names.
  - [Segment features / feature tree](https://github.com/Girv98/asca-rust/0.10.2/doc/doc.md#segment-features) — coronal/dorsal/laryngeal decomposition for place labels (`dental`, `velar`, …).
- **Scope boundary:** failures are **matrix feature names** (`[+voiced]`, `[+sibilant]`), not IPA segment diacritics. `diacritics.json` informs semantic targets; corrections still rewrite matrix syntax unless a separate segment-diacritic cluster appears.
- Related: [Spike: ASCA feature-matrix expansions for Index class letters](09-spike-asca-class-letter-feature-matrices.md) (`group_mappings.csv`); [Correction pass: ejective marker ʼ](20-correction-pass-ejective-marks.md) (`[+cg]`).
- Resolve with `/research`; output a findings markdown under `research/` and a proposed `feature_mappings.csv` seed (high-confidence rows only).

## Mapping kinds to classify (expected)

1. **Rename** — Index shorthand → ASCA shorthand (e.g. `voiced` → `voice`).
2. **Different shorthand** — same node, different label (e.g. `sibilant` → `strident`).
3. **Feature bundle** — Index place/manner → ASCA matrix (e.g. coronal place labels → `[+anterior,…]`).
4. **Defer** — suprasegmental Index labels (`hightone`, `lowtone`, …), lenis/fortis, co-reference (`sameC`), section-local (`AP`, `RP`).

## Acceptance criteria

- [x] Every inventory `unknown_feature` token with count ≥ 3 classified into kinds 1–4 with cited ASCA source
- [x] Proposed `feature_mappings.csv` columns documented (whether `asca_target` may be a multi-feature matrix)
- [x] High-confidence seed rows listed separately from “needs spike / env rewrite” tail
- [x] Findings linked from this ticket; no implementation in parser/ingest (spike only)

## Answer

Findings: [research/index-feature-matrices-to-asca-targets.md](../research/index-feature-matrices-to-asca-targets.md).

- **~32%** of failures (`voiced`, `stressed`, `sibilant→strident`) are high-confidence **rename** rows; **~32%** are **place bundles** (`dental`, `alveolar`, `palatal`, `velar`, `uvular`); **~35%** **defer** (tone, lenis/fortis, syllable open/closed, `sameC`, `AP`, etc.).
- **`feature_mappings.csv`** lives at `data/asca/feature_mappings.csv` (not `src/conlanger/data/asca/`). Schema extends ticket 07 with `mapping_kind`, optional `host`, `confidence`; **`asca_target` may be a multi-feature bundle**.
- Seed CSV block (10 rows) in findings; correction pass should start with `voiced` only per prior assessment, then add bundle support before place labels.
