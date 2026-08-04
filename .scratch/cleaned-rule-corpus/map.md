wayfinder:map

# Cleaned rule corpus SoT

## Destination

A **cleaned rule corpus** (applier-neutral YAML SoT) derived from **Index Diachronica HTML**, where **corpus rules** **compile** to valid ASCA — with **historical fidelity** and a scalable correction workflow. See `CONTEXT.md`.

## Notes

- Glossary: `CONTEXT.md`. Decisions: ADRs 0001–0010.
- Skills: `/research`, `/grill-with-docs` or grilling + domain-modeling, `/prototype` if needed.
- Tracker: `docs/agents/issue-tracker.md` (Wayfinding operations).

## Decisions so far

- [What counts as a valid ASCA rule string?](issues/01-valid-asca-rule-string.md) — ASCA form is `input ARROW output [/env] [|exception]`; non-empty I/O (`*`/`∅` insert/delete, `&`/`@` metathesis); one `_` focus in env; `#` env-peripheral only; prefer `ParsedRules::try_from` (asca **0.10.2**). Findings: [research/asca-rule-validity.md](research/asca-rule-validity.md) (incl. internal parse pipeline for Python).
- [YAML schema for the cleaned rule corpus](issues/03-yaml-schema-cleaned-rule-corpus.md) — Top-level `abbreviations` + `sections`; rules carry `input`/`output`/`raw`/`source` (optional `env`/`exception`/`status`); ID-shaped strings; hierarchical string→string abbreviation tables; multi-line `raw` via `\|`; HTML SoT `index_diachronica_original.html` via lxml. (`status` amends earlier `skipped` — see fidelity ticket.)
- [Inventory which current rules compile and which fail](issues/02-inventory-valid-vs-invalid-rules.md) — Provisional AI YAML: 9721 rules → 5554 ok / 4167 fail under `asca 0.9.3`; CSV + summary in [inventory/](inventory/).
- [Create an ASCA validator for SoundChangeRuleSet](issues/08-asca-validator.md) — `validate_asca` via asca **0.10.2** `run` (raises `ASCAValidationError`); 500 `asca_guess` fixture rows (seed 20260802; 370 ok / 130 expected fail).
- [Historical fidelity vs valid-but-inaccurate fallback](issues/04-historical-fidelity-vs-validity.md) — Edit ladder + **rule status** / **validation report** split. ADR-0010.
- [Correction workflow for invalid rules](issues/05-correction-workflow-invalid-rules.md) — Regen YAML, per-**corpus rule** **compile validation**, cluster **failure classes**. ADR-0010.
- [Normalise segment feature matrices for appliers](issues/07-normalise-segment-features.md) — **Feature matrix** synonyms at ingest → `feature_mappings.csv`. Whitespace deferred.
- [Resolve abbreviations unsupported by ASCA and Brassica](issues/06-resolve-applier-unsupported-abbreviations.md) — **PhonologicalRuleSet** + **class letter** mappings; **symbol** ingest norm; cluster-driven deferrals.
- [Spike: ASCA feature-matrix expansions for Index class letters](issues/09-spike-asca-class-letter-feature-matrices.md) — `group_mappings.csv` validated. [research/asca-class-letter-mappings.md](research/asca-class-letter-mappings.md).

## Implementation plan (tickets 11+)

Phased delivery — not vertical slices upfront:

1. **[Minimal extract-only ingest](issues/11-minimal-extract-only-ingest.md)** — four rule parts + **Symbol** normalization only; no class letters, features, or compile transforms.
2. **[Full-corpus validation inventory](issues/12-full-corpus-validation-inventory.md)** — every **corpus rule** through `validate_asca` (ASCA 0.10.2); validation report CSV + clustered failure-class summary.
3. **[Correction passes](issues/13-correction-pass-template.md)** — cluster-driven iterations (parsing fixes and/or feature additions); re-run inventory after each pass until adoption criteria met.

**Compile validation:** use ASCA directly (`validate_asca` / `asca run` + baseline wordlist). Rule-derived candidate generation ([ticket 10](issues/10-rule-derived-probe-synthesis.md)) — **wontfix**.

## Not yet specified

- **Whitespace tokenisation for ASCA** — inter-segment spacing (deferred from ticket 07)
- **Meta-notation at ingest** — later find/replace; cluster-driven for now (ticket 06)
- **Series indices** and section-local prose abbreviations — cluster-driven; hand-add mapping rows when warranted
- Abbreviation table authorship at scale
- Prose-**environment** mapping
- Adoption criteria for cleaned YAML replacing HTML as **SoT**
- Brassica compiler (ADR-0001)
- Edge-split policy (ADR-0005; interim **skipped**)
- External one-off rule override schema

## Out of scope

- Generative sound-change *sequences* model — see [Generative sound-change sequences (GAN or next-in-sequence)](../sound-change-sequences/issues/01-generative-sound-change-sequences.md)
- Bundle ~100 preset inventories — [Bundle ~100 pre-generated phoneme inventories](../phoneme-inventories/issues/01-bundle-100-pregenerated-inventories.md)
- Automate PHOIBLE/WALS prep — [Automate PHOIBLE and WALS data preparation pipeline](../data-processing-pipeline/issues/01-automate-phoible-wals-prep.md)
- Full Brassica adoption / shipping a Brassica compiler
