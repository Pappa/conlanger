wayfinder:map

# Cleaned rule corpus SoT

## Destination

A **cleaned rule corpus** (applier-neutral YAML SoT) derived from **Index Diachronica HTML**, where **corpus rules** **compile** to valid ASCA — with **historical fidelity** and a scalable correction workflow. See `CONTEXT.md`.

## Notes

- Glossary: `CONTEXT.md` — **Subscript notation** (four uses: correspondence-series index, positional slot, identity subscript, collective subscript). Decisions: ADRs 0001–0010.
- Skills: `/research`, `/grill-with-docs` or grilling + domain-modeling, `/prototype` if needed.
- **`data/` folder:** project data tree — use for reference **and** implementation. Index Diachronica HTML SoT: `data/diachronica/index_diachronica_original.html`; regenerated corpus YAML: `data/diachronica/index_diachronica_parsed.yml`; runtime CSV mappings: `data/asca/` (e.g. `group_mappings.csv`).
- **`src/conlanger/`:** parser, compile, validation, and orchestration code.
- **`legacy/` folder:** previous attempts only — do **not** copy code or data from `legacy/` when implementing cleaned-corpus work (tickets 11+).
- Tracker: `docs/agents/issue-tracker.md` (Wayfinding operations).

## Decisions so far

