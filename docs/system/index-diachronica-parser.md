# Index Diachronica parse

Parse-time transforms turn Index Diachronica HTML into an **applier-neutral** rule index YAML. Each **corpus rule** carries **`stages`** (ordered opaque spine strings), optional **`env`** / **`exception`** (string or **`IndexContext`**), **`raw`**, **`rule id`**, and **`source`** — not YAML `input`/`output` keys ([ADR-0011](../adr/0011-index-rule-stages.md)). Parse normalizes Index surface and project phonology in those fields; applier-specific syntax is deferred to [compile](./sound-change-applier.md). The HTML line is preserved in **`raw`** for audit ([ADR-0006](../adr/0006-html-source-of-truth-yaml-successor.md), [ADR-0010](../adr/0010-historical-fidelity-class-first-status.md), [ADR-0016](../adr/0016-parse-pipeline-order-and-raw-semantics.md)).

**Primary code:** `[src/conlanger/ingest/parser.py](../src/conlanger/ingest/parser.py)` (`IndexDiachronicaParser(parser_config)`); parse output is assembled as pydantic `Index` / `IndexSection` / `IndexRule` / `IndexContext` (`[index_models.py](../src/conlanger/ingest/models/index_models.py)`, [ADR-0017](../adr/0017-structured-env-exception-indexcontext.md)). `parse()` returns one document mapping with top-level `name` (`"Index Diachronica"`) and `sections`; serialization uses `Index.model_dump(exclude_none=True, mode="python")` at that boundary only. **Bracket-aware scanning** (nested `{…}`, optional `(…)`, matrices `[…]`, comma/space splits): `[src/conlanger/utils/bracket_scanner.py](../src/conlanger/utils/bracket_scanner.py)` (`BracketScanner`, `split_outside_brackets`). **Nested set flatten** (env / exception / stages): `[flatten_nested_sets.py](../src/conlanger/ingest/utils/flatten_nested_sets.py)`. **Collective subscript expansion:** `[src/conlanger/ingest/utils/series.py](../src/conlanger/ingest/utils/series.py)` (`apply_series_expansions` from `ParserConfig.series_expansions`). **Correspondence-series indices** stay Index-shaped at parse and expand at [compile](./sound-change-applier.md) via `CompilerConfig`. **Config I/O:** `[config_loaders.py](../src/conlanger/scripts/config_loaders.py)` reads `config/parser/`; **orchestration:** `uv run create_index` → `[create_index.py](../src/conlanger/scripts/create_index.py)`.

**Scope:** parse-time only. Class-letter expansion, length marks, ejectives, laryngeal aliases, and multi-step **chain expansion** run at [applier compile](./sound-change-applier.md). Compile validation runs in [validate](./validate.md) ([ADR-0003](../adr/0003-validate-after-applier-compile.md)).

**Related:** [ADR-0004](../adr/0004-series-indices-per-section-maps.md) (correspondence-series indices), [GLOSSARY.md](../../GLOSSARY.md).

**Package imports:** `ingest` may import `utils` only (not `compile`); `compile` may import `ingest` and `utils`; shared helpers such as [`bracket_scanner.py`](../src/conlanger/utils/bracket_scanner.py) live under `utils`. Applier-neutral position projection for parse policies: [`index_context_project.py`](../src/conlanger/ingest/utils/index_context_project.py).

### Feature name mappings (parse vs compile)

Distinctive-feature **names** inside postfix `[...]` matrices may be normalised at parse to **canonical cleaned-index** names (`config/parser/feature_mappings.yml`). **ASCA** feature geometry, tone rows, and polarity inverts live at compile (`config/compile/asca/feature_mappings.yml` — planned split per ticket 148). Bracket syntax stays applier-neutral in YAML; colon host matrices are compile-only. Index `%` / `$` and stress marks follow the same tier policy (Index symbols in SoT; atomic `%`/`$` compile migration in ticket 153).

---



## Document-level pipeline


