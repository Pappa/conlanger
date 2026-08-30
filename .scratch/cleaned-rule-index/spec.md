Status: ready-for-agent

# Cleaned rule index

Applier-neutral YAML successor to Index Diachronica HTML as the authoritative **rule index**, where **corpus rules** carry a **stages** spine and **compile** to valid ASCA under **historical fidelity** constraints, with a scalable **class-first** correction workflow.

Glossary: `CONTEXT.md`. Architectural context: ADRs 0001–0006, 0010–0014. Living decisions: `.scratch/cleaned-rule-index/map.md`. Operator command: `uv run create_index`. Pipeline: **parse → compile → validate** ([ADR-0013](../../docs/adr/0013-parse-compile-validate.md)).

## Problem Statement

Index Diachronica HTML is the current **source of truth** for attested sound-change rules, but it is not directly executable by sound-change appliers. Early ASCA-flavoured YAML dumps mirrored applier syntax rather than an applier-neutral **rule index**, and a large share of rules still fail **compile validation** under ASCA even after years of provisional cleanup.

The project needs a **cleaned rule index** — structured YAML owned by Conlanger, not ASCA or Brassica — from which **applier compilers** emit executable rules, with automated **compile validation**, grouped **failure classes** for prioritisation, explicit **rule status** for config hold-outs, and durable provenance back to the HTML. Progress must be measurable (section-completeness and ok-flip changelog), historically faithful (no valid-but-inaccurate rewrites), and scalable (class-first transforms over one-off edits).

## Solution

Build and iterate an end-to-end pipeline that:

1. **Parses** Index Diachronica HTML into applier-neutral YAML (**corpus rules** with **stages**, `raw`, `rule id`, `source`; optional `env`, `exception`, `status`, `sporadic`, `comment`).
2. Applies **class-first** normalisation at parse and compile (symbol cleanup, IPA and feature mappings, manual mappings, section mappings, series expansions, prose env rewrites, nested-set flattening, and dozens of cluster-driven correction passes) while preserving `raw` and **historical fidelity**.
3. **Compiles** each **sound-change section** through **DiachronicSeries** with operator config injected at the script boundary (`ParserConfig`, `CompilerConfig` — group mappings, series mappings, feature bundles, compile transforms).
4. **Validates** each **corpus rule** post-compile via forked ASCA (`validate_asca` / `validate_asca_part` on compiled field strings; baseline probe wordlist).
5. **Inventories** ok/fail/skipped per rule with **failure classes**, per-field **blame**, success/error CSV splits, and an append-only ok-flip changelog.
6. **Iterates** correction passes cluster-driven from inventory until adoption criteria for promoting cleaned YAML over HTML as SoT are met.

Brassica compilation remains a future parallel path behind the same index (ADR-0001); this spec delivers the ASCA path first.

**Current baseline** (ASCA 0.10.2, regenerated index): **8089 / 9676 ok (83.6%)**; **373 / 714 sections all OK (52.2%)**; **975** fail; **612** skipped (config hold-outs). Success metric prioritises **sections with zero validation fails**; near-miss sections (≤3 fails) are hunted before heavy-residual sections.

## User Stories