- [What counts as a valid ASCA rule string?](issues/01-valid-asca-rule-string.md) — ASCA form is `input ARROW output [/env] [|exception]`; non-empty I/O (`*`/`∅` insert/delete, `&`/`@` metathesis); one `_` focus in env; `#` env-peripheral only; prefer `ParsedRules::try_from` (asca **0.10.2**). Findings: [research/asca-rule-validity.md](research/asca-rule-validity.md) (incl. internal parse pipeline for Python).
- [YAML schema for the cleaned rule corpus](issues/03-yaml-schema-cleaned-rule-corpus.md) — Top-level `abbreviations` + `sections`; rules carry `input`/`output`/`raw`/`source` (optional `env`/`exception`/`status`/`sporadic`/`comment`); ID-shaped strings; hierarchical string→string abbreviation tables; multi-line `raw` via `\|`; HTML SoT `index_diachronica_original.html` via lxml.
- [Inventory which current rules compile and which fail](issues/02-inventory-valid-vs-invalid-rules.md) — Provisional AI YAML: 9721 rules → 5554 ok / 4167 fail under `asca 0.9.3`; CSV + summary in [inventory/](inventory/).
- [Create an ASCA validator for SoundChangeRuleSet](issues/08-asca-validator.md) — `validate_asca` via asca **0.10.2** `run` (raises `ASCAValidationError`); 500 `asca_guess` fixture rows (seed 20260802; 370 ok / 130 expected fail).
- [Historical fidelity vs valid-but-inaccurate fallback](issues/04-historical-fidelity-vs-validity.md) — Edit ladder + **rule status** / **validation report** split. ADR-0010.
- [Correction workflow for invalid rules](issues/05-correction-workflow-invalid-rules.md) — Regen YAML, per-**corpus rule** **compile validation**, cluster **failure classes**. ADR-0010.
- [Normalise segment feature matrices for appliers](issues/07-normalise-segment-features.md) — **Feature matrix** synonyms at ingest → `feature_mappings.csv`. Whitespace deferred.
- [Resolve abbreviations unsupported by ASCA and Brassica](issues/06-resolve-applier-unsupported-abbreviations.md) — **PhonologicalRuleSet** + **class letter** mappings; **symbol** ingest norm; cluster-driven deferrals.
- [Spike: ASCA feature-matrix expansions for Index class letters](issues/09-spike-asca-class-letter-feature-matrices.md) — `group_mappings.csv` validated. [research/asca-class-letter-mappings.md](research/asca-class-letter-mappings.md).
- [Spike: Index feature matrices → ASCA targets](issues/29-spike-index-feature-matrices-to-asca-targets.md) — `feature_mappings.csv` schema + seed rows. [research/index-feature-matrices-to-asca-targets.md](research/index-feature-matrices-to-asca-targets.md).
- [Rule-derived probe synthesis for compile validation](issues/10-rule-derived-probe-synthesis.md) — **wontfix**; baseline wordlist (`asca_probe_words.wsca`) via `validate_asca` is sufficient for clustering (~98% failures are Tier 1–2 syntax).
- [Minimal extract-only ingest](issues/11-minimal-extract-only-ingest.md) — `IndexDiachronicaParser` → applier-neutral YAML (`data/diachronica/index_diachronica_parsed.yml`); **Symbol** norm + parse-time class-first fixes (em dash, arrows, chain split, glosses, stress, `sporadic`); class letters deferred to compile.
- [Full-corpus validation inventory](issues/12-full-corpus-validation-inventory.md) — `uv run regenerate_corpus`; per-rule CSV + summary under [inventory/](inventory/). Current baseline: **6422 / 9317 ok (68.9%)** on ASCA 0.10.2.
- [Correction pass (cluster-driven)](issues/13-correction-pass-template.md) — standing recipe; instances are tickets 14–25 (and onward).
- [Correction pass: unknown_grouping (class letters at compile)](issues/14-correction-pass-unknown-grouping.md) — `PhonologicalRuleSet` + `group_mappings.csv` at compile; ~59% of cluster passes outright.
- [Correction pass: unknown_character — length marker ː](issues/15-correction-pass-length-marker.md) — compile `normalize_asca_length_marks()`; ~52% of cluster passes.
- [Correction pass: unknown_character — em dash —](issues/16-correction-pass-em-dash.md) — parse-time leading list-marker strip.
- [Correction pass: unknown_character — rule arrow →](issues/17-correction-pass-arrow.md) — parse-time `→` → `>` in field values after primary split.
- [Correction pass: chained rules — parse-time split](issues/18-correction-pass-chain-split.md) — chains without env/exception expand to sequential corpus rules (row count increases).
- [Correction pass: uncertainty glosses — sporadic / sometimes](issues/19-correction-pass-sporadic-qualifier.md) — strip gloss; set `sporadic: true` (187 rules).
- [Correction pass: ejective marker ʼ](issues/20-correction-pass-ejective-marks.md) — compile `normalize_asca_ejective_marks()` → `[+cg]`.
- [Correction pass: trailing bracket / quote glosses](issues/21-correction-pass-trailing-glosses.md) — parse-time editorial prose strip.
- [Correction pass: when stressed / when unstressed env conditions](issues/22-correction-pass-stress-conditions.md) — parse-time env stress-phrase normalization.
- [Correction pass: labialized Index class letters (Kʷ, K(ʷ), …)](issues/23-correction-pass-labialized-class-letters.md) — compile labialization on class letters.
- [Correction pass: smart quotes and typographic apostrophes](issues/24-correction-pass-smart-quotes.md) — parse + compile quote/apostrophe cleanup.
- [Correction pass: remaining bare length marker ː](issues/25-correction-pass-bare-length-marker.md) — extended length-mark compile pass; `ː` cluster 242 → 40.
- [Parse-time resolution for correspondence-series indices](issues/26-parse-time-correspondence-series-indices.md) — expand at HTML→YAML parse to ASCA-parseable strings when section map exists; `raw` retains subscripts; unmapped → literal + validation fail (no pre-emptive skip). ADR-0004 amended.
- [Rule comment field on corpus rules](issues/30-rule-comment-field-on-corpus-rules.md) — optional `comment` on corpus rules; capture-not-discard prose stripped at parse (semicolon tails, glosses, env qualifiers); distinct from section `comments`.
- [Spike: field-isolation compile validation](issues/35-spike-field-isolation-compile-validation.md) — **go-with-limits**: canned/shape-aware stubs + `validate_asca`/baseline wordlist attribute most Tier 1–2 fails; whole-rule `ok` stays SoT; fails-only sidecar + `blame`; no probe synthesis. Findings: [research/field-isolation-compile-validation.md](research/field-isolation-compile-validation.md). Follow-on: [Field-isolation inventory sidecar](issues/36-field-isolation-inventory-sidecar.md).
- [Inventory success/error CSV splits and ok-change changelog](issues/34-inventory-success-error-splits-and-ok-changelog.md) — regen writes success/error filtered CSVs + append-only `ok`-flip changelog (match by `source`); summary links new artifacts.
- [Document the sound-change rule pipeline in docs/](issues/37-document-sound-change-pipeline.md) — **grill 2026-08-07:** four `docs/` pages + `SYSTEM.md` **Pipeline stages (legacy)** / **(new)**; applier compile table (implemented order + planned `TBD` rows); parse / validation / applier docs split; compile validation lives in applier doc; no ADR for transform order.
- [Spike: ASCA compile transform ordering (planned steps)](issues/38-spike-asca-compile-transform-order.md) — done. Findings: [research/asca-compile-transform-order.md](research/asca-compile-transform-order.md). Orders 3–4 before group mappings; 10 meta cluster-last.
- [Refactor SoundChangeRuleSet and compile subcomponents](issues/39-refactor-sound-change-ruleset.md) — **blocked by 37**; scope TBD until docs land.

## Pipeline documentation (grill 2026-08-07)

**Runtime:** parse once → correction loop; each pass runs applier compile → compile validation per rule (ADR-0003). Operator command: `uv run regenerate_corpus` (rename deferred).

**Docs (two processing steps, ad hoc — no ticket):**

| SYSTEM.md row | Target doc |
| --- | --- |
| Index Diachronica ingest | `docs/index-diachronica-ingest.md` (merge parser + corpus-validation) |
| Sound change rule compilation | `docs/sound-change-rule-compilation.md` (rename from `sound-change-applier.md`) |

Delete superseded doc paths; fix all links. Transform order in compilation doc only. Refactor `SoundChangeRuleSet` → [ticket 39](issues/39-refactor-sound-change-ruleset.md).