| Step                                                        | Status      | Order | Rationale                                                                                                          | Code                                                |
| ----------------------------------------------------------- | ----------- | ----- | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------- |
| HTML load + `<sub>` normalisation (lxml, non-strict)        | implemented | 1     | Real-world Index markup has quirks; lxml tolerates them; disk I/O stays in scripts.                                | `load_html_document`, `create_index`                |
| DOM → index document                                        | implemented | 2     | Walk loaded tree; `source_file` names provenance in rule `source`.                                                 | `IndexDiachronicaParser.parse`                      |
| Section discovery (`//section[@id]`, first `<h2>`)          | implemented | 3     | One sound-change section per HTML `<h2>` block.                                                                    | `IndexDiachronicaParser.parse`                      |
| Section heading split (`index`, section title)              | implemented | 4     | Dotted ancestry key drives hierarchical series lookup ([ADR-0004](../adr/0004-series-indices-per-section-maps.md)). | `parse_section_heading`                             |
| Citation extraction (first `<p>` after `<h2>`, non-`schg`)  | implemented | 5     | Bibliographic provenance per section.                                                                              | `IndexDiachronicaParser.parse`                      |
| Rule extraction (`<p class="schg">` → `parse_rule_element`) | implemented | 6     | Sound-change rules are the index payload.                                                                          | `IndexDiachronicaParser.parse`                      |


---



## Per-rule pipeline

Deterministic order is fixed in `parse_rule_string` (`ingest/parser.py`).

### Phase A — HTML text extraction


| Step                                                  | Status      | Order | Rationale                                                                                                                                                                                                                                                                                                                                                                                                    | Code                                                                  |
| ----------------------------------------------------- | ----------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| `<sub>` → Unicode subscripts                          | implemented | A1    | HTML `<sub>1</sub>` must become `₁` before token recognition.                                                                                                                                                                                                                                                                                                                                                | `extract_element_text`, `to_subscript`                              |
| Whitespace collapse                                   | implemented | A2    | Normalize inter-element whitespace on the rule line.                                                                                                                                                                                                                                                                                                                                                         | `strip_whitespace` (via `extract_element_text`)                     |
| Section skip (`skip_sections` in `parser_config.yml`) | implemented | F3    | Owner-curated hold-out when Index misrepresents source material; parse extracts rules normally, sets `status: skipped` on the section object; compile and inventory validation bypass those rules (ticket 78). Distinct from per-rule `status: skipped` (ticket 89). | `IndexDiachronicaParser.parse`, `DiachronicSeries`, `index_inventory` |
| Rule skip (`skip_rules` in `parser_config.yml`)       | implemented | F4    | Owner-curated hold-out for individual **rule id**s; sets `status: skipped` on the index rule.                                                                                                                                                                                                                                                                                                                | `IndexDiachronicaParser.parse_rule_element`                           |




### Phase A½ — Working-line overlays (before structural split)

Applied to a **working copy** of the extracted line; `raw` **is stored before any of this** and is never rewritten.


| Step                                              | Status      | Order | Rationale                                                                                                                                                                                                                                                  | Code                             |
| ------------------------------------------------- | ----------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Index Diachronica correction overlay (by rule id) | implemented | A½1   | Owner-authored Unicode line fixes from `config/parser/index_corrections.yml` on the **working line** when the HTML **rule id** matches; `raw` stays HTML-only ([ADR-0016](../adr/0016-parse-pipeline-order-and-raw-semantics.md)).              | `IndexRule.update_rule` in `parse_rule_string` |
| Manual mapping (`manual_mappings.yml`)            | implemented | A½2   | Owner-authored substring rewrites on the working line; **definition order** (not longest-match).                                                                                                                                                             | `apply_manual_mappings`          |
| Section mapping (`section_mappings`)              | implemented | A½3   | Section-scoped token rewrites from `config/parser/parser_config.yml` (e.g. Austronesian `*D` → class letter `D`); ancestry merge via `section_index_prefixes` (ticket 97). | `apply_section_mappings`         |
| Quoted-prose detection                            | implemented | A½4   | Whole-line editorial prose → empty `stages` + `comment`; no further transforms.                                                                                                                                                                            | `is_quoted_prose_paragraph`      |


---



## Per-rule pipeline (continued)



### Phase B — Symbol normalization (before field split)

Applied to the **remainder** after the first-`;` comment partition (see Phase B½); `raw` **is stored before any of this** (see `parse_rule_element`).


