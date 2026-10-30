Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: feature_mappings.csv schema and Index matrix → ASCA targets.
Result: [0038-index-feature-matrices-to-asca-targets.md](../spikes/0038-index-feature-matrices-to-asca-targets.md)
Blocked by:

## Question

For high-volume **`unknown_feature`** tokens in the validation inventory (251 rules; 39 distinct matrix feature names), how should Index **feature matrix** names inside `[...]` map to ASCA — single feature shorthands, multi-feature bundles, or “unrepresentable without rule rewrite” — and what **`feature_mappings.csv`** schema is needed beyond ticket 07’s 1:1 synonym assumption?

## Answer

Findings: [research/index-feature-matrices-to-asca-targets.md](../spikes/index-feature-matrices-to-asca-targets.md).

- **~32%** of failures (`voiced`, `stressed`, `sibilant→strident`) are high-confidence **rename** rows; **~32%** are **place bundles** (`dental`, `alveolar`, `palatal`, `velar`, `uvular`); **~35%** **defer** (tone, lenis/fortis, syllable open/closed, `sameC`, `AP`, etc.).
- **`feature_mappings.csv`** lives at `data/asca/feature_mappings.csv` (not `src/conlanger/data/asca/`). Schema extends ticket 07 with `mapping_kind`, optional `host`, `confidence`; **`asca_target` may be a multi-feature bundle**.
- Seed CSV block (10 rows) in findings; correction pass should start with `voiced` only per prior assessment, then add bundle support before place labels.
