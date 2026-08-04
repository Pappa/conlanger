Type: grilling
Status: resolved
Blocked by: 01, 03, 04

# Resolve abbreviations unsupported by ASCA and Brassica

## Question

Which Index Diachronica abbreviations (class letters, series indices, other shorthand) cannot be expressed under ASCA and/or Brassica, and what concrete expansions or corpus treatments should replace them so compilers can emit valid applier input?

## Notes

- Skills: `/research` for ASCA/Brassica support surfaces; `/grill-with-docs` (or grilling + domain-modeling) for which expansions / `skipped` treatments to adopt.
- Honor [Historical fidelity vs valid-but-inaccurate fallback](04-historical-fidelity-vs-validity.md).
- Evidence: `data/diachronica/sound_change_abbreviations.txt`, `index_diachronica_original.html`, [01-valid-asca-rule-string](01-valid-asca-rule-string.md).

## Answer

Domain terms: **Class letter**, **Symbol**, **Meta-notation**, **PhonologicalRuleSet**, **Abbreviation table**, **Failure class**, **Series index**, **Correspondence series** — see `CONTEXT.md`.

### Decisions

- **No validation-first filtering** — apply mappings, throw at ASCA, fix top **failure classes** each cycle ([Correction workflow](05-correction-workflow-invalid-rules.md)).
- **Class letters** at compile/runtime: **PhonologicalRuleSet** loads `data/asca/group_mappings.csv`, passes mappings to the transformer; unmapped tokens stay as-is. Retire ingest `str.maketrans`.
- **Symbols** at HTML→YAML ingest (distinct from class letters; see ticket 07 for **Feature matrix**).
- HTML provides a **global Key to Abbreviations** only — section-local prose (Athabaskan `TŠ`, etc.): **failure class** clusters; hand-add rows when warranted; no prose-extraction spike.
- **Deferred (cluster-driven):** **series indices**, **meta-notation**, section-local tokens.
- **Brassica:** deferred (`src/conlanger/data/brassica/`).
- **Follow-on:** [Spike 09](09-spike-asca-class-letter-feature-matrices.md) (done); implement **PhonologicalRuleSet**.