1. As a pipeline maintainer, I want Index Diachronica HTML parsed into applier-neutral YAML, so that appliers compile from a single index format rather than ad-hoc ASCA strings.
2. As a pipeline maintainer, I want every **corpus rule** to carry `raw`, `rule id`, and `source` provenance, so that I can audit any cleaned field against the HTML line.
3. As a pipeline maintainer, I want the change spine stored as **stages** (ordered opaque strings), so that single-step, chain, and missing-arrow rules share one schema (ADR-0011).
4. As a pipeline maintainer, I want optional `env` and `exception` omitted when absent, so that “any environment” and “no exception” need no sentinel values.
5. As a pipeline maintainer, I want **sound-change sections** to map one-to-one with HTML `<h2>` blocks, so that section identity (index, title, citation) is preserved for compile and analysis.
6. As a pipeline maintainer, I want section-level `status: skipped` only from operator config (`skip_sections`), so that whole sections can be held out without editing HTML.
7. As a sound-change researcher, I want **historical fidelity** preferred over valid-but-inaccurate rewrites, so that the index reflects Index Diachronica claims even when ASCA cannot express them (ADR-0010).
8. As a sound-change researcher, I want rules held out via config (`skip_rules`) to render as ASCA comments, so that they remain visible without silently changing phonological meaning.
9. As a sound-change researcher, I want detailed skip/validation reasons in a **validation report**, not embedded in the long-term YAML, so that the index stays applier-neutral and lean.
10. As an agent implementing fixes, I want **failure classes** grouped across the index, so that I can prioritise **class-first** transforms over one-off edits.
11. As an agent implementing fixes, I want a steady-state correction loop (parse → compile → validate → regenerate → cluster → fix), so that progress is measurable and repeatable.
12. As an agent implementing fixes, I want **class-first** transforms in the parser or compile layer, so that mechanical fixes scale across thousands of rules.
13. As an agent implementing fixes, I want git-diffable YAML regeneration, so that I can review churn and grow regression fixtures when outcomes change.
14. As an agent implementing fixes, I want section-completeness as the primary success metric, so that finishing near-miss sections (≤3 fails) is prioritised over raw ok-percentage alone.
15. As a developer, I want **compile validation** after applier compile (not at YAML ingest), so that the index remains applier-neutral per ADR-0003.
16. As a developer, I want `validate_asca` with clear errors on failure, so that the correction workflow has a concrete ASCA gate.
17. As a developer, I want validation driven by forked ASCA (`github.com/Pappa/asca-rust` 0.10.3) via `asca validate` and `asca run` on the baseline probe wordlist, so that syntax and runtime structural failures are caught where probes match rule shape.
18. As a developer, I want per-field `validate_asca_part` blame in inventory, so that Tier 1–2 syntax failures attribute to input, output, env, or exception without stub rules.
19. As a developer, I want **DiachronicSeries** to accept injected **CompilerConfig** (group mappings, series mappings), so that class-letter and correspondence-index expansion applies at compile without baking ASCA syntax into the index YAML.
20. As a developer, I want unmapped **class letters** to pass through unchanged, so that validation surfaces unknown tokens via **failure classes** rather than silent substitution.
21. As a developer, I want **symbol** normalisation at HTML→YAML parse, so that Index boundary/null/stress marks become ASCA-canonical in compile fields while `raw` preserves Index form.
22. As a developer, I want **feature matrix** synonym replacement at parse inside `[...]` via operator feature mappings, so that safe 1:1 ASCA equivalents normalise without inventing bundles.
23. As a developer, I want unmapped feature names left as-is at parse, so that `unknown_feature` failures drive cluster-based mapping work.
24. As a developer, I want **IPA letter mappings** at parse with configurable confidence levels, so that high- and medium-confidence tokens normalise while low-confidence rows await evidence.
25. As a developer, I want **manual mappings** applied at parse (after corrections, before other transforms), so that maintainer-authored rewrites scale without editing HTML.
26. As a developer, I want **Index Diachronica corrections** keyed by **rule id** to replace `raw` at parse, so that owner corrections do not require editing the HTML file (ADR-0012).
27. As a developer, I want **section mappings** at parse for section-local abbreviation expansion (e.g. Athabaskan `*D`/`*R`/`*T`), so that hierarchical shorthand resolves before compile.
28. As a developer, I want **series expansions** (collectives, global) at parse and **series mappings** (correspondence indices) at compile, so that the four **subscript notation** uses each land at the correct stage.
29. As a developer, I want multi-line `raw` preserved via YAML literal blocks, so that complex HTML rule lines remain byte-auditable.
30. As a developer, I want lxml non-strict HTML parsing of the Index HTML SoT, so that real-world markup quirks do not block ingest.
31. As a developer, I want **compile validation** scoped per **corpus rule** within a section, so that one bad rule does not obscure others in the same **sound-change section**.
32. As a developer, I want a validation report CSV with section identity, **rule id**, ok/fail, **failure class**, reason, description, and optional **blame** / **alt_idx**, so that pandas analysis can drive correction priorities.
33. As a developer, I want success and error filtered CSV splits plus an append-only ok-flip changelog keyed by `source`, so that regressions and wins are auditable across passes.
34. As a developer, I want chain rules (length ≥ 3 **stages**) expanded at compile into adjacent pairs, so that one HTML line can encode multi-step changes without parse-time row splitting (ADR-0005 amended).
35. As a developer, I want missing-arrow rules (length-1 **stages**) to compile with an empty output, so that prose-only lines inventory as fails rather than being auto-skipped.
36. As a developer, I want **optional outputs** (unpaired output sets) compiled as **alternative outcomes** with uniform random selection and inventory validated on alternatives only (`alt_idx`), so that speaker variation is representable without structuring optional outputs in YAML (ticket 61).
37. As a developer, I want nested bracket sets flattened at parse (env/exception and stages I/O) per researched policy, so that ASCA-parseable flat sets replace Index nesting where safe.
38. As a developer, I want Index I/O parenthetical optionals expanded to flat cartesian `{…}` sets (not ASCA `<>` optionals), so that compile matches linguistic convention and ASCA syntax limits (ticket 100).
39. As a developer, I want prose env **`else`** rewritten to complementary **exception** on the following rule, so that Index catch-alls become ASCA-valid without `#_` stubs.
40. As a developer, I want prose env **`medial`** / **`medially`** rewritten to `_` env plus boundary **exception**, so that word-internal conditioning is ASCA-expressible.
41. As a developer, I want the first semicolon on a rule line cut as **rule comment** before chain split, so that editorial prose does not break I/O parsing.
42. As a developer, I want **sporadic** qualifiers stripped from fields and recorded as `sporadic: true`, so that uncertainty is metadata rather than ASCA syntax.
43. As a developer, I want compile-time normalisation for length marks, ejective marks, superscript modifiers, parenthetical segment notation, labialized class letters, and group-mapping boundary rules, so that Index typography becomes ASCA-canonical without mutating `raw`.
44. As a developer, I want per-field string transforms on **SoundChangeRule** with compiled fields joined at render, so that `.rsca` output stays byte-identical while enabling per-field validation (ADR-0014, ticket 99).
45. As a developer, I want package library code to accept in-memory config only (empty defaults), with scripts loading operator YAML from `config/`, so that tests do not depend on production mapping drift.
46. As a project owner, I want permanent skip decisions and rare same-intent swaps to require my approval, so that meaning-changing exceptions stay controlled.
47. As a test author, I want fixture rows in `sound_change_rules.csv` for HTML-extract expectations and ASCA-guess validation cases, so that parser and validator regressions share one auditable table.
48. As a test author, I want end-to-end pipeline smoke tests (HTML → parse → compile → validate), so that the highest integration seam guards the correction loop.
49. As a pipeline consumer, I want the cleaned YAML to replace HTML as SoT only after explicit adoption criteria are met, so that premature promotion does not lose HTML authority.
50. As a future Brassica integrator, I want the index to remain applier-neutral, so that a Brassica **applier compiler** can be added without reshaping on-disk YAML.
51. As a maintainer, I want the edit ladder (formatting → token replacement → normalisation → config skip) applied consistently, so that agents do not invent ad-hoc per-rule policies.
52. As a maintainer, I want inventory metrics reproducible (rule counts, ok/fail/skipped, sections all-OK, top **failure classes**), so that progress toward a compilable index is trackable across iterations.
53. As a maintainer, I want **meta-notation** and residual prose-env clusters handled inventory-driven, so that hard cases are not blocked on premature global policies.
54. As a maintainer, I want ASCA alias file (`asca -l`) kept complementary for lexicon romanisation only, not for class-letter expansion in rules, so that compile uses group mappings instead (grill 2026-08-10).
55. As a maintainer, I want `legacy/` treated as read-only prior attempts, so that new implementation does not copy obsolete code or data.
56. As an operator, I want `uv run create_index` to regenerate YAML, inventory CSVs, summary, and comment-phrase survey in one invocation, so that the correction loop is automatable by agents.
57. As an operator, I want `--skip-validation` for ingest-only runs when ASCA is not installed, so that parse work is not blocked by the validator binary.
58. As a developer, I want syllable-position `#U` / `U#` tails compiled via underline structures and env-set exceptions, so that Index positional notation becomes ASCA-valid without shipping `// #_%` (ticket 58).
59. As a developer, I want inter-segment whitespace handled compile-only (Brassica spacing policy), so that the SoT stays Index-shaped while ASCA remains space-optional.
60. As a researcher, I want **rule comment** prose captured in `comment` and section prose in section `comments`, so that editorial context is preserved without polluting compile fields.

## Implementation Decisions

### Corpus schema and source of truth

- Top-level YAML: `sections` array (top-level `abbreviations` retired from parse output; section-local maps live in operator config).
- Each **sound-change section**: required `section` (title), `index` (dotted ancestry key); optional `citation`, section-level `comments`, `rules`, `status: skipped` (config hold-out only).
- Each **corpus rule**: required **stages** (list of opaque Index-shaped strings), `raw`, `rule id`, `source` (`index_diachronica_original.html:<line>`); optional `env`, `exception`, `status`, `sporadic`, `comment`.
- **Stages** length 2 = single change; ≥ 3 = chain (compile expands adjacent pairs); 1 = missing arrow (compile supplies empty output).
- Field values are opaque Index-shaped strings — not an ASCA AST. Config-skipped rules carry `status: skipped` and render as ASCA comments (`#\t` + `raw`).
- HTML remains current SoT until cleaned YAML meets adoption criteria; regeneration must remain traceable to HTML (ADR-0006). **Index Diachronica corrections** overlay `raw` by **rule id** without editing HTML (ADR-0012).

### Operator config vs corpus data

- **config/** — operator settings (YAML), loaded only by scripts and injected as `ParserConfig` / `CompilerConfig`. Parse: `parser_config.yml`, `manual_mappings.yml`, `ipa_mappings.yml`, `feature_mappings.yml`, `index_diachronica_corrections.yml`. Compile: `compiler_config.yml`, `group_mappings.yml`.
- **data/** — corpus and generated artifacts: Index HTML SoT, regenerated `index_diachronica_parsed.yml`, runtime ASCA alias file, inventory outputs under `.scratch/cleaned-rule-index/inventory/`.
- Library code under `src/conlanger` (except scripts) accepts in-memory config; empty defaults when omitted. `create_index` is the bootstrap composing real operator config.

### Parse (HTML → YAML)

- Parser: `IndexDiachronicaParser` using lxml; phases cover section structure, **stages** spine from `→` splits, `/ env` and `! exception` parsing, citation/comments, rule id from HTML `id`.
- Transform order (representative): corrections overlay → section mappings → manual mappings → symbol/IPA/feature normalisation → class-first correction passes (em dash, arrow, glosses, sporadic, stress, smart quotes, chain-aware comment cut, prose env else/medial, parallel-column null omission, nested-set flatten, optional-output detection metadata, series expansions, section skip flags, etc.). All preserve `raw` except corrections replace it entirely.
- **Class letters**: no ingest-time blind substitution; expansion at compile via **CompilerConfig** group mappings. Six letters (C, O, F, L, N, V) pass through (ASCA inbuilt). Mapped letters expand per boundary rules; glued sequences (`SR`, `VOR`) expand letter-by-letter when recognised.
- **Correspondence-series indices**: compile-time series mappings (longest-prefix lookup); **collective subscripts**: parse-time series expansions from parser config.
- **Positional slots** and **identity subscripts**: compile projection (phases 1–2 done; edge-case hold-outs remain).
- Edge-split (ADR-0005): one **corpus rule** per HTML line; chains stay one row; compile-time chain expansion emits sequential ASCA steps.

### Compile

- One **sound-change section** → one **DiachronicSeries**: runtime container with **SoundChangeRule** per **corpus rule**.
- Per-field string transforms at **SoundChangeRule** instantiation (ADR-0014); compiled `input`/`output`/`env`/`exception` strings stored on the rule and joined at `__str__` / render (ticket 99).
- Compile pipeline (order documented in applier compile doc): representative steps include superscript normalisation, parenthetical expansion, input-optionals-to-structures, length/ejective marks, group mappings, labialized class letters, series mappings, chain expansion, optional-output alternative peers.
- **Optional outputs**: parent rule holds alternatives; inventory validates alternatives only with `alt_idx`; parent samples one alternative via instance `Random`.
- ASCA alias file is **not** used for class-letter rewrite in rules; group mappings at compile are authoritative.

### Validate and inventory

- Post-compile only (ADR-0003): `validate_asca` = `validate_asca_syntax` then `asca run` + baseline wordlist; `validate_asca_part` for per-field blame.
- Forked ASCA 0.10.3 (`ASCA_BIN`); CLI fields `input`/`output`/`context`/`exception`.
- One inventory row per **corpus rule**; config-skipped rules count as ok with description `held-out (commented rule)`.
- Artifacts: full inventory CSV, success/error splits, ok-flip changelog, summary markdown, optional field-isolation/blame CSVs.
- Tier 4 runtime failures may be under-detected when probes do not match rule shape — acceptable for clustering. Rule-derived probe synthesis (ticket 10) — **wontfix**.

### Historical fidelity and rule status

- Edit ladder (ADR-0010): class-first safe transforms OK; meaning-changing or ASCA-unrepresentable → config `skip_rules` / `skip_sections` only after class-first work exhausted; valid-but-inaccurate rewrites forbidden. No auto-skip for unmapped tokens during bulk correction.
- Corpus carries thin optional `status` only; full validator detail lives in temporary **validation report** CSV.
- Defined transform classes: apply without per-rule approval. Permanent skip / rare swaps: project owner only.

### Correction workflow and prioritisation

- Steady-state loop: parse HTML → compile → validate per rule → regenerate YAML + inventory → cluster **failure classes** → implement correction pass → repeat.
- Primary metric: **sections with 0 validation fails**; hunt near-miss sections (≤3 fails) before heavy-residual sections.
- **Current frontier** (from map): `*X` wildcards (83), parenthesized optional length `(ː)` (104, blocked by grill 94), breve `̆` (84), tone features (62), near-miss unknown_character (63), syllable-position `#U`/`U#` (98); paused grill on paren/parallel notation (71) now unblocked by I/O optionals spike (100). Group-mapping residuals (M/X/I/Y) deprioritised.
- Class-first transforms live in parser (parse-time) and **SoundChangeRule** compile transforms. External one-off override schema deferred.

### Adoption criteria (to define)

- Not yet specified; requires owner sign-off before promoting cleaned YAML over HTML (e.g. minimum sections-all-OK rate, ok-percentage floor, zero unexplained drift from `raw`, fixture coverage for changed statuses).

## Testing Decisions

### Primary seam (proposed — one integration surface)

**HTML file → `IndexDiachronicaParser.parse` (with injected config) → index document → per-section `DiachronicSeries` compile → `validate_asca` / `validate_index_rule` per active corpus rule.**

This is the highest seam that exercises ingest, **stages** schema, config injection policy, ASCA compilation, and post-compile validation together — matching the correction workflow (ticket 05) and ADR-0003. Prior art: `tests/conlanger/tools/test_index_pipeline.py` documents and implements this seam.

Tests at this seam should:

- Use real or minimal HTML fixtures mirroring Index Diachronica structure (`<section>`, `<h2>`, `<p class="schg">` with `id`).
- Assert **corpus rule** fields (`stages`, `raw`, `rule id`, `source`, optional `env`/`exception`/`status`) without asserting internal parser function names.
- Build `DiachronicSeries` with minimal injected config and call `validate_asca` or `validate_index_rule`; expect pass or documented fail for held-out rules.
- Prefer parametrized cases from `tests/fixtures/sound_change_rules.csv` (`html_extract` for ingest; hand-curated E2E smoke for full pipeline — `asca_guess` rows are not reliable for full-pipeline expectation without re-baselining).

Rationale: lower seams (rule-line splitting alone, or `validate_asca` alone) do not prove the index pipeline; higher seams (full lexicon evolution) mix unrelated concerns. One end-to-end compile-validation seam minimises cross-module test duplication.

### Supporting seams (existing — do not replace)

- Parser unit/param tests on rule-line splitting and HTML element parsing — `tests/conlanger/tools/test_parser.py` against `sound_change_rules.csv` `html_extract` rows.
- Validator unit tests — `tests/conlanger/tools/test_asca_validator.py` against `asca_guess` fixture rows.
- Per-cluster correction-pass tests (tickets 14+) — parse and compile transforms with ASCA where applicable.
- Config injection tests with `minimal_compiler_config` / empty defaults — no production config assertions in library tests (ticket 102).

### What makes a good test

- Assert external behaviour: YAML shape, rendered `.rsca` strings, validation pass/fail, `status` on corpus rules — not private methods or intermediate CSV layouts unless that artifact is the public contract.
- Preserve auditability: fixture rows keep `id`, `source`, `raw` pointing at HTML lines.
- When compile outcome changes intentionally, update fixtures and note the **failure class** or edit-ladder step that motivated the change.
- Skip ASCA-dependent tests gracefully when the binary is absent (match existing `ASCA_INSTALLED` pattern).
- Use injected minimal config in unit tests; load production config only in integration/script tests.

### Modules under test

- `IndexDiachronicaParser` (parse)
- `DiachronicSeries` / `SoundChangeRule` (compile + ASCA emission)
- `validate_asca` / `validate_asca_part` (post-compile gate)
- `index_inventory` / `create_index` (orchestration: YAML + validation report from HTML path)

## Out of Scope

- **Generative sound-change sequences** model — `.scratch/sound-change-sequences/`.
- Bundling ~100 **preset inventories** — `.scratch/phoneme-inventories/`.
- Automating PHOIBLE/WALS data prep — `.scratch/data-processing-pipeline/`.
- Shipping a **Brassica compiler** or full Brassica adoption.
- **Abbreviation table authorship at scale** beyond operator config + inventory-driven hand-adds.
- External one-off rule override schema.
- Promoting cleaned YAML to SoT without owner-approved adoption criteria.
- **Rule-derived probe synthesis** (ticket 10 — wontfix).
- Porting ASCA's full unit-test index wholesale.
- Copying implementation or data from `legacy/`.
- Structured compile IR collections on **SoundChangeRule** (ticket 94 — blocked/unscheduled; condensed/parallel column IR deferred).
- Sporadic sampling at apply time (ticket 68 — `needs-triage`).

## Further Notes

- Wayfinder map (living decisions, ticket frontier): `.scratch/cleaned-rule-index/map.md`.
- ASCA validity reference: `.scratch/cleaned-rule-index/research/asca-rule-validity.md`.
- Inventory baseline: `.scratch/cleaned-rule-index/inventory/` (**8089 ok / 9676 rows**, 83.6%).
- Pipeline docs: `docs/system/index-diachronica-parser.md`, `docs/system/sound-change-applier.md`, `docs/system/validate.md`, `docs/SYSTEM.md`.
- Re-inventory after major milestones: `uv run create_index`.
- Grill 71 (paren/parallel set notation) paused 2026-08-29; resume from `research/io-optionals-asca-and-convention.md` after ticket 100 resolution.
- Config layout migration (ticket 101) and compiled-fields-at-render (ticket 99) are resolved as of 2026-08-30.