| Step                                                 | Status      | Order | Rationale                                                                                                                           | Code                                               |
| ---------------------------------------------------- | ----------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Index `%` / stem `$` in SoT                          | implemented | B1–B2 | Syllable boundary `%` and stem `$` stay Index-shaped in parsed YAML; ASCA `$` projection runs at compile ([sound-change-applier.md](./sound-change-applier.md)). | —                                                  |
| Index stress mark `"` (U+201D) → `segment:[+stress]` | implemented | B3    | Index stress notation is phonological, not prose quotes; must become ASCA feature syntax. Prose curly quotes in env are left alone. | `normalize_stress_marks` (via `normalize_symbols`) |




### Phase B½ — First-`;` rule comment partition (before structural split)

After Phase A½ overlays (correction → manual mapping → section mapping) and quoted-prose detection; **before** symbol normalization and structural split inside **`IndexRule.init()`**. The tail is stored as index **rule comment** as-is (no symbol/feature/IPA/series transforms). Detectors (`sporadic`, trailing glosses, stress, medial) run on the remainder only — not on **rule comment**. Field-level env/exception `;` capture (`apply_semicolon_field_comments`) is retired in favour of this whole-line cut (ticket 77).


| Step                                                      | Status      | Order | Rationale                                                                                                                                                                    | Code                           |
| --------------------------------------------------------- | ----------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| Partition first `;` on working line                            | implemented | B½1   | Editorial tails (including arrows inside gloss) must not become spurious chain stages. Naive first-`;` anywhere; owner **Manual mapping** rows plant the intended delimiter. | `IndexRule.build` (`split_semicolon_comment`) |
| No `→` in remainder → empty `stages` + optional `comment` | implemented | B½2   | Prose-only or mapping-shaped lines with no rule spine stay in the index; compile validation may fail.                                                                        | `parse_rule_element`           |




### Phase C — Structural field split


| Step                                     | Status      | Order | Rationale                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Code                                                     |
| ---------------------------------------- | ----------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Leading em-dash list marker strip (`—` ) | implemented | C1    | Index list formatting, not phonology (correction pass 16).                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | `IndexRule.build` (internal `extract_rule_parts`) |
| Primary I/O split (first `→`)            | implemented | C2    | Core rule shape: `input → output [/ env] [! exception]`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `split_input_output`                                     |
| Output / env / exception split           | implemented | C3    | ASCA env uses `/`; exception via `!`, word `except`, or second `/`. A slash glued to output (`∅/ _#`) is the same delimiter without the preceding space (pass 82); symmetrically, env glued after a spaced slash (`∅ /{a,E}_`) splits when the character after `/` is env-start (pass 132). Lines that omit `/` entirely are Index errata — overlay in `index_corrections.yml`, not a parse partition. | `split_post_arrow`, `split_env_exception`                |
| Remaining `→` → `>` in field values      | implemented | C4    | Chained outputs and embedded arrows must use ASCA `>` (correction pass 17).                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `normalize_rule_arrows` (via `IndexRule.build`)   |


**Missing** `→`**:** still a index rule (spine shape is ticket 90); no `status: skipped` unless the **rule id** is listed in `parser_config.yml` `skip_rules`. Boolean `skip` / `skipped` are not index fields.

### Phase D — Class-first field transforms (post-split)