## Implementation plan (tickets 11+)

Phased delivery — not vertical slices upfront:

1. ~~**[Minimal extract-only ingest](issues/11-minimal-extract-only-ingest.md)**~~ — done (parse path also gained class-first fixes from passes 14–25).
2. ~~**[Full-corpus validation inventory](issues/12-full-corpus-validation-inventory.md)**~~ — done; re-run after each correction pass.
3. **[Correction passes](issues/13-correction-pass-template.md)** — in progress via [14–25](issues/14-correction-pass-unknown-grouping.md). ~~[Extract correspondence-series mappings from Index Diachronica HTML](issues/28-extract-correspondence-series-mappings-from-html.md)~~ done → [Implement parse-time correspondence-series expansion](issues/27-implement-parse-time-correspondence-series-expansion.md). Coverage follow-ups: [series-mappings-coverage-backlog.md](series-mappings-coverage-backlog.md). ~~[Spike: Index feature matrices → ASCA targets](issues/29-spike-index-feature-matrices-to-asca-targets.md)~~ done → ~~[Correction pass: unknown_feature Phase 1](issues/32-correction-pass-unknown-feature.md)~~ done (renames + `short`→`-long`); Phase 2 place bundles open.
4. **Validation confidence (2026-08 charted):** ~~[Inventory success/error CSV splits and ok-change changelog](issues/34-inventory-success-error-splits-and-ok-changelog.md)~~ done; next [Field-isolation inventory sidecar](issues/36-field-isolation-inventory-sidecar.md) (spike done). Open cluster work: [Debug / fix: Index `same POA`](issues/33-debug-same-poa-feature-artefact.md); ~~[Correction pass: positional slots and identity subscripts](issues/40-correction-pass-positional-identity-subscripts.md)~~ phase 1 done (+51 ok) → [Correction pass: subscript edge cases (phase 2)](issues/41-correction-pass-subscript-edge-cases.md). ~~[Compile-time chain expansion](../adr-0005-no-ingest-split/issues/03-compile-time-chain-expansion.md)~~ done (+132 ok).

**Compile validation:** use ASCA directly (`validate_asca` / `asca run` + baseline wordlist). Rule-derived candidate generation ([ticket 10](issues/10-rule-derived-probe-synthesis.md)) — **wontfix**. Field-isolation (if adopted) must stay inside that boundary.

## Not yet specified

- **Bare I/O “already good” tagging** — optional idea: for rules with only `input`/`output` (no `env`/`exception`/`comment`), try Index `raw` with arrow normalised to ASCA `>` and see if ASCA accepts; tag as not needing transforms. Left foggy on purpose (grill Q5); full-rule `ok` + [ok-change changelog](issues/34-inventory-success-error-splits-and-ok-changelog.md) may already cover regression guarding. Revisit after 34/35.
- **Subscript notation (all four uses)** — grilled + researched: [subscript-notation-index-asca-brassica.md](research/subscript-notation-index-asca-brassica.md), [positional-slots-and-identity-subscripts.md](research/positional-slots-and-identity-subscripts.md). **Working policy:** correspondence-series + collective → **parse-time**; positional + identity → **compile-time** (Index-shaped in YAML). **Phase 1:** [Correction pass: positional slots and identity subscripts](issues/40-correction-pass-positional-identity-subscripts.md) (+51 ok). **Phase 2:** [Correction pass: subscript edge cases](issues/41-correction-pass-subscript-edge-cases.md). **Compile order:** [research/asca-compile-transform-order.md](research/asca-compile-transform-order.md).
- **Whitespace tokenisation for ASCA** — inter-segment spacing (deferred from ticket 07)
- **Meta-notation at ingest** — later find/replace; cluster-driven for now (ticket 06)
- **Section-local abbreviations** (e.g. Athabaskan `TŠ`) — cluster-driven; hand-add mapping rows when warranted
- Abbreviation table authorship at scale
- Prose-**environment** mapping — informed by extracted **`comment`** qualifiers ([Capture rule comments at parse time](issues/31-capture-rule-comments-at-parse-time.md)); structured env from prose not yet specified
- Adoption criteria for cleaned YAML replacing HTML as **SoT**
- Brassica compiler (ADR-0001)
- Edge-split policy (ADR-0005; **`status: skipped` deferred** until post-correction triage per ticket 26 / ADR-0010)
- External one-off rule override schema

## Out of scope

- Generative sound-change *sequences* model — see [Generative sound-change sequences (GAN or next-in-sequence)](../sound-change-sequences/issues/01-generative-sound-change-sequences.md)
- Bundle ~100 preset inventories — [Bundle ~100 pre-generated phoneme inventories](../phoneme-inventories/issues/01-bundle-100-pregenerated-inventories.md)
- Automate PHOIBLE/WALS prep — [Automate PHOIBLE and WALS data preparation pipeline](../data-processing-pipeline/issues/01-automate-phoible-wals-prep.md)
- Full Brassica adoption / shipping a Brassica compiler
