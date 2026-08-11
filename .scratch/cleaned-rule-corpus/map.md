wayfinder:map

# Cleaned rule corpus SoT

## Destination

A **cleaned rule corpus** (applier-neutral YAML SoT) derived from **Index Diachronica HTML**, where **corpus rules** **compile** to valid ASCA — with **historical fidelity** and a scalable correction workflow. See `CONTEXT.md`.

## Notes

- Glossary: `CONTEXT.md` — **Subscript notation** (four uses); **Stages**; **Optional outputs** (grill open). Decisions: ADRs 0001–0011.
- Skills: `/research`, `/grill-with-docs` or grilling + domain-modeling, `/prototype` if needed.
- **`data/` folder:** project data tree — use for reference **and** implementation. Index Diachronica HTML SoT: `data/diachronica/index_diachronica_original.html`; regenerated corpus YAML: `data/diachronica/index_diachronica_parsed.yml`; runtime ASCA mappings under `data/asca/` — **`group_mappings.csv`** (Index **class letters** at compile); **`asca_aliases.alias`** (word (de)romanisation via `asca -l` only — not rule grouping letters).
- **`src/conlanger/`:** parser, compile, validation, and orchestration code.
- **`legacy/` folder:** previous attempts only — do **not** copy code or data from `legacy/` when implementing cleaned-corpus work (tickets 11+).
- Tracker: `docs/agents/issue-tracker.md` (Wayfinding operations).

## Decisions so far