| Step                                                                  | Status      | Order | Rationale                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Code                       |
| --------------------------------------------------------------------- | ----------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| Uncertainty gloss → `sporadic: true` + `comment`                      | implemented | D1    | `sporadic`/`sometimes`/`occasionally` are editorial qualifiers, not ASCA syntax (pass 19); a trailing `?` / `?` on env or exception is the same uncertainty marker (pass 132). Stripped prose captured, not discarded. Runs on remainder only (not **rule comment** seeded at B½).           | `apply_sporadic_qualifier` |
| Trailing / embedded editorial gloss strip → `comment`                 | implemented | D2    | Prose in quotes, parens, semicolon tails breaks ASCA; capture-not-discard (passes 21, 24, 31, 82). Internal order: embedded quotes → trailing quotes → trailing parens (including unclosed `(prose…` and `= /ə/` pronunciation glosses; set/matrix parentheticals stay in stages) → semicolon prose. Field-level `;` capture retired (B½). Unclosed strip is stages-only so env/exception can still pair a gloss Index split across `!`. | `apply_trailing_glosses`   |
| Env stress phrase normalization (`when stressed` / `when unstressed`) | implemented | D3    | Index env prose → ASCA env with `_` focus prefix (pass 22).                                                                                                                                                                                                                                                                                                                                      | `apply_stress_conditions`  |
| Prose conditional env phrases                                         | implemented | D3½   | Index conditional prose → project env strings (pass 134); runs before prose position and `//` split (165).                                                                                                                                                                                                       | `apply_prose_conditional_env_conditions` |
| Prose position env phrases                                          | implemented | D3¾   | Bare position prose → Index env strings (`U#`, `U[±stress]`, …); no Tier C ASCA literals at parse (107, 163).                                                                                                                                                                                                  | `apply_prose_position_env_conditions` |
| Index ` // ` env shorthand + prose exception tails                   | implemented | D3⅞   | Split into structured `IndexContext` env/exception; compile emits ASCA `//` grammar (108, 164).                                                                                                                                                                                                           | `apply_double_slash_env_conditions` |
| Editorial `in` before mechanical `#U` / `U#`                        | implemented | D3⅞+  | Parse-only strip on env/exception `context` after 107/108, before feature/IPA (pass 98); helper in `ingest/utils/syllable_position.py` (150).                                                                                                                                                                  | `apply_syllable_position_editorial_strip` |
| Feature matrix synonym replacement (inside `[...]` only)              | implemented | D4    | Index→ASCA renames / bundles / **tone** via `config/parser/feature_mappings.yml` (`mapping_kind` includes `tone` → `[tone: N]`; pass 62). Unmapped names left literal for `unknown_feature` clustering. Runs on env/exception **`context`** (not `position`) **before** neighbour/medial extraction so prose like `near [+emphatic]` is normalized first (143). | `apply_feature_mappings`   |
| IPA character substitution                                          | implemented | D4½   | `config/parser/ipa_mappings.yml` on stages and env/exception **`context`**; same ordering constraint as D4 (before `apply_index_context_position_extraction`).                                                                                                                                                                                                                                                          | `apply_ipa_mappings`       |
| Env medial / neighbour position extraction                          | implemented | D6    | Post-split `IndexContext.position` for `medial`, `adjacent_to`, `near`, `in` (143); compile projects to ASCA (144). Runs **after** D4/D4½.                                                                                          | `apply_index_context_position_extraction` |
| Dialect prose in env/exception `context`                            | implemented | D7    | Structured `dialect` on `IndexContext`; `context` trimmed when fully parsed.                                                                                                                                                                                                                                                                                                                              | `IndexRule.apply_dialects_to_env_fields` |
| Collective subscript expansion (`series_expansions`)                  | implemented | D0    | Fan out `Xₓ` collectives from `config/parser/parser_config.yml` (grill 73). Runs first after `init()` (before D1–D3 gloss/stress passes). Correspondence-series indices (`h₁`, `s₁`, …) stay literal until compile.                                                                                                                                                                              | `apply_series_expansions`  |




### Phase E — Rule assembly (post-transform)


| Step                                                     | Status       | Order | Rationale                                                                                                                                                                                                                                 | Code                                 |
| -------------------------------------------------------- | ------------ | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Multi-step chains (`a > b > c`)                          | compile-time | —     | One index row per HTML line; adjacent **stages** expand at compile (`[expand_chained_index_rule](../src/conlanger/compile/tools/asca/chains.py)`). Chains **with** env/exception stay one row; env/exception attach to each emitted step. | `SoundChangeRule` / compile pipeline |
| Attach provenance (`raw`, `source`, optional `sporadic`) | implemented  | E1    | Every emitted rule carries HTML line ref and original Index text.                                                                                                                                                                         | `parse_rule_element`                 |




### Phase F — Section post-pass (after per-line extract)


| Step                                                    | Status      | Order | Rationale                                                                                                                                                                                                                                                                                 | Code                                        |
| ------------------------------------------------------- | ----------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Catch-all `/ else` → complementary `exception`          | implemented | F1    | Index default branch is not an env; when the previous rule has `env` and no `exception`, omit `env` and set `exception` to that env (pass 53). Deferred: prev with both env+exception, neither, or else-after-else. | `resolve_catch_all_else_rules` (in `parse`) |
| Nested `{…}` set flatten (env / exception / stages)     | implemented | F1½   | ASCA rejects same-type nested braces; union + parenthetical-in-set rewrite via `BracketScanner` (passes 69–70). `raw` unchanged. Runs immediately after F1.                                                                                              | `flatten_nested_sets_in_section_rules`      |


