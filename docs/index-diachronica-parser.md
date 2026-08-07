# Index Diachronica parse

Parse-time transforms turn Index Diachronica HTML into an **applier-neutral** rule corpus YAML. This stage normalizes Index notation toward ASCA-parseable form in corpus fields (`input`, `output`, `env`, `exception`) while preserving the original HTML line in `raw` for audit ([ADR-0006](./adr/0006-html-source-of-truth-yaml-successor.md), [ADR-0010](./adr/0010-historical-fidelity-class-first-status.md)).

**Primary code:** [`src/conlanger/tools/parsers.py`](../src/conlanger/tools/parsers.py) (`IndexDiachronicaParser`). **Series expansion:** [`src/conlanger/tools/series_mappings.py`](../src/conlanger/tools/series_mappings.py). **Orchestration:** `uv run regenerate_corpus` → [`regenerate_corpus.py`](../src/conlanger/scripts/regenerate_corpus.py).

**Scope:** parse-time only. Class-letter expansion, length marks, ejectives, and laryngeal aliases run at [applier compile](./sound-change-applier.md). Compile validation runs after that ([ADR-0003](./adr/0003-validate-after-applier-compile.md)).

**Related:** [spec](../.scratch/cleaned-rule-corpus/spec.md) (Ingest section), [wayfinder map](../.scratch/cleaned-rule-corpus/map.md), [ADR-0004](./adr/0004-series-indices-per-section-maps.md) (correspondence-series indices).

---

## Document-level pipeline

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| HTML parse (lxml, non-strict) | implemented | 1 | Real-world Index markup has quirks; lxml tolerates them. | `IndexDiachronicaParser.parse` |
| Section discovery (`//section[@id]`, first `<h2>`) | implemented | 2 | One sound-change section per HTML `<h2>` block. | `IndexDiachronicaParser.parse` |
| Section heading split (`index`, section title) | implemented | 3 | Dotted ancestry key drives hierarchical series lookup ([ADR-0004](./adr/0004-series-indices-per-section-maps.md)). | `parse_section_heading` |
| Citation extraction (first `<p>` after `<h2>`, non-`schg`) | implemented | 4 | Bibliographic provenance per section. | `IndexDiachronicaParser.parse` |
| Section comments (later non-`schg` paragraphs) | implemented | 5 | Editorial prose preserved separately from rules. | `IndexDiachronicaParser.parse`, `note_from_element` |
| Rule extraction (`<p class="schg">` → `parse_rule_element`) | implemented | 6 | Sound-change rules are the corpus payload. | `IndexDiachronicaParser.parse` |
| Section `abbreviations` table (from series mappings) | implemented | 7 | Hierarchical token→target map for correspondence-series; populated from `data/asca/series_mappings.csv`, not prose inference. | `section_abbreviations_for_index`, `IndexDiachronicaParser.parse` |
| Global `abbreviations` | planned | 8 | Schema slot exists; global Key-to-Abbreviations not authored at ingest yet. | `IndexDiachronicaParser.abbreviations` (returns `{}`) |

---

## Per-rule pipeline

Deterministic order is fixed in `parse_rule_element` (`parsers.py`).

### Phase A — HTML text extraction

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| `<sub>` → Unicode subscripts | implemented | A1 | HTML `<sub>1</sub>` must become `₁` before token recognition. | `extract_text_with_subs`, `to_subscript` |
| Whitespace collapse | implemented | A2 | Normalize inter-element whitespace on the rule line. | `strip_whitespace` (via `extract_text_with_subs`) |

### Phase B — Symbol normalization (before field split)

Applied to the working copy only; **`raw` is stored before this** (see `parse_rule_element`).

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Stem boundary `$` preservation | implemented | B1 | Index `$` (stem) and `%` (syllable) both map to ASCA `$`; placeholder prevents `%→$` from clobbering stem `$`. | `normalize_symbols` |
| Syllable boundary `%` → ASCA `$` | implemented | B2 | Index `%` is syllable boundary; ASCA uses `$`. | `normalize_symbols` |
| Index stress mark `"` (U+201D) → `segment:[+stress]` | implemented | B3 | Index stress notation is phonological, not prose quotes; must become ASCA feature syntax. Prose curly quotes in env are left alone. | `normalize_stress_marks` (via `normalize_symbols`) |

