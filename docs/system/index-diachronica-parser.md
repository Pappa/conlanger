# Index Diachronica parse

Parse-time transforms turn Index Diachronica HTML into an **applier-neutral** rule index YAML. This stage normalizes Index notation toward ASCA-parseable form in index fields (`input`, `output`, `env`, `exception`) while preserving the original HTML line in `raw` for audit ([ADR-0006](./adr/0006-html-source-of-truth-yaml-successor.md), [ADR-0010](./adr/0010-historical-fidelity-class-first-status.md)).

**Primary code:** [`src/conlanger/tools/ingest/parser.py`](../src/conlanger/tools/ingest/parser.py) (`IndexDiachronicaParser(parser_config)`). **Collective subscript expansion:** [`src/conlanger/utils/series.py`](../src/conlanger/utils/series.py) (`apply_series_expansions` from `ParserConfig.series_expansions`). **Correspondence-series indices** stay Index-shaped at parse and expand at [compile](./sound-change-applier.md) via `CompilerConfig`. **Config I/O:** [`config_loaders.py`](../src/conlanger/scripts/config_loaders.py) reads `config/parser/`; **orchestration:** `uv run create_index` → [`create_index.py`](../src/conlanger/scripts/create_index.py).

**Scope:** parse-time only. Class-letter expansion, length marks, ejectives, laryngeal aliases, and multi-step **chain expansion** run at [applier compile](./sound-change-applier.md). Compile validation runs in [validate](./validate.md) ([ADR-0003](./adr/0003-validate-after-applier-compile.md)).

**Related:** [spec](../.scratch/rule-index/spec.md) (Ingest section), [wayfinder map](../.scratch/rule-index/map.md), [ADR-0004](./adr/0004-series-indices-per-section-maps.md) (correspondence-series indices).

---

## Document-level pipeline

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| HTML parse (lxml, non-strict) | implemented | 1 | Real-world Index markup has quirks; lxml tolerates them. | `IndexDiachronicaParser.parse` |
| Section discovery (`//section[@id]`, first `<h2>`) | implemented | 2 | One sound-change section per HTML `<h2>` block. | `IndexDiachronicaParser.parse` |
| Section heading split (`index`, section title) | implemented | 3 | Dotted ancestry key drives hierarchical series lookup ([ADR-0004](./adr/0004-series-indices-per-section-maps.md)). | `parse_section_heading` |
| Citation extraction (first `<p>` after `<h2>`, non-`schg`) | implemented | 4 | Bibliographic provenance per section. | `IndexDiachronicaParser.parse` |
| Section comments (later non-`schg` paragraphs) | implemented | 5 | Editorial prose preserved separately from rules. | `IndexDiachronicaParser.parse`, `note_from_element` |
| Rule extraction (`<p class="schg">` → `parse_rule_element`) | implemented | 6 | Sound-change rules are the index payload. | `IndexDiachronicaParser.parse` |

---

## Per-rule pipeline

Deterministic order is fixed in `parse_rule_element` (`tools/ingest/parser.py`).

### Phase A — HTML text extraction

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| `<sub>` → Unicode subscripts | implemented | A1 | HTML `<sub>1</sub>` must become `₁` before token recognition. | `extract_text_with_subs`, `to_subscript` |
| Whitespace collapse | implemented | A2 | Normalize inter-element whitespace on the rule line. | `strip_whitespace` (via `extract_text_with_subs`) |

### Phase A½ — Working-line overlays (before structural split)

Applied to a **working copy** of the extracted line; **`raw` is stored before any of this** and is never rewritten.

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Index Diachronica correction overlay (by rule id) | implemented | A½1 | Owner-authored Unicode line fixes from `config/parser/index_diachronica_corrections.yml`; replaces extracted text when the HTML **rule id** matches. | `parse_rule_element` |
| Section mapping (`section_mappings`) | implemented | A½2 | Section-scoped token rewrites from `config/parser/parser_config.yml` (e.g. Austronesian `*D` → class letter `D`); ancestry merge via `section_index_prefixes` ([ticket 97](../.scratch/rule-index/issues/97-implement-parser-config-section-mappings.md)). | `apply_section_mappings` |
| Manual mapping (`manual_mappings.yml`) | implemented | A½3 | Owner-authored substring rewrites on the working line; longest `from` first. | `apply_manual_mappings` |
| Quoted-prose detection | implemented | A½4 | Whole-line editorial prose → empty `stages` + `comment`; no further transforms. | `is_quoted_prose_paragraph` |

---

## Per-rule pipeline (continued)

### Phase B — Symbol normalization (before field split)

Applied to the **remainder** after the first-`;` comment peel (see Phase B½); **`raw` is stored before any of this** (see `parse_rule_element`).

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Stem boundary `$` preservation | implemented | B1 | Index `$` (stem) and `%` (syllable) both map to ASCA `$`; placeholder prevents `%→$` from clobbering stem `$`. | `normalize_symbols` |
| Syllable boundary `%` → ASCA `$` | implemented | B2 | Index `%` is syllable boundary; ASCA uses `$`. | `normalize_symbols` |
| Index stress mark `"` (U+201D) → `segment:[+stress]` | implemented | B3 | Index stress notation is phonological, not prose quotes; must become ASCA feature syntax. Prose curly quotes in env are left alone. | `normalize_stress_marks` (via `normalize_symbols`) |

### Phase B½ — First-`;` rule comment peel (before structural split)

After **Manual mapping** and quoted-prose detection; **before** symbol normalization and `extract_rule_parts`. The tail is stored as index **rule comment** as-is (no symbol/feature/IPA/series transforms). Detectors (`sporadic`, trailing glosses, stress, medial) run on the remainder only — not on **rule comment**. Field-level env/exception `;` capture (`apply_semicolon_field_comments`) is retired in favour of this whole-line cut ([ticket 77](../.scratch/rule-index/issues/77-implement-first-semicolon-comment-cut.md)).

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Peel first `;` on working line | implemented | B½1 | Editorial tails (including arrows inside gloss) must not become spurious chain stages. Naive first-`;` anywhere; owner **Manual mapping** rows plant the intended delimiter. | `split_line_semicolon_comment` |
| No `→` in remainder → empty `stages` + optional `comment` | implemented | B½2 | Prose-only or mapping-shaped lines with no rule spine stay in the index; compile validation may fail. | `parse_rule_element` |

### Phase C — Structural field split

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Leading em-dash list marker strip (`— `) | implemented | C1 | Index list formatting, not phonology ([correction pass 16](../.scratch/rule-index/issues/16-correction-pass-em-dash.md)). | `strip_leading_index_list_marker` → `extract_rule_parts` |
| Primary I/O split (first `→`) | implemented | C2 | Core rule shape: `input → output [/ env] [! exception]`. | `split_input_output` |
| Output / env / exception split | implemented | C3 | ASCA env uses `/`; exception via `!`, word `except`, or second `/`. A slash glued to output (`∅/ _#`) is the same delimiter without the preceding space ([pass 82](../.scratch/rule-index/issues/82-correction-pass-output-env-slash-boundary.md)). Lines that omit `/` entirely are Index errata — overlay in `index_diachronica_corrections.yml`, not a parse peel. | `split_post_arrow`, `split_env_exception` |
| Remaining `→` → `>` in field values | implemented | C4 | Chained outputs and embedded arrows must use ASCA `>` ([correction pass 17](../.scratch/rule-index/issues/17-correction-pass-arrow.md)). | `normalize_rule_arrows` (via `extract_rule_parts`) |

**Missing `→`:** still a index rule (spine shape is [ticket 90](../.scratch/rule-index/issues/90-missing-arrow-single-stage.md)); no `status: skipped` unless the **rule id** is listed in `parser_config.yml` `skip_rules`. Boolean `skip` / `skipped` are not index fields.

### Phase D — Class-first field transforms (post-split)

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Uncertainty gloss → `sporadic: true` + `comment` | implemented | D1 | `sporadic`/`sometimes`/`occasionally` are editorial qualifiers, not ASCA syntax ([pass 19](../.scratch/rule-index/issues/19-correction-pass-sporadic-qualifier.md)). Stripped prose captured, not discarded. Runs on remainder only (not **rule comment** seeded at B½). | `apply_sporadic_qualifier` |
| Trailing / embedded editorial gloss strip → `comment` | implemented | D2 | Prose in quotes, parens, semicolon tails breaks ASCA; capture-not-discard ([passes 21, 24, 31, 82](../.scratch/rule-index/map.md)). Internal order: embedded quotes → trailing quotes → trailing parens (including unclosed `(prose…` and `= /ə/` pronunciation glosses; set/matrix parentheticals stay in stages) → semicolon prose. Field-level `;` capture retired (B½). Unclosed strip is stages-only so env/exception can still pair a gloss Index split across `!`. | `apply_trailing_glosses` |
| Env stress phrase normalization (`when stressed` / `when unstressed`) | implemented | D3 | Index env prose → ASCA env with `_` focus prefix ([pass 22](../.scratch/rule-index/issues/22-correction-pass-stress-conditions.md)). | `apply_stress_conditions` |
| Feature matrix synonym replacement (inside `[...]` only) | implemented | D4 | Index→ASCA renames / bundles / **tone** via `config/parser/feature_mappings.yml` (`mapping_kind` includes `tone` → `[tone: N]`; [pass 62](../.scratch/rule-index/issues/62-correction-pass-tone-features.md)). Unmapped names left literal for `unknown_feature` clustering. | `apply_feature_mappings` |
| Collective subscript expansion (`series_expansions`) | implemented | D5 | Fan out `Xₓ` collectives from `config/parser/parser_config.yml` ([grill 73](../.scratch/rule-index/issues/73-grill-series-mapping-config-sot.md)). Correspondence-series indices (`h₁`, `s₁`, …) stay literal until compile. | `apply_series_expansions` |

### Phase E — Rule assembly (post-transform)

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Multi-step chains (`a > b > c`) | compile-time | — | One index row per HTML line; adjacent **stages** expand at compile ([`expand_chained_index_rule`](../src/conlanger/tools/compile/asca/chains.py)). Chains **with** env/exception stay one row; env/exception attach to each emitted step. | `SoundChangeRule` / compile pipeline |
| Attach provenance (`raw`, `source`, optional `sporadic`) | implemented | E1 | Every emitted rule carries HTML line ref and original Index text. | `parse_rule_element` |

### Phase F — Section post-pass (after per-line extract)

| Step | Status | Order | Rationale | Code |
| --- | --- | ---: | --- | --- |
| Catch-all `/ else` → complementary `exception` | implemented | F1 | Index default branch is not an env; when the previous rule has `env` and no `exception`, omit `env` and set `exception` to that env ([pass 53](../.scratch/rule-index/issues/53-correction-pass-prose-env-else.md)). Deferred: prev with both env+exception, neither, or else-after-else. | `resolve_catch_all_else_rules` (in `parse`) |
| Env medial phrase normalization (`medial` / `medially`) | implemented | F2 | Index word-internal prose → `env: _` + boundary `exception: :{#_, _#}:` ([pass 55](../.scratch/rule-index/issues/55-correction-pass-prose-env-medial.md)). Defer env+existing-exception merge. | `apply_medial_env_conditions` |
| Section skip (`skip_sections` in `parser_config.yml`) | implemented | F3 | Owner-curated hold-out when Index misrepresents source material; parse extracts rules normally, sets `status: skipped` on the section object; compile and inventory validation bypass those rules ([ticket 78](../.scratch/rule-index/issues/78-implement-parser-config-section-skip.md)). Distinct from per-rule `status: skipped` ([ticket 89](../.scratch/rule-index/issues/89-unify-status-skipped.md)). | `IndexDiachronicaParser.parse`, `DiachronicSeries`, `index_inventory` |
| Rule skip (`skip_rules` in `parser_config.yml`) | implemented | F4 | Owner-curated hold-out for individual **rule id**s; sets `status: skipped` on the index rule. | `IndexDiachronicaParser.parse_rule_element` |

---

