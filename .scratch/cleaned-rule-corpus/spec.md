Status: ready-for-agent

# Cleaned rule corpus

Applier-neutral YAML successor to Index Diachronica HTML as the authoritative **rule corpus**, with **corpus rules** that **compile** to valid ASCA under **historical fidelity** constraints and a scalable **class-first** correction workflow.

Glossary: `CONTEXT.md`. Architectural context: ADRs 0001–0006, 0010. Prior decisions: `.scratch/cleaned-rule-corpus/map.md` and resolved tickets 01–09.

## Problem Statement

Index Diachronica HTML is the current **source of truth** for attested sound-change rules, but it is not directly executable by sound-change appliers. Provisional ASCA-flavoured YAML dumps exist, yet roughly 43% of rules fail **compile validation** under ASCA, the on-disk shape still mirrors applier syntax rather than an applier-neutral **rule corpus**, and there is no durable workflow to clean rules at scale while preserving **historical fidelity** and auditability back to the HTML.

The project needs a **cleaned rule corpus** — structured YAML owned by Conlanger, not ASCA or Brassica — from which **applier compilers** emit executable rules, with automated **compile validation**, grouped **failure classes** for prioritisation, and explicit **rule status** for held-out cases.

## Solution

Build an end-to-end pipeline that:

1. Parses **Index Diachronica HTML** into the applier-neutral YAML schema (global and section-level **abbreviation** tables, **sound-change sections**, **corpus rules** with `input`/`output`/`raw`/`source` and optional `env`/`exception`/`status`).
2. Applies **class-first** normalisation at ingest (safe **symbol** and **feature matrix** synonym replacement; **class letter** expansion deferred to compile time via **abbreviation table** CSV).
3. Compiles each **sound-change section** through a **PhonologicalRuleSet** that loads package **abbreviation tables** and emits ASCA-ready strings.
4. Runs **compile validation** per **corpus rule** via `validate_asca` (ASCA 0.10.2, probe wordlist).
5. Produces a temporary **validation report** (CSV) with **failure classes** and reason vocabulary; sets thin optional `status` on corpus rules (`needs-validation`, `skipped`; omit = ok).
6. Iterates: cluster failures → implement parser/compiler fixes → regenerate YAML → grow fixtures for changed **rule status** — until adoption criteria for replacing HTML as SoT are met.

Brassica compilation remains a future parallel path behind the same corpus (ADR-0001); this spec delivers the ASCA path first.

## User Stories