### Phase C — Structural field split

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Leading em-dash list marker strip (`— `) | implemented | C1 | Index list formatting, not phonology ([correction pass 16](../.scratch/cleaned-rule-corpus/issues/16-correction-pass-em-dash.md)). | `strip_leading_index_list_marker` → `extract_rule_parts` |
| Primary I/O split (first `→`) | implemented | C2 | Core rule shape: `input → output [/ env] [! exception]`. | `split_input_output` |
| Output / env / exception split | implemented | C3 | ASCA env uses `/`; exception via `!`, word `except`, or second `/`. | `split_post_arrow`, `split_env_exception` |
| Remaining `→` → `>` in field values | implemented | C4 | Chained outputs and embedded arrows must use ASCA `>` ([correction pass 17](../.scratch/cleaned-rule-corpus/issues/17-correction-pass-arrow.md)). | `normalize_rule_arrows` (via `extract_rule_parts`) |

**Missing `→`:** returns a skip-shaped dict with empty I/O and `"skipped": "missing separator '→'"` — not yet wired to corpus `status: skipped` schema.

### Phase D — Class-first field transforms (post-split)

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Uncertainty gloss → `sporadic: true` + `comment` | implemented | D1 | `sporadic`/`sometimes` are editorial qualifiers, not ASCA syntax ([pass 19](../.scratch/cleaned-rule-corpus/issues/19-correction-pass-sporadic-qualifier.md)). Stripped prose captured, not discarded. | `apply_sporadic_qualifier` |
| Trailing / embedded editorial gloss strip → `comment` | implemented | D2 | Prose in quotes, parens, semicolon tails breaks ASCA; capture-not-discard ([passes 21, 24, 31](../.scratch/cleaned-rule-corpus/map.md)). Internal order: embedded quotes → trailing quotes → trailing parens → semicolon prose. | `apply_trailing_glosses` |
| Env stress phrase normalization (`when stressed` / `when unstressed`) | implemented | D3 | Index env prose → ASCA env with `_` focus prefix ([pass 22](../.scratch/cleaned-rule-corpus/issues/22-correction-pass-stress-conditions.md)). | `apply_stress_conditions` |
| Feature matrix synonym replacement (inside `[...]` only) | implemented (Phase 1) | D4 | Safe 1:1 Index→ASCA renames via `data/asca/feature_mappings.csv` (5 seed rows; [pass 32](../.scratch/cleaned-rule-corpus/issues/32-correction-pass-unknown-feature.md)). Unmapped names left literal for `unknown_feature` clustering. | `apply_feature_mappings` |
| Correspondence-series + collective subscript expansion | implemented (partial coverage) | D5 | When `series_mappings.csv` has a section hit, rewrite tokens to ASCA-parseable targets; unmapped tokens stay literal ([ADR-0004](./adr/0004-series-indices-per-section-maps.md), [tickets 26–28](../.scratch/cleaned-rule-corpus/issues/26-parse-time-correspondence-series-indices.md)). Positional (`C₁`) and identity (`V₀`) tokens are **explicitly skipped** by `in_scope_series_token`. | `apply_series_mappings` |

### Phase E — Rule expansion (post-transform)

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Chain split (no env/exception) | implemented | E1 | `a > b > c` without env becomes sequential single-step rules ([pass 18](../.scratch/cleaned-rule-corpus/issues/18-correction-pass-chain-split.md)). Chains **with** env/exception stay one row. | `expand_chained_rule_parts` |
| Attach provenance (`raw`, `source`, optional `sporadic`) | implemented | E2 | Every emitted rule carries HTML line ref and original Index text. | `parse_rule_element` |

---