---



## `config/parser/parser_config.yml`


| Key                       | Purpose                                                                                                                                                                                                                                                     |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ipa_mappings.confidence` | Which `config/parser/ipa_mappings.yml` confidence levels apply at parse (`None` = all rows)                                                                                                                                                                 |
| `series_expansions`       | Collective subscript fan-out (`Hₓ` → `h₁, h₂, h₃`, …)                                                                                                                                                                                                       |
| `section_mappings`        | Section-scoped token rewrites (`"10.1": {"*D": "D", …}`); applies to matching section and all descendants; child row overrides ancestor for the same `from` key (ticket 97) |
| `skip_sections`           | List of `{id, reason}` — `id` matches section `index`; `reason` is operator documentation only. Listed sections gain `status: skipped` in parsed YAML.                                                                                                      |
| `skip_rules`              | List of `{id, reason}` — `id` matches HTML **rule id**; `reason` becomes optional index `comment`. Listed rules gain `status: skipped`.                                                                                                                     |


---



## Planned / deferred parse-time work


| Step                                                              | Status                                | Order | Rationale                                                                                                                                                                                                  |
| ----------------------------------------------------------------- | ------------------------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Positional slots (`C₁C₂ → C₂`)                                    | planned (compile-time)                | TBD   | ASCA reference syntax (`C=1`, bare `2`) is applier-specific; index stays Index-shaped. See [positional-slots research](../../.backlog/spikes/0033-positional-slots-and-identity-subscripts.md).       |
| Identity subscripts (`V₀V₀ → V₀`)                                 | planned (compile-time)                | TBD   | Same policy as positional slots.                                                                                                                                                                           |
| Class letter expansion (`S`, `A`, `R`, …)                         | implemented at **compile**, not parse | —     | Avoid baking ASCA syntax into applier-neutral YAML (pass 14).                                                                      |
| Feature matrix Phase 2+ (remaining place/manner, pitch accent, …) | planned                               | TBD   | Tone pass shipped (62); other deferred features stay inventory-driven.                                                                |
| Whitespace tokenisation inside brackets                           | deferred                              | TBD   | Most polarity-space cases handled by feature regex; multi-word tone names are CSV keys with spaces.                                                                                                        |
| Meta-notation (`X0`, `Xn`, retroflex marks, repetition groups)    | deferred (cluster-driven)             | TBD   | No evidence-based ASCA expansion without inventory clustering.                                                                                                                                             |
| Section-local abbreviations (`TŠ`, uppercase `S₁`)                | partial (cluster-driven)              | TBD   | Owner-curated `section_mappings` rows at parse (ticket 97); bulk authoring inventory-driven.                               |
| Global abbreviation table authorship                              | removed                               | —     | Document-level `abbreviations` key dropped from parse output; section mappings are config-driven, not stored tables.                                                                                       |
| Edge-split / parse-time auto-skip for unrepresentable lines       | removed                               | —     | `status: skipped` is config-only (ticket 89); missing-arrow / gloss-only lines stay in parse → compile → validate.                             |
| Prose-environment mapping (comment paragraphs → structured `env`) | planned (spike)                       | TBD   | `comment` field captures qualifiers; structured env from prose not specified.                                                                                                                              |
| Dedicated smart-quote normalizer                                  | partial                               | TBD   | Embedded/trailing `"`/`"` stripped as glosses at parse (pass 24); typographic apostrophe `'` → ejective at **compile**.                |
| Correspondence-series index mappings                              | compile-time                          | TBD   | Section-scoped rows authored in `config/compile/asca/compiler_config.yml` (ticket 75); PIE laryngeals seeded in `global`. |


---



## Pipeline placement


| Stage                                   | Doc                                                  |
| --------------------------------------- | ---------------------------------------------------- |
| **Index Diachronica parse** (this page) | `uv run create_index`                                |
| Applier compile                         | [compile-rules.md](./compile-rules.md) (`uv run compile_rules`) |
| Validate                                | [validate.md](./validate.md) (`uv run validate_rules`) |


See also [SYSTEM.md](./SYSTEM.md#pipeline-stages-new).