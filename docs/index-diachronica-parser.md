# Index Diachronica parse

Parse-time transforms turn Index Diachronica HTML into an **applier-neutral** rule corpus YAML. This stage normalizes Index notation toward ASCA-parseable form in corpus fields (`input`, `output`, `env`, `exception`) while preserving the original HTML line in `raw` for audit ([ADR-0006](./adr/0006-html-source-of-truth-yaml-successor.md), [ADR-0010](./adr/0010-historical-fidelity-class-first-status.md)).

**Primary code:** [`src/conlanger/tools/ingest/parser.py`](../src/conlanger/tools/ingest/parser.py) (`IndexDiachronicaParser`). **Collective subscript expansion:** [`src/conlanger/utils/series.py`](../src/conlanger/utils/series.py) (`apply_series_expansions` from `data/parser_config.yml`). **Correspondence-series indices** stay Index-shaped at parse and expand at [compile](./sound-change-applier.md) via `data/compiler_config.yml`. **Orchestration:** `uv run regenerate_corpus` → [`regenerate_corpus.py`](../src/conlanger/scripts/regenerate_corpus.py).

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
| Global `abbreviations` | planned | 7 | Schema slot exists; global Key-to-Abbreviations not authored at ingest yet. | `IndexDiachronicaParser.abbreviations` (returns `{}`) |

---

## Per-rule pipeline

Deterministic order is fixed in `parse_rule_element` (`tools/ingest/parser.py`).

### Phase A — HTML text extraction

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| `<sub>` → Unicode subscripts | implemented | A1 | HTML `<sub>1</sub>` must become `₁` before token recognition. | `extract_text_with_subs`, `to_subscript` |
| Whitespace collapse | implemented | A2 | Normalize inter-element whitespace on the rule line. | `strip_whitespace` (via `extract_text_with_subs`) |

### Phase B — Symbol normalization (before field split)

Applied to the **remainder** after the first-`;` comment peel (see Phase B½); **`raw` is stored before any of this** (see `parse_rule_element`).

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Stem boundary `$` preservation | implemented | B1 | Index `$` (stem) and `%` (syllable) both map to ASCA `$`; placeholder prevents `%→$` from clobbering stem `$`. | `normalize_symbols` |
| Syllable boundary `%` → ASCA `$` | implemented | B2 | Index `%` is syllable boundary; ASCA uses `$`. | `normalize_symbols` |
| Index stress mark `"` (U+201D) → `segment:[+stress]` | implemented | B3 | Index stress notation is phonological, not prose quotes; must become ASCA feature syntax. Prose curly quotes in env are left alone. | `normalize_stress_marks` (via `normalize_symbols`) |

### Phase B½ — First-`;` rule comment peel (before structural split)

After **Manual mapping** and quoted-prose skip; **before** symbol normalization and `extract_rule_parts`. The tail is stored as corpus **rule comment** as-is (no symbol/feature/IPA/series transforms). Detectors (`sporadic`, trailing glosses, stress, medial) run on the remainder only — not on **rule comment**. Field-level env/exception `;` capture (`apply_semicolon_field_comments`) is retired in favour of this whole-line cut ([ticket 77](../.scratch/cleaned-rule-corpus/issues/77-implement-first-semicolon-comment-cut.md)).

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Peel first `;` on working line | implemented | B½1 | Editorial tails (including arrows inside gloss) must not become spurious chain stages. Naive first-`;` anywhere; owner **Manual mapping** rows plant the intended delimiter. | `split_line_semicolon_comment` |
| No `→` in remainder → skipped + comment | implemented | B½2 | Prose-only or mapping-shaped lines with no rule spine. | `parse_rule_element` |

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
| Uncertainty gloss → `sporadic: true` + `comment` | implemented | D1 | `sporadic`/`sometimes`/`occasionally` are editorial qualifiers, not ASCA syntax ([pass 19](../.scratch/cleaned-rule-corpus/issues/19-correction-pass-sporadic-qualifier.md)). Stripped prose captured, not discarded. Runs on remainder only (not **rule comment** seeded at B½). | `apply_sporadic_qualifier` |
| Trailing / embedded editorial gloss strip → `comment` | implemented | D2 | Prose in quotes, parens, semicolon tails breaks ASCA; capture-not-discard ([passes 21, 24, 31](../.scratch/cleaned-rule-corpus/map.md)). Internal order: embedded quotes → trailing quotes → trailing parens → semicolon prose. Field-level `;` capture retired (B½). | `apply_trailing_glosses` |
| Env stress phrase normalization (`when stressed` / `when unstressed`) | implemented | D3 | Index env prose → ASCA env with `_` focus prefix ([pass 22](../.scratch/cleaned-rule-corpus/issues/22-correction-pass-stress-conditions.md)). | `apply_stress_conditions` |
| Feature matrix synonym replacement (inside `[...]` only) | implemented | D4 | Index→ASCA renames / bundles / **tone** via `data/asca/feature_mappings.csv` (`mapping_kind` includes `tone` → `[tone: N]`; [pass 62](../.scratch/cleaned-rule-corpus/issues/62-correction-pass-tone-features.md)). Unmapped names left literal for `unknown_feature` clustering. | `apply_feature_mappings` |
| Collective subscript expansion (`series_expansions`) | implemented | D5 | Fan out `Xₓ` collectives from `data/parser_config.yml` ([grill 73](../.scratch/cleaned-rule-corpus/issues/73-grill-series-mapping-config-sot.md)). Correspondence-series indices (`h₁`, `s₁`, …) stay literal until compile. | `apply_series_expansions` |