1. As a pipeline maintainer, I want Index Diachronica HTML parsed into applier-neutral YAML, so that appliers compile from a single corpus format rather than ad-hoc ASCA strings.
2. As a pipeline maintainer, I want every **corpus rule** to carry `raw` and `source` provenance, so that I can audit any cleaned field against the HTML line.
3. As a pipeline maintainer, I want optional `env` and `exception` fields omitted when absent, so that “any environment” and “no exception” are represented without sentinel values.
4. As a pipeline maintainer, I want **sound-change sections** to map one-to-one with HTML `<h2>` blocks, so that section identity (index, title, citation) is preserved for compile and analysis.
5. As a sound-change researcher, I want **historical fidelity** preferred over valid-but-inaccurate rewrites, so that the corpus reflects Index Diachronica claims even when ASCA cannot express them.
6. As a sound-change researcher, I want rules that cannot be faithfully compiled marked `status: skipped` with empty `input`/`output`, so that held-out rules remain visible without silently changing phonological meaning.
7. As a sound-change researcher, I want detailed skip/validation reasons in a **validation report**, not embedded in the long-term YAML, so that the corpus stays applier-neutral and lean.
8. As an agent implementing fixes, I want **failure classes** grouped across the corpus, so that I can prioritise **class-first** transforms over one-off edits.
9. As an agent implementing fixes, I want a steady-state correction loop (parse → compile → validate → regenerate → cluster → fix), so that progress is measurable and repeatable.
10. As an agent implementing fixes, I want **class-first** transforms implemented in the HTML parser, so that mechanical fixes scale across thousands of rules.
11. As an agent implementing fixes, I want git-diffable YAML regeneration, so that I can review churn and grow regression fixtures when **rule status** changes.
12. As a developer, I want **compile validation** after applier compile (not at YAML ingest), so that the corpus remains applier-neutral per ADR-0003.
13. As a developer, I want `validate_asca(SoundChangeRule) -> True` with clear errors on failure, so that correction workflow has a concrete ASCA gate.
14. As a developer, I want validation driven by ASCA 0.10.2 via `asca run` on a **probe wordlist**, so that runtime structural failures are caught alongside syntax errors.
15. As a developer, I want **PhonologicalRuleSet** to load `group_mappings.csv` at compile time, so that **class letter** expansions apply without baking ASCA syntax into the corpus YAML.
16. As a developer, I want unmapped **class letters** to pass through unchanged, so that validation surfaces unknown tokens via **failure classes** rather than silent substitution.
17. As a developer, I want **symbol** normalisation at HTML→YAML ingest, so that Index boundary/null/stress marks become ASCA-canonical in corpus fields while `raw` preserves Index form.
18. As a developer, I want **feature matrix** synonym replacement at ingest inside `[...]` only, so that Index feature names with safe 1:1 ASCA equivalents normalise via `feature_mappings.csv`.
19. As a developer, I want unmapped feature names left as-is at ingest, so that `unknown_feature` failures drive cluster-based mapping work.
20. As a developer, I want global and section-level **abbreviation** tables in the YAML schema, so that hierarchical shorthand resolution is representable even when section overrides are deferred.
21. As a developer, I want multi-line `raw` preserved via YAML literal blocks, so that complex HTML rule lines remain byte-auditable.
22. As a developer, I want lxml non-strict HTML parsing of `index_diachronica_original.html`, so that real-world markup quirks do not block ingest.
23. As a developer, I want **compile validation** scoped per **corpus rule** within a section, so that one bad rule does not obscure others in the same **sound-change section**.
24. As a developer, I want a validation report CSV with columns for section identity, rule index, ok/fail, **failure class**, reason, and description, so that pandas analysis can drive correction priorities.
25. As a developer, I want CSV reason vocabulary (`trailing-comment`, `broken-syntax`, `asca-unrepresentable`, `valid-but-inaccurate`, `other`), so that skip decisions are filterable and consistent with ADR-0010.
26. As a developer, I want `status: needs-validation` for rules that received structural normalisation pending re-check, so that agents can clear status on clean re-validate without owner approval.
27. As a project owner, I want permanent **skipped** rules and rare same-intent swaps to require my approval, so that meaning-changing exceptions stay controlled.
28. As a test author, I want fixture rows in `sound_change_rules.csv` for both HTML-extract expectations and ASCA-guess validation cases, so that parser and validator regressions share one auditable table.
29. As a test author, I want sampled HTML rules (with recorded RNG seed) in fixtures, so that validator behaviour is grounded in real Index Diachronica lines.
30. As a pipeline consumer, I want the cleaned YAML to replace HTML as SoT only after explicit adoption criteria are met, so that premature promotion does not lose HTML authority.
31. As a future Brassica integrator, I want the corpus to remain applier-neutral, so that a Brassica **applier compiler** can be added without reshaping on-disk YAML.
32. As a maintainer, I want edge-split policy (ADR-0005) to use interim `status: skipped` for unrepresentable one-line splits, so that provenance is kept without inventing extra authored rules.
33. As a maintainer, I want trailing undelimited comments extracted to compile comments when safe, else skipped with reason `trailing-comment`, so that prose after rules does not break ASCA parse.
34. As a maintainer, I want the edit ladder (formatting → token replacement → normalisation → skip) applied consistently, so that agents do not invent ad-hoc per-rule policies.
35. As a maintainer, I want inventory metrics reproducible (rule counts, ok/fail percentages, top **failure classes**), so that progress toward a compilable corpus is trackable across iterations.
36. As a maintainer, I want **series indices** and section-local prose abbreviations handled cluster-driven with hand-added mapping rows when warranted, so that hard cases are not blocked on a global prose-extraction spike.
37. As a maintainer, I want **meta-notation** (`X0`, `Xn`, retroflex marks, repetition groups) deferred to validation clusters, so that the first delivery does not invent ASCA expansions without evidence.
38. As a developer, I want `SoundChangeRule` / `RuleChange` to render ASCA rule strings from corpus rule dicts, so that the ASCA **applier compiler** has a stable string emission layer.
39. As a developer, I want skipped corpus rules to render as ASCA comments, so that `validate_asca` ignores held-out rules without deleting section structure.
40. As an operator, I want a script or entry point to regenerate the full cleaned YAML from HTML and emit the validation report in one invocation, so that the correction loop is automatable by agents.