## `config/parser/parser_config.yml`

| Key | Purpose |
| --- | --- |
| `ipa_mappings.confidence` | Which `config/parser/ipa_mappings.yml` confidence levels apply at parse (`None` = all rows) |
| `series_expansions` | Collective subscript fan-out (`Hₓ` → `h₁, h₂, h₃`, …) |
| `section_mappings` | Section-scoped token rewrites (`"10.1": {"*D": "D", …}`); applies to matching section and all descendants; child row overrides ancestor for the same `from` key ([ticket 97](../.scratch/rule-index/issues/97-implement-parser-config-section-mappings.md)) |
| `skip_sections` | List of `{id, reason}` — `id` matches section `index`; `reason` is operator documentation only. Listed sections gain `status: skipped` in parsed YAML. |
| `skip_rules` | List of `{id, reason}` — `id` matches HTML **rule id**; `reason` becomes optional index `comment`. Listed rules gain `status: skipped`. |

---

## Planned / deferred parse-time work

| Step | Status | Order | Rationale |
| --- | --- | --- | --- |
| Positional slots (`C₁C₂ → C₂`) | planned (compile-time) | TBD | ASCA reference syntax (`C=1`, bare `2`) is applier-specific; index stays Index-shaped. See [positional-slots research](../.scratch/rule-index/research/positional-slots-and-identity-subscripts.md). |
| Identity subscripts (`V₀V₀ → V₀`) | planned (compile-time) | TBD | Same policy as positional slots. |
| Class letter expansion (`S`, `A`, `R`, …) | implemented at **compile**, not parse | — | Avoid baking ASCA syntax into applier-neutral YAML ([pass 14](../.scratch/rule-index/issues/14-correction-pass-unknown-grouping.md)). |
| Feature matrix Phase 2+ (remaining place/manner, pitch accent, …) | planned | TBD | Tone pass shipped ([62](../.scratch/rule-index/issues/62-correction-pass-tone-features.md)); other deferred features stay inventory-driven. |
| Whitespace tokenisation inside brackets | deferred | TBD | Most polarity-space cases handled by feature regex; multi-word tone names are CSV keys with spaces. |
| Meta-notation (`X0`, `Xn`, retroflex marks, repetition groups) | deferred (cluster-driven) | TBD | No evidence-based ASCA expansion without inventory clustering. |
| Section-local abbreviations (`TŠ`, uppercase `S₁`) | partial (cluster-driven) | TBD | Owner-curated `section_mappings` rows at parse ([ticket 97](../.scratch/rule-index/issues/97-implement-parser-config-section-mappings.md)); bulk authoring inventory-driven. |
| Global abbreviation table authorship | removed | — | Document-level `abbreviations` key dropped from parse output; section mappings are config-driven, not stored tables. |
| Edge-split / parse-time auto-skip for unrepresentable lines | removed | — | `status: skipped` is config-only ([ticket 89](../.scratch/rule-index/issues/89-unify-status-skipped.md)); missing-arrow / gloss-only lines stay in parse → compile → validate. |
| Prose-environment mapping (comment paragraphs → structured `env`) | planned (spike) | TBD | `comment` field captures qualifiers; structured env from prose not specified. |
| Dedicated smart-quote normalizer | partial | TBD | Embedded/trailing `"`/`"` stripped as glosses at parse ([pass 24](../.scratch/rule-index/issues/24-correction-pass-smart-quotes.md)); typographic apostrophe `'` → ejective at **compile**. |
| Correspondence-series index mappings | compile-time | TBD | Section-scoped rows authored in `config/compile/asca/compiler_config.yml` ([ticket 75](../.scratch/rule-index/issues/75-implement-compiler-config-series-mappings.md)); PIE laryngeals seeded in `global`. |

---

## Pipeline placement

| Stage | Doc |
| --- | --- |
| **Index Diachronica parse** (this page) | — |
| Applier compile | [sound-change-applier.md](./sound-change-applier.md) |
| Validate | [validate.md](./validate.md) |

See also [SYSTEM.md](./SYSTEM.md#pipeline-stages-new).
