Type: task
Status: resolved
Blocked by: 11

# Full-corpus validation inventory

## What to build

Run every **corpus rule** from extract-only cleaned YAML through ASCA **compile validation** and produce a recorded inventory for clustering and iterative correction.

Pipeline per rule: corpus rule dict → `DiachronicSeries` → `validate_asca` (existing `src/conlanger/tools/asca_validator.py`, driving installed **asca 0.10.2** via `asca run`). Use the baseline wordlist (`tests/fixtures/asca_probe_words.wsca` or equivalent fixed lexicon) — no rule-derived candidate generator.

Deliver a single invocable entry point (script or module) that takes an HTML path and emits:

1. Regenerated cleaned YAML (from ticket 11 ingest)
2. Validation report CSV per **corpus rule**: section identity, rule index, ok/fail, **failure class**, reason, description
3. Inventory summary (total rules, ok/fail counts and percentages, top **failure classes** ranked by count)

Re-baseline against cleaned schema + ASCA 0.10.2, replacing the provisional 0.9.3 / `index_diachronica_ai.yml` inventory in `.scratch/cleaned-rule-corpus/inventory/`.

## Notes

- Validation is post-extract only — no compile-layer transforms beyond what `DiachronicSeries` already renders from corpus fields.
- Tier 4 runtime failures may be under-detected when the baseline wordlist does not match a rule's shape; acceptable for this inventory pass (~98% of provisional failures are Tier 1–2 syntax). Revisit only if clustering shows a Tier 4 cluster worth targeting later.
- Does **not** implement parser/compiler fixes — measures only. Correction passes (ticket 13+) are filed after reviewing the clustered output.
- Skip gracefully when `asca` 0.10.2 binary is absent (match existing validator test pattern).

## Blocked by

- [Minimal extract-only ingest](11-minimal-extract-only-ingest.md)

## Acceptance criteria

- [x] One command regenerates cleaned YAML + validation report CSV + summary markdown from HTML path
- [x] CSV columns include section identity, rule index, ok/fail, failure class, reason, description
- [x] Summary records rule counts, ok/fail percentages, and top failure classes (reproducible across runs)
- [x] Inventory artifacts written under `.scratch/cleaned-rule-corpus/inventory/`
- [x] Per-**corpus rule** validation — one bad rule in a section does not obscure others

## Answer

Entry point: `uv run regenerate_corpus` (`src/conlanger/scripts/regenerate_corpus.py`).

Inventory module: `src/conlanger/tools/corpus_inventory.py` — per-rule validation via `PhonologicalRuleSet(...).to_sound_change_ruleset()` + `validate_asca` (ASCA 0.10.2, baseline `tests/fixtures/asca_probe_words.wsca`).

Artifacts: `.scratch/cleaned-rule-corpus/inventory/asca-rule-inventory.csv` and `asca-rule-inventory-summary.md`.

Latest baseline (after passes 14–25): **6422 / 9317 ok (68.9%)**; top failure classes: `syntax_other`, `unknown_character`, `expected_underscore`, `unknown_feature`. Replaces provisional 0.9.3 / `index_diachronica_ai.yml` inventory.