## Implementation Decisions

### Corpus schema and source of truth

- Top-level YAML: `abbreviations` (string→string) + `sections` array.
- Each section: required `section` (title), `index` (dotted ancestry key); optional `citation`, section-level `abbreviations`, `rules`.
- Each **corpus rule**: required `input`, `output`, `raw`, `source` (`index_diachronica_original.html:<line>`); optional `env`, `exception`, `status`.
- Field values are opaque Index-shaped strings — not an ASCA AST. Empty `input`/`output` when `status: skipped`.
- HTML (`index_diachronica_original.html`) remains current SoT until cleaned YAML meets adoption criteria; regeneration must remain traceable to HTML (ADR-0006).
- Provisional files (`index_diachronica_ai.yml`, early XML) are migration references only.

### Ingest (HTML → YAML)

- Parser: `IndexDiachronicaParser` using lxml; phases cover section structure, `→` I/O split, `/ env` and `! exception` parsing, citation/comments.
- **Symbol** normalisation at ingest to ASCA-canonical form in corpus fields; `raw` unchanged.
- **Feature matrix** synonym replacement at ingest inside `[...]` via `feature_mappings.csv`; unmapped names left as-is.
- **Class letters**: no ingest-time `str.maketrans` blind substitution as the long-term approach; expansion at compile via **PhonologicalRuleSet** + `group_mappings.csv`. Six letters (C, O, F, L, N, V) pass through (ASCA inbuilt). Seventeen validated rows in `group_mappings.csv`; M (diphthong) removed — cluster-driven.
- **Series indices**, section-local prose abbreviations, **meta-notation**: cluster-driven; hand-add abbreviation rows when inventory warrants.
- **Whitespace tokenisation** for inter-segment spacing: deferred.
- Edge-split (ADR-0005): interim `status: skipped` for lines not yet representable as one **corpus rule**.

### Compile and validation

- One **sound-change section** → one **PhonologicalRuleSet** (runtime container: corpus rules + abbreviation mappings + compiled output). *Not yet implemented; ticket 06 follow-on.*
- **Applier compiler** path: corpus rule dict → `RuleChange` → `SoundChangeRule` string → `validate_asca`.
- `validate_asca`: ASCA 0.10.2 via `asca run` on probe wordlist; raises `ASCAValidationError` on failure; skips commented (held-out) rules.
- Validation runs per **corpus rule**, not whole-section-only gate.
- Post-compile validation only — ingest does not reject non-ASCA-shaped corpus fields (ADR-0003).

### Historical fidelity and rule status

- Edit ladder (ADR-0010, ticket 04): class-first safe transforms OK; meaning-changing or ASCA-unrepresentable → `status: skipped`; structural normalisation → `needs-validation` until re-validated; valid-but-inaccurate rewrites forbidden.
- Corpus carries thin optional `status` only; full `reason`/`description`/validator detail live in temporary **validation report** CSV.
- Defined transform classes: apply without per-rule approval. Permanent skip / rare swaps: project owner only.

### Correction workflow

- Steady-state loop: parse HTML → per section/rule compile + `validate_asca` → regenerate YAML → update validation report → fixture samples for changed **rule status** → cluster **failure classes** → implement **class-first** parser/compiler fixes → repeat.
- Class-first transforms live in `IndexDiachronicaParser` (and compile layer as needed). External one-off override file deferred.
- Baseline inventory evidence: 9721 provisional rules, ~57% ok / ~43% fail under earlier ASCA 0.9.3 inventory; top classes include `syntax_other`, `nested_brackets`, `expected_underscore`, `unknown_feature`, `prose_or_expected_arrow`. Re-baseline against cleaned schema + 0.10.2 expected during implementation.

### Package data

- Abbreviation tables under `src/conlanger/data/asca/`: `group_mappings.csv`, `feature_mappings.csv`.
- Brassica data path reserved; Brassica compiler out of scope for this spec.

### Adoption criteria (to define during implementation)

- Not yet specified in wayfinder; spec requires explicit criteria before promoting cleaned YAML over HTML as SoT (e.g. minimum compile-success rate, zero unexplained drift from `raw`, fixture coverage for changed statuses). Implementation should propose metrics and seek owner sign-off.