- [What counts as a valid ASCA rule string?](issues/01-valid-asca-rule-string.md) — ASCA form is `input ARROW output [/env] [|exception]`; non-empty I/O (`*`/`∅` insert/delete, `&`/`@` metathesis); one `_` focus in env; `#` env-peripheral only; prefer `ParsedRules::try_from` (asca **0.10.2**). Findings: [research/asca-rule-validity.md](research/asca-rule-validity.md) (incl. internal parse pipeline for Python).
- [Corpus rule `stages` schema cutover](issues/59-corpus-rule-stages-schema.md) — ADR-0011: uniform **`stages`** spine; compile expands adjacent pairs; `stages: []` + `status: skipped` hold-outs; regenerated `index_diachronica_parsed.yml`.
- [YAML schema for the cleaned rule corpus](issues/03-yaml-schema-cleaned-rule-corpus.md) — Top-level `abbreviations` + `sections`; rules carry **`stages`**/`raw`/`source` (optional `env`/`exception`/`status`/`sporadic`/`comment`) per [ADR-0011](../../docs/adr/0011-corpus-rule-stages.md) / [ticket 59](issues/59-corpus-rule-stages-schema.md) (supersedes stored `input`/`output`); hierarchical string→string abbreviation tables; multi-line `raw` via `\|`; HTML SoT `index_diachronica_original.html` via lxml.
- [Inventory which current rules compile and which fail](issues/02-inventory-valid-vs-invalid-rules.md) — Provisional AI YAML: 9721 rules → 5554 ok / 4167 fail under `asca 0.9.3`; CSV + summary in [inventory/](inventory/).
- [Create an ASCA validator for DiachronicSeries](issues/08-asca-validator.md) — `validate_asca` via asca **0.10.2** `run` (raises `ASCAValidationError`); 500 `asca_guess` fixture rows (seed 20260802; 370 ok / 130 expected fail).
- [Historical fidelity vs valid-but-inaccurate fallback](issues/04-historical-fidelity-vs-validity.md) — Edit ladder + **rule status** / **validation report** split. ADR-0010.
- [Correction workflow for invalid rules](issues/05-correction-workflow-invalid-rules.md) — Regen YAML, per-**corpus rule** **compile validation**, cluster **failure classes**. ADR-0010.
- [Normalise segment feature matrices for appliers](issues/07-normalise-segment-features.md) — **Feature matrix** synonyms at ingest → `feature_mappings.csv`. Inter-segment whitespace deferred here → resolved in [Spike: inter-segment whitespace and phoneme boundaries](issues/44-spike-inter-segment-whitespace.md).
- [Resolve abbreviations unsupported by ASCA and Brassica](issues/06-resolve-applier-unsupported-abbreviations.md) — **PhonologicalRuleSet** + **class letter** mappings; **symbol** ingest norm; cluster-driven deferrals.
- [Spike: ASCA feature-matrix expansions for Index class letters](issues/09-spike-asca-class-letter-feature-matrices.md) — `group_mappings.csv` validated. [research/asca-class-letter-mappings.md](research/asca-class-letter-mappings.md). Grill 2026-08-10: **do not** replace with ASCA `.alias` `-l` — see below.
- **Grill: ASCA alias file vs compile class-letter mappings** — grill 2026-08-10: **no-go** — ASCA `.alias` (`-l`) is word (de)romanisation only; rules parse without alias expansion; `@into` cannot express `{L,G}` / `{C:[…],[+click]}` rows. Keep **`group_mappings.csv`** + **`apply_asca_group_mappings`** at compile (bracket-safe, labialized class letters, positional slots). `data/asca/asca_aliases.alias` stays complementary (probe lexicon / output romanisation). Findings: [research/asca-alias-file-vs-group-mappings.md](research/asca-alias-file-vs-group-mappings.md).
- [Spike: Index feature matrices → ASCA targets](issues/29-spike-index-feature-matrices-to-asca-targets.md) — `feature_mappings.csv` schema + seed rows. [research/index-feature-matrices-to-asca-targets.md](research/index-feature-matrices-to-asca-targets.md).
- [Rule-derived probe synthesis for compile validation](issues/10-rule-derived-probe-synthesis.md) — **wontfix**; baseline wordlist (`asca_probe_words.wsca`) via `validate_asca` is sufficient for clustering (~98% failures are Tier 1–2 syntax).
- [Minimal extract-only ingest](issues/11-minimal-extract-only-ingest.md) — `IndexDiachronicaParser` → applier-neutral YAML (`data/diachronica/index_diachronica_parsed.yml`); **Symbol** norm + parse-time class-first fixes (em dash, arrows, chain split, glosses, stress, `sporadic`); class letters deferred to compile.
- [Full-corpus validation inventory](issues/12-full-corpus-validation-inventory.md) — `uv run regenerate_corpus`; per-rule CSV + summary under [inventory/](inventory/). Current baseline: **6422 / 9317 ok (68.9%)** on ASCA 0.10.2.
- [Correction pass (cluster-driven)](issues/13-correction-pass-template.md) — standing recipe; instances are tickets 14–25 (and onward).
- [Correction pass: unknown_grouping (class letters at compile)](issues/14-correction-pass-unknown-grouping.md) — `PhonologicalRuleSet` + `group_mappings.csv` at compile; ~59% of cluster passes outright. Confirmed still required (alias-file spike 2026-08-10).
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
- [Correction pass: residual smart quotes](issues/52-correction-pass-residual-smart-quotes.md) — stress-mark expansion + gloss/apostrophe gaps; **+44** ok.
- [Correction pass: remaining bare length marker ː](issues/25-correction-pass-bare-length-marker.md) — extended length-mark compile pass; `ː` cluster 242 → 40.
- [Correction pass: unknown_grouping residual `T`](issues/43-correction-pass-unknown-grouping-t.md) — `_GROUPING_FOLLOW` IPA tail fix; `T` token 49 → 5 (+38 ok).
- [Parse-time resolution for correspondence-series indices](issues/26-parse-time-correspondence-series-indices.md) — expand at HTML→YAML parse to ASCA-parseable strings when section map exists; `raw` retains subscripts; unmapped → literal + validation fail (no pre-emptive skip). ADR-0004 amended.
- [Rule comment field on corpus rules](issues/30-rule-comment-field-on-corpus-rules.md) — optional `comment` on corpus rules; capture-not-discard prose stripped at parse (semicolon tails, glosses, env qualifiers); distinct from section `comments`.
- [Spike: field-isolation compile validation](issues/35-spike-field-isolation-compile-validation.md) — **go-with-limits**: canned/shape-aware stubs + `validate_asca`/baseline wordlist attribute most Tier 1–2 fails; whole-rule `ok` stays SoT; fails-only sidecar + `blame`; no probe synthesis. Findings: [research/field-isolation-compile-validation.md](research/field-isolation-compile-validation.md). Follow-on: [Field-isolation inventory sidecar](issues/36-field-isolation-inventory-sidecar.md).
- [Inventory success/error CSV splits and ok-change changelog](issues/34-inventory-success-error-splits-and-ok-changelog.md) — regen writes success/error filtered CSVs + append-only `ok`-flip changelog (match by `source`); summary links new artifacts.
- [Document the sound-change rule pipeline in docs/](issues/37-document-sound-change-pipeline.md) — **grill 2026-08-07:** four `docs/` pages + `SYSTEM.md` **Pipeline stages (legacy)** / **(new)**; applier compile table (implemented order + planned `TBD` rows); parse / validation / applier docs split; compile validation lives in applier doc; no ADR for transform order.
- [Spike: ASCA compile transform ordering (planned steps)](issues/38-spike-asca-compile-transform-order.md) — done. Findings: [research/asca-compile-transform-order.md](research/asca-compile-transform-order.md). Orders 3–4 before group mappings; 10 meta cluster-last.
- [Refactor DiachronicSeries and compile subcomponents](issues/39-refactor-sound-change-ruleset.md) — **blocked by 37**; scope TBD until docs land.
- [Spike: unknown_character → IPA mapping candidates](issues/42-spike-unknown-character-ipa-mappings.md) — 42 letter-like tokens classified; high-confidence seed set (ḱ, Ṽ, nasal vowels, š/Ṣ, French è, Slavic yers). Findings: [research/unknown-character-ipa-mappings.md](research/unknown-character-ipa-mappings.md) + [research/unknown-character-ipa-mappings.csv](research/unknown-character-ipa-mappings.csv).
- [Correction pass: IPA letter mappings](issues/49-correction-pass-ipa-letter-mappings.md) — `ipa_mapping.csv` seeded (45 rows); high-confidence applied at parse; all 15 high-conf source tokens cleared from error inventory. Medium rows in CSV; runtime levels → ~~[Parser config: IPA mapping confidence levels](issues/56-parser-config-ipa-confidence-levels.md)~~ done (`data/parser_config.yml` → high+medium at parse).
- [Correction pass: parenthetical segment notation](issues/48-correction-pass-parenthetical-segment-notation.md) — compile `expand_index_parenthetical_notation()` via `expand_meta_notation`; `received '('` cluster 144 → 35 (+109 recovered).
- [Correction pass: superscript segment modifiers](issues/50-correction-pass-superscript-segment-modifiers.md) — compile `normalize_asca_superscript_modifiers()` (pipeline step 4); superscript parse errors 56 → 17 (+40 ok).
- [Correction pass: input optionals to env](issues/51-correction-pass-input-optionals-to-env.md) — compile `expand_input_optionals_to_structures()`; `Options can only be used` cluster 18 → 0 (+18 ok).
- [Spike: inter-segment whitespace and phoneme boundaries](issues/44-spike-inter-segment-whitespace.md) — **compile-only** Brassica spacing; SoT stays Index-shaped (ASCA is space-optional/trie-segmented; Index spaces mostly parallel parts). Findings: [research/inter-segment-whitespace-phoneme-boundaries.md](research/inter-segment-whitespace-phoneme-boundaries.md).
- [Prototype: parse-time inter-segment whitespace feasibility](issues/46-prototype-parse-time-inter-segment-whitespace.md) — demo + readout: segmentiser sketch go-with-limits; parse-time ASCII-space SoT leans no-go until parallel/Kind-B/matrix fixed. [research/parse-time-whitespace-prototype-results.md](research/parse-time-whitespace-prototype-results.md).
- [Feature bundle expansion + vowel-height compounds](issues/57-feature-bundle-expansion-vowel-height.md) — `mapping_kind=bundle` plumbing; seed `close-mid`→`-hi,-lo,+tense`, `open-mid`→`-hi,-lo,-tense` per ASCA vowel-space; +2 ok; unblocks [#54 place bundles](issues/54-correction-pass-unknown-feature-place-bundles.md).
- [Spike: Index syllable position `#U` / `U#` → ASCA](issues/58-spike-index-syllable-position-u-hash.md) — grill 2026-08-09: `! in #U` is syllable-tier, not `// #_%`; leave **~14** exception rules failing until faithful encoding found.
- [Corpus rule `stages` schema cutover](issues/59-corpus-rule-stages-schema.md) — grill 2026-08-09: replace `input`/`output` with uniform **`stages`**; one env/exception per rule; compile expands adjacent pairs. [ADR-0011](../../docs/adr/0011-corpus-rule-stages.md).
- [Parse-time manual rule mappings](issues/60-parse-time-manual-rule-mappings.md) — done: `manual_mappings.csv` at parse before other transforms; `raw` unchanged; debug CSV + unmatched warnings; inventory **7184 → 7185 ok (+1)**.
- [Correction pass: Index parallel-column `∅` in multi-segment I/O](issues/60-correction-pass-parallel-column-null.md) — grill 2026-08-09: omit mixed top-level null columns on input/output; set-internal `∅` out of scope (**note:** duplicate ticket number 60 with manual mappings — rename when convenient).
- [Grill: optional outputs](issues/61-grill-optional-outputs.md) — **needs-grilling** (paused): unpaired output sets e.g. `d → {∅,ð}`; YAML keeps set; choice/testability still open. Glossary: **Optional outputs**.
- [Correction pass: prose env `else`](issues/53-correction-pass-prose-env-else.md) — grill 2026-08-09: parse-time complementary rewrite — prev `env`∧¬exception → else omits `env`, `exception` = prev env; defer 4 env+exception pairs; no `#_` stub.
- [Correction pass: prose env medial](issues/55-correction-pass-prose-env-medial.md) — parse-time — bare `medial`/`medially` = word-internal → `env: _` + `exception: :{#_, _#}:`; `when medial` on structural env same when no exception; defer env+existing-exception merge (Mongolic); comment prose does not narrow to intervocalic. **+53 ok**.

## Pipeline documentation (grill 2026-08-07)

**Runtime:** parse once → correction loop; each pass runs applier compile → compile validation per rule (ADR-0003). Operator command: `uv run regenerate_corpus` (rename deferred).

**Docs (two processing steps, ad hoc — no ticket):**

| SYSTEM.md row | Target doc |
| --- | --- |
| Index Diachronica ingest | `docs/index-diachronica-ingest.md` (merge parser + corpus-validation) |
| Sound change rule compilation | `docs/sound-change-rule-compilation.md` (rename from `sound-change-applier.md`) |

Delete superseded doc paths; fix all links. Transform order in compilation doc only. Refactor `DiachronicSeries` → [ticket 39](issues/39-refactor-sound-change-ruleset.md).

## Implementation plan (tickets 11+)

Phased delivery — not vertical slices upfront:

1. ~~**[Minimal extract-only ingest](issues/11-minimal-extract-only-ingest.md)**~~ — done (parse path also gained class-first fixes from passes 14–25).
2. ~~**[Full-corpus validation inventory](issues/12-full-corpus-validation-inventory.md)**~~ — done; re-run after each correction pass.
3. **[Correction passes](issues/13-correction-pass-template.md)** — in progress via [14–25](issues/14-correction-pass-unknown-grouping.md). ~~[Extract correspondence-series mappings from Index Diachronica HTML](issues/28-extract-correspondence-series-mappings-from-html.md)~~ done → [Implement parse-time correspondence-series expansion](issues/27-implement-parse-time-correspondence-series-expansion.md). Coverage follow-ups: [series-mappings-coverage-backlog.md](series-mappings-coverage-backlog.md). ~~[Spike: Index feature matrices → ASCA targets](issues/29-spike-index-feature-matrices-to-asca-targets.md)~~ done → ~~[Correction pass: unknown_feature Phase 1](issues/32-correction-pass-unknown-feature.md)~~ done (renames + `short`→`-long`); Phase 2 place bundles open.
4. **Validation confidence (2026-08 charted):** ~~[Inventory success/error CSV splits and ok-change changelog](issues/34-inventory-success-error-splits-and-ok-changelog.md)~~ done; next [Field-isolation inventory sidecar](issues/36-field-isolation-inventory-sidecar.md) (spike done). ~~[Correction pass: positional slots and identity subscripts](issues/40-correction-pass-positional-identity-subscripts.md)~~ phase 1 done (+51 ok) → [Correction pass: subscript edge cases (phase 2)](issues/41-correction-pass-subscript-edge-cases.md). ~~[Compile-time chain expansion](../adr-0005-no-ingest-split/issues/03-compile-time-chain-expansion.md)~~ done (+132 ok). (`samePOA` / deferred unknown_feature leftovers stay inventory-driven — no standalone ticket; former #33 deleted as too specific.)

**Compile validation:** use ASCA directly (`validate_asca` / `asca run` + baseline wordlist) on **compile-expanded** rule strings — not `-l` for class letters (alias file does not rewrite `.rsca` tokens). Rule-derived candidate generation ([ticket 10](issues/10-rule-derived-probe-synthesis.md)) — **wontfix**. Field-isolation (if adopted) must stay inside that boundary.

## Not yet specified

- **Bare I/O “already good” tagging** — optional idea: for rules with only `input`/`output` (no `env`/`exception`/`comment`), try Index `raw` with arrow normalised to ASCA `>` and see if ASCA accepts; tag as not needing transforms. Left foggy on purpose (grill Q5); full-rule `ok` + [ok-change changelog](issues/34-inventory-success-error-splits-and-ok-changelog.md) may already cover regression guarding. Revisit after 34/35.
- **Subscript notation (all four uses)** — grilled + researched: [subscript-notation-index-asca-brassica.md](research/subscript-notation-index-asca-brassica.md), [positional-slots-and-identity-subscripts.md](research/positional-slots-and-identity-subscripts.md). **Working policy:** correspondence-series + collective → **parse-time**; positional + identity → **compile-time** (Index-shaped in YAML). **Phase 1:** [Correction pass: positional slots and identity subscripts](issues/40-correction-pass-positional-identity-subscripts.md) (+51 ok). **Phase 2:** [Correction pass: subscript edge cases](issues/41-correction-pass-subscript-edge-cases.md). **Compile order:** [research/asca-compile-transform-order.md](research/asca-compile-transform-order.md).
- **Meta-notation at ingest** — later find/replace; cluster-driven for now (ticket 06)
- **Section-local abbreviations** (e.g. Athabaskan `TŠ`) — cluster-driven; hand-add mapping rows when warranted
- Abbreviation table authorship at scale
- Prose-**environment** mapping — informed by extracted **`comment`** qualifiers ([Capture rule comments at parse time](issues/31-capture-rule-comments-at-parse-time.md)). **`/ else` catch-alls** → [ticket 53](issues/53-correction-pass-prose-env-else.md) (done). **`medial` / `medially`** → [ticket 55](issues/55-correction-pass-prose-env-medial.md) (done). Other prose env clusters still inventory-driven.
- **Optional outputs** — unpaired Index output sets (e.g. `d → {∅,ð}`); ASCA-illegal; choice/render design paused — [grill ticket 61](issues/61-grill-optional-outputs.md) (`needs-grilling`)
- Adoption criteria for cleaned YAML replacing HTML as **SoT**
- Brassica compiler (ADR-0001)
- Edge-split policy (ADR-0005; **`status: skipped` deferred** until post-correction triage per ticket 26 / ADR-0010)
- External one-off rule override schema

## Out of scope

- Generative sound-change *sequences* model — see [Generative sound-change sequences (GAN or next-in-sequence)](../sound-change-sequences/issues/01-generative-sound-change-sequences.md)
- Bundle ~100 preset inventories — [Bundle ~100 pre-generated phoneme inventories](../phoneme-inventories/issues/01-bundle-100-pregenerated-inventories.md)
- Automate PHOIBLE/WALS prep — [Automate PHOIBLE and WALS data preparation pipeline](../data-processing-pipeline/issues/01-automate-phoible-wals-prep.md)
- Full Brassica adoption / shipping a Brassica compiler