### Phase E — Rule expansion (post-transform)

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Chain split (no env/exception) | implemented | E1 | `a > b > c` without env becomes sequential single-step rules ([pass 18](../.scratch/cleaned-rule-corpus/issues/18-correction-pass-chain-split.md)). Chains **with** env/exception stay one row. | `expand_chained_rule_parts` |
| Attach provenance (`raw`, `source`, optional `sporadic`) | implemented | E2 | Every emitted rule carries HTML line ref and original Index text. | `parse_rule_element` |

### Phase F — Section post-pass (after per-line extract)

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Catch-all `/ else` → complementary `exception` | implemented | F1 | Index default branch is not an env; when the previous rule has `env` and no `exception`, omit `env` and set `exception` to that env ([pass 53](../.scratch/cleaned-rule-corpus/issues/53-correction-pass-prose-env-else.md)). Deferred: prev with both env+exception, neither, or else-after-else. | `resolve_catch_all_else_rules` (in `parse`) |
| Env medial phrase normalization (`medial` / `medially`) | implemented | F2 | Index word-internal prose → `env: _` + boundary `exception: :{#_, _#}:` ([pass 55](../.scratch/cleaned-rule-corpus/issues/55-correction-pass-prose-env-medial.md)). Defer env+existing-exception merge. | `apply_medial_env_conditions` |
| Section skip (`skip_sections` in `parser_config.yml`) | implemented | F3 | Owner-curated hold-out when Index misrepresents source material; parse extracts rules normally, sets `skipped: true` on the section object; compile and inventory validation bypass those rules ([ticket 78](../.scratch/cleaned-rule-corpus/issues/78-implement-parser-config-section-skip.md)). Distinct from per-rule `status: skipped`. | `IndexDiachronicaParser.parse`, `DiachronicSeries`, `corpus_inventory` |

---

## `data/parser_config.yml`

| Key | Purpose |
| --- | --- |
| `ipa_mappings.confidence` | Which `ipa_mappings.csv` confidence levels apply at parse |
| `series_expansions` | Collective subscript fan-out (`Hₓ` → `h₁, h₂, h₃`, …) |
| `skip_sections` | List of `{id, reason}` — `id` matches section `index`; `reason` is operator documentation only. Listed sections gain `skipped: true` in parsed YAML. |

---

## Planned / deferred parse-time work

| Step | Status | Order | Rationale |
| --- | --- | --- | --- |
| Positional slots (`C₁C₂ → C₂`) | planned (compile-time) | TBD | ASCA reference syntax (`C=1`, bare `2`) is applier-specific; corpus stays Index-shaped. See [positional-slots research](../.scratch/cleaned-rule-corpus/research/positional-slots-and-identity-subscripts.md). |
| Identity subscripts (`V₀V₀ → V₀`) | planned (compile-time) | TBD | Same policy as positional slots. |
| Class letter expansion (`S`, `A`, `R`, …) | implemented at **compile**, not parse | — | Avoid baking ASCA syntax into applier-neutral YAML ([pass 14](../.scratch/cleaned-rule-corpus/issues/14-correction-pass-unknown-grouping.md)). |
| Feature matrix Phase 2+ (remaining place/manner, pitch accent, …) | planned | TBD | Tone pass shipped ([62](../.scratch/cleaned-rule-corpus/issues/62-correction-pass-tone-features.md)); other deferred features stay inventory-driven. |
| Whitespace tokenisation inside brackets | deferred | TBD | Most polarity-space cases handled by feature regex; multi-word tone names are CSV keys with spaces. |
| Meta-notation (`X0`, `Xn`, retroflex marks, repetition groups) | deferred (cluster-driven) | TBD | No evidence-based ASCA expansion without inventory clustering. |
| Section-local abbreviations (`TŠ`, uppercase `S₁`) | deferred (cluster-driven) | TBD | Index global Key insufficient; hand-added rows when clusters warrant. |
| Global abbreviation table authorship | planned | TBD | `abbreviations()` returns `{}`. |
| Edge-split / `status: skipped` for unrepresentable lines | deferred | TBD | ADR-0005 interim skip policy deferred until post-correction triage. |
| Prose-environment mapping (comment paragraphs → structured `env`) | planned (spike) | TBD | `comment` field captures qualifiers; structured env from prose not specified. |
| Dedicated smart-quote normalizer | partial | TBD | Embedded/trailing `"`/`"` stripped as glosses at parse ([pass 24](../.scratch/cleaned-rule-corpus/issues/24-correction-pass-smart-quotes.md)); typographic apostrophe `'` → ejective at **compile**. |
| Correspondence-series index mappings | compile-time | TBD | Section-scoped rows authored in `data/compiler_config.yml` ([ticket 75](../.scratch/cleaned-rule-corpus/issues/75-implement-compiler-config-series-mappings.md)); PIE laryngeals seeded in `global`. |

---

## Pipeline placement

| Stage | Doc |
| --- | --- |
| **Index Diachronica parse** (this page) | — |
| Applier-neutral corpus validation | [applier-neutral-corpus-validation.md](./applier-neutral-corpus-validation.md) |
| Applier compile | [sound-change-applier.md](./sound-change-applier.md) |
| Compile validation | [sound-change-applier.md#compile-validation](./sound-change-applier.md#compile-validation) |

See also [SYSTEM.md](./SYSTEM.md#pipeline-stages-new).