## Testing Decisions

### Primary seam (proposed — one integration surface)

**HTML file → `IndexDiachronicaParser.parse` → cleaned YAML document → per-section `PhonologicalRuleSet` compile → `validate_asca` per active corpus rule.**

This is the highest seam that exercises ingest, schema shape, abbreviation/feature policy, ASCA compilation, and post-compile validation together — matching the correction workflow loop (ticket 05) and ADR-0003. Tests at this seam should:

- Use real or minimal HTML fixtures mirroring Index Diachronica structure (`<section>`, `<h2>`, `<p class="schg">`).
- Assert corpus rule fields (`input`, `output`, `raw`, `source`, optional `env`/`exception`/`status`) without asserting internal parser function names.
- Build `SoundChangeRule` from compiled section output and call `validate_asca`; expect `True` or documented `ASCAValidationError` / expected skip for `status: skipped`.
- Prefer parametrized cases drawn from `tests/fixtures/sound_change_rules.csv` (`html_extract` for ingest expectations; `asca_guess` for validator-aligned compile cases).

Rationale: lower seams (e.g. `extract_rule_parts` alone, or `validate_asca` alone) already exist and do not prove the corpus pipeline; higher seams (full lexicon evolution) mix unrelated concerns. One end-to-end compile-validation seam minimises cross-module test duplication.

### Supporting seams (existing — do not replace)

- Parser unit/param tests on rule-line splitting and HTML element parsing — prior art: `tests/conlanger/tools/test_IndexDiachronicaParser.py` against `sound_change_rules.csv` `html_extract` rows.
- Validator unit tests — prior art: `tests/conlanger/tools/test_asca_validator.py` against `asca_guess` fixture rows (seed 20260802; 370 expected ok, 130 expected fail).

### What makes a good test

- Assert external behaviour: YAML shape, rendered ASCA strings, validation pass/fail, `status` on corpus rules — not private methods or intermediate CSV layouts unless that artifact is the public contract.
- Preserve auditability: fixture rows keep `id`, `source`, `raw` pointing at HTML lines.
- When **rule status** or compile outcome changes intentionally, update fixtures and note the **failure class** or edit-ladder step that motivated the change.
- Skip tests gracefully when `asca` 0.10.2 binary is absent (match existing validator test pattern).

### Modules under test

- `IndexDiachronicaParser` (ingest)
- `PhonologicalRuleSet` (compile — to be added)
- `SoundChangeRule` / `RuleChange` (ASCA emission)
- `validate_asca` (post-compile gate)
- Optional: thin orchestration script/module for regenerate + validation report (behaviour: produces YAML + CSV from HTML path)

## Out of Scope

- **Generative sound-change sequences** model (GAN / next-in-sequence) — see `.scratch/sound-change-sequences/`.
- Bundling ~100 **preset inventories** — see `.scratch/phoneme-inventories/`.
- Automating PHOIBLE/WALS data prep — see `.scratch/data-processing-pipeline/`.
- Shipping a **Brassica compiler** or full Brassica adoption.
- **Prose-environment mapping** (Index comment paragraphs → structured `env`) — no schema pretence; future spike.
- **Whitespace tokenisation** policy for ASCA inter-segment spacing — deferred from feature-normalisation ticket.
- **Meta-notation** global compile expansion — cluster-driven deferral.
- **Abbreviation table authorship at scale** beyond package CSV + hand-added cluster rows.
- External one-off rule override schema.
- Promoting cleaned YAML to SoT without owner-approved adoption criteria.

## Further Notes

- ASCA validity reference: `.scratch/cleaned-rule-corpus/research/asca-rule-validity.md` (0.10.2; §5 internal pipeline for Python).
- Class letter research: `.scratch/cleaned-rule-corpus/research/asca-class-letter-mappings.md`.
- Inventory baseline: `.scratch/cleaned-rule-corpus/inventory/` (provisional YAML; re-run expected after cleaned schema lands).
- Resolved wayfinder tickets 01–09 are incorporated above; open fog items remain explicitly deferred, not silent requirements.
- `PhonologicalRuleSet` replaces parser-time `str.maketrans` for `{L,G}`-style nested expansions — documented limitation of current parser.
- Re-inventory after major milestones should use ASCA 0.10.2 and cleaned YAML, not `index_diachronica_ai.yml` + 0.9.3, for comparable metrics.