## Planned / deferred parse-time work

| Step | Status | Order | Rationale |
| --- | --- | --- | --- |
| Positional slots (`C₁C₂ → C₂`) | planned (compile-time) | TBD | ASCA reference syntax (`C=1`, bare `2`) is applier-specific; corpus stays Index-shaped. See [positional-slots research](../.scratch/cleaned-rule-corpus/research/positional-slots-and-identity-subscripts.md). |
| Identity subscripts (`V₀V₀ → V₀`) | planned (compile-time) | TBD | Same policy as positional slots. |
| Class letter expansion (`S`, `A`, `R`, …) | implemented at **compile**, not parse | — | Avoid baking ASCA syntax into applier-neutral YAML ([pass 14](../.scratch/cleaned-rule-corpus/issues/14-correction-pass-unknown-grouping.md)). |
| Feature matrix Phase 2+ (place bundles, suprasegmentals, tones, …) | planned | TBD | Phase 1 shipped (5 rows); ~87 deferred features need research. |
| Whitespace tokenisation inside brackets | deferred | TBD | `[+high tone]`, `[- glottalized]` need space normalisation before lookup. |
| Meta-notation (`X0`, `Xn`, retroflex marks, repetition groups) | deferred (cluster-driven) | TBD | No evidence-based ASCA expansion without inventory clustering. |
| Section-local abbreviations (`TŠ`, uppercase `S₁`) | deferred (cluster-driven) | TBD | Index global Key insufficient; hand-added rows when clusters warrant. |
| Global abbreviation table authorship | planned | TBD | `abbreviations()` returns `{}`; hierarchical section tables partially populated via series mappings only. |
| Edge-split / `status: skipped` for unrepresentable lines | deferred | TBD | ADR-0005 interim skip policy deferred until post-correction triage. |
| Prose-environment mapping (comment paragraphs → structured `env`) | planned (spike) | TBD | `comment` field captures qualifiers; structured env from prose not specified. |
| Dedicated smart-quote normalizer | partial | TBD | Embedded/trailing `"`/`"` stripped as glosses at parse ([pass 24](../.scratch/cleaned-rule-corpus/issues/24-correction-pass-smart-quotes.md)); typographic apostrophe `'` → ejective at **compile**. |
| Series mappings full coverage | in progress | TBD | HTML extraction done ([ticket 28](../.scratch/cleaned-rule-corpus/issues/28-extract-series-mappings-from-html.md)); gaps remain per coverage backlog. |

---

## Series mappings module (parse-adjacent)

Not part of the per-rule transform chain, but feeds parse-time expansion:

| Component | Status | Role | Code |
| --- | --- | --- | --- |
| HTML → CSV extraction | implemented | Builds `data/asca/series_mappings.csv` from citations, tables, parallel/singleton rule I/O. | `update_series_mappings_from_html` via `uv run regenerate_corpus --update-series-mappings` |
| Hierarchical lookup | implemented | Longest-prefix section match; optional `*` global fallback. | `lookup_series_target`, `section_index_prefixes` |
| Collective subscript synthesis | implemented | `Xₓ` → `{member targets}` when ≥2 members declared in citation. | `_collective_rows_for_section` |
| ASCA digit segment fallback | implemented | `h₁` → `h1`; grouping-letter collision → `f1`. | `asca_digit_segment` |
| Coverage audit / report | implemented | Tracks in-scope vs out-of-scope subscript tokens. | `audit_series_extraction`, `write_coverage_report` |

---

## Pipeline placement

| Stage | Doc |
| --- | --- |
| **Index Diachronica parse** (this page) | — |
| Applier-neutral corpus validation | [applier-neutral-corpus-validation.md](./applier-neutral-corpus-validation.md) |
| Applier compile | [sound-change-applier.md](./sound-change-applier.md) |
| Compile validation | [sound-change-applier.md#compile-validation](./sound-change-applier.md#compile-validation) |

See also [SYSTEM.md](./SYSTEM.md#pipeline-stages-new).
