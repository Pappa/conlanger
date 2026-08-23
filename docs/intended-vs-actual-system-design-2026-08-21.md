# Intended vs. Actual System Design - 2026-08-21

"Inntended" here refer to the design as recorded in the project docs, not _my_ intended design of the 
Index Diachronica parse and asca compile pipeline.

**Intended** here is CONTEXT + the ADRs, with later ADRs winning when they conflict with the stage docs. That matters: `docs/index-diachronica-parser.md` still describes `input`/`output` and parse-time chain split; [ADR-0011](docs/adr/0011-index-rule-stages.md) and [ADR-0005](docs/adr/0005-one-index-rule-per-html-line.md) superseded that. ⚠️ marks where **code** does not match that intended design (not where a stage doc is merely stale).

Placement in the four-stage pipeline ([SYSTEM.md](docs/SYSTEM.md)):

- Index Diachronica parse
- Applier-neutral index validation (inventory lives here; it *calls* compile + compile validation per rule)
- Applier compile (ASCA)
- Compile validation

---

## Intended pipeline

- **Index Diachronica parse** (HTML → applier-neutral **rule index** YAML; [ADR-0002](docs/adr/0002-applier-neutral-yaml-rule-index.md), [ADR-0006](docs/adr/0006-html-source-of-truth-yaml-successor.md))
  - **Ingest**
    - Read `data/diachronica/index_diachronica_original.html` as **source of truth** for each rule line unless an **Index Diachronica correction** replaces it ([ADR-0012](docs/adr/0012-index-diachronica-corrections-overlay.md))
    - Read overlay `data/diachronica/index_diachronica_corrections.yml` (keyed by **rule id**)
    - Read parse tables: `data/common/manual_mappings.csv`, `data/parser_config.yml` (`series_expansions`, IPA confidence, `skip_sections`), `data/asca/feature_mappings.csv`, `data/common/ipa_mappings.csv`
    - Parse HTML non-strictly (lxml)
  - **Processing**
    - Discover each **sound-change section** (`<section id>` + first `<h2>`)
    - Split heading into `index` + title (dotted ancestry for later series lookup)
    - First non-`schg` `<p>` → citation; later non-`schg` `<p>` → section comments
    - Each `<p class="schg">` → one **index rule** (1 HTML line → 1 YAML row; [ADR-0005](docs/adr/0005-one-index-rule-per-html-line.md))
    - Global `abbreviations` slot exists but is empty until authored
    - After all rules in a section: resolve `/ else`; apply section skip from `parser_config.yml`
    - Write `data/diachronica/index_diachronica_parsed.yml` (`uv run create_index`)
  - **Transformation** (per rule; index fields stay Index-shaped / applier-neutral — not ASCA syntax)
    - `<sub>` → Unicode subscripts, then collapse whitespace
    - If a correction exists for this **rule id**, that Unicode string **is** `raw`; `source` still points at the HTML line ([ADR-0012](docs/adr/0012-index-diachronica-corrections-overlay.md))
    - **Manual mapping** rewrites the working copy only (`raw` unchanged)
    - Peel first `;` as **rule comment** (detectors must not see the tail)
    - Normalize **symbols** on the working line (`%` → `$`, Index stress `"` → `segment:[+stress]`; protect stem `$`)
    - Strip leading `— `; isolate one `env` and one `exception`; split the change spine on **every** `→` into **stages** ([ADR-0011](docs/adr/0011-index-rule-states.md))
    - Remaining arrows inside a field → `>` (ASCA chain glyph in an opaque string, not a second index row)
    - Uncertainty glosses → `sporadic: true` + `comment`
    - Trailing/embedded editorial glosses → `comment`
    - Env stress prose (`when stressed` / `when unstressed`) → ASCA-shaped env with `_`
    - Feature-matrix names inside `[...]` via `feature_mappings.csv` (unmapped left literal)
    - ⚠️ **Collective subscripts** (`Xₓ`) fan out from `parser_config.yml` `series_expansions` into member **correspondence-series indices**; docs put this *after* feature mappings — code runs it *immediately after the field split*
    - IPA character maps from `ipa_mappings.csv` (confidence-gated) on stages / env / exception
    - **Correspondence-series indices** (`h₁`, `s₁`) stay literal until compile ([ADR-0004](docs/adr/0004-series-indices-per-section-maps.md) amendment)
    - **Positional slots** / **identity subscripts** stay Index-shaped at parse
    - **Class letters** are *not* expanded at parse
    - One index rule per line: **no** parse-time explosion of chains into extra YAML rows
    - Unrepresentable / prose-only lines → `stages: []` + `status: skipped` (edge-split policy still deferred as a bulk skip programme)
    - ⚠️ Catch-all `/ else` → previous sibling’s env becomes `exception` (**section post-pass**)
    - ⚠️ **Medial** / **medially** → `env: _` + `exception: :{#_, _#}:` (docs place this *after* else, as a section post-pass; code does it *per rule*, before feature/IPA maps)
    - `skip_sections` → `skipped: true` on the section object (compile/inventory bypass the whole section)
- **Applier-neutral index validation** (inventory)
  - Sits here in the pipeline: after parse, it compiles and compile-validates each index rule to produce the inventory CSVs. Not detailed further.
- **Applier compile** (index section → ASCA `.rsca` string; index YAML is never mutated)
  - **Ingest**
    - One **sound-change section** dict (`index`, `section`, optional `citation` / `comment` / `skipped`, `rules`)
    - Compile tables: `data/asca/group_mappings.csv` (**abbreviation table**), `data/compiler_config.yml` (**series mappings**, hierarchical section + `global`)
  - **Processing** (`DiachronicSeries` then `SoundChangeRule`)
    - One section → one `DiachronicSeries` (the runtime compile unit)
    - Assemble parts in order: title (`@ {index} - {section}`), optional citation, optional comment
    - If the section is `skipped`, emit no rules
    - For each **index rule**, compile expands `stages` into adjacent pairs at **compile time** only ([ADR-0011](docs/adr/0011-index-rule-stages.md)): `[A, B, C]` → two steps `A > B` and `B > C`, each stamped with the same rule-level `env` / `exception`
    - Each step is one `SoundChangeRule` (requires `input` / `output` *after* that expansion — those are compile-time fields, not index YAML)
    - ⚠️ Held-out rules: intended story is `status: skipped` (empty `stages`) *and/or* `skip: true` rendered as an ASCA comment (`#\t…`) so section structure stays visible; code only implements the empty-`stages` omit path for parse hold-outs, plus a separate unused-looking `skip: true` comment path
    - **Optional outputs** (`d → {∅,ð}`): each set member becomes a peer `SoundChangeRule` on `.alternatives`; the parent samples one uniformly via instance `Random` as the emitted line; inventory validates the alternatives, not the sample
  - **Transformation** (on the joined ASCA string; order is load-bearing)
    - Drop mixed parallel-null columns on input/output separately (`c ɲ > ∅ n` → `c ɲ > n`; pure deletion unchanged)
    - Expand parallel output-null set branches into `.alternatives` when it is not the unpaired optional-output case
    - Join: `input > output` plus optional ` / env` and ` // exception`
    - Optional ellipsis: `(C…)` → `(C,0)`; `(…C)` → `(..)C` (**before** class-letter expansion)
    - **Series mapping**: correspondence-series indices → segments from `compiler_config.yml` (**before** positional/identity rewrite, so `h₁` is not treated as a slot)
    - ⚠️ **Positional slots** and **identity subscripts** → ASCA refs (`C=1`, bare `2`, `V=0`) — stage doc still says *planned*; this is intended compile-time work that should not live in the YAML
    - ⚠️ **Section-local abbreviations** (`TŠ`, `TS`) — planned, before group mappings so `TS` is not split into `T`+`S`
    - **Class letters** via `group_mappings.csv`; unmapped letters stay literal
    - Length `ː` / `(ː)` → `:[+long]`
    - Merge adjacent `[tone: N]` into the prior matrix
    - Typographic apostrophe → ejective `ʼ`
    - Ejective `ʼ` → `:[+cg]` / `+cg` in matrices
    - Breve vowels → bare segment or `:[-long]`
    - Residual meta-notation last (tilde, parentheticals, input optionals, concatenated `}∅` deletion columns)
    - ⚠️ Docs name a public `ASCA_COMPILE_STEP_NAMES` list as the order contract; that symbol is not in the code
- **Compile validation**
  - After compile only ([ADR-0003](docs/adr/0003-validate-after-applier-compile.md)): `validate_asca(DiachronicSeries)` writes `str(series)` and runs `asca validate` / `asca run` against a **probe wordlist**. Inventory is the operator loop around this gate.

---

## Actual pipeline

- **Index Diachronica parse** (`IndexDiachronicaParser` in `src/conlanger/tools/ingest/parser.py`; orchestrated by `create_index`)
  - **Ingest**
    - `load_default_ingest_tables()`: manual mappings, `parser_config.yml` (also `skip_rules`), feature mappings, IPA mappings, corrections YAML
    - HTML path (default `data/diachronica/index_diachronica_original.html`)
    - `load_html_document`: normalize `<sub>` in the file text, then lxml parse
  - **Processing**
    - Walk `//section[@id]`; require `./h2`; `parse_section_heading`
    - `schg` paragraphs: `p.get("id")` as `rule_id` → `parse_rule_element` (always returns a **one-element** list)
    - Non-`schg` prose → citation then `comments`
    - Then `resolve_catch_all_else_rules(rules)` for that section
    - Then `skipped: true` if `index` is in `skip_sections`
    - `abbreviations()` → `{}`
    - Write YAML via `write_cleaned_index`; then inventory unless `--skip-validation`
  - **Transformation** (`parse_rule_element`, actual order)
    - `extract_text_with_subs` → initial `raw`
    - Corrections overlay replaces `raw` when `rule_id` hits
    - `apply_manual_mappings` on a working copy (`raw` stays pre-manual)
    - Quoted-prose paragraph → one skipped rule (`stages: []`, `status: skipped`)
    - `split_line_semicolon_comment`
    - `normalize_symbols` on the whole remainder
    - `extract_rule_parts`: em-dash strip → first `→` → env/exception → `build_stages_from_spine` (every remaining `→` in the spine) → `normalize_rule_arrows` (`→` → `>`) on each stage/env/exception — **no `input`/`output` keys**
    - Missing `→` → `stages: []`, `status: skipped` (not the old `"skipped": "missing separator '→'"` string)
    - `apply_series_expansions` (collectives)
    - `apply_sporadic_qualifier` (flag popped, reattached at emit)
    - `apply_trailing_glosses`
    - Gloss-only (`< 2` stages + comment) → skipped
    - `apply_stress_conditions` (env/exception only)
    - `apply_medial_env_conditions` **here** (per rule, before feature/IPA, not after else)
    - `apply_feature_mappings`
    - `apply_ipa_mappings`
    - `finalize_stages_shape` (`< 2` non-empty stages → skipped)
    - `skip_rules` in parser config → forced skipped shell (comment from config)
    - Emit one dict: `stages`, optional `env`/`exception`/`comment`/`sporadic`/`status`, plus `raw`, `source`, `rule_id`
- **Inventory**
  - After YAML write: each index rule → mini-section → `DiachronicSeries` → `validate_asca` → CSV. Same compile path as below.
- **Applier compile** (`src/conlanger/tools/rules.py` + `src/conlanger/tools/compile/asca/pipeline.py`)
  - **Ingest**
    - `DiachronicSeries(section, format="asca", group_mappings=…, compiler_config=…)`
    - `group_mappings` typically `asca_group_mappings_dict()`; `compiler_config` defaults to `load_compiler_config()`
    - Only `format="asca"` is accepted
  - **Processing — `DiachronicSeries`**
    - Builds `self._parts`: `RuleTitle`, optional `RuleCitation`, optional `RuleComment`
    - If `section["skipped"]`: **return** (no `SoundChangeRule`s)
    - For each index rule:
      - `normalize_index_rule_tilde_fields(rule)` (mutates a copy of `stages`; a `" > "` inside a stage can **split into extra stages**)
      - `expand_chained_index_rule` reads **only** `stages`; emits `N−1` dicts `{input, output, …meta}` for adjacent pairs; copies `env` / `exception` / `comment` / `sporadic` / `skip` onto every step; `< 2` non-empty stages → `[]` (parse `status: skipped` rules simply **vanish** from the `.rsca`)
      - Each step → `SoundChangeRule(...)`
    - `str(DiachronicSeries)` joins parts with newlines + trailing newline → `.rsca` body
  - **Processing — `SoundChangeRule`**
    - Constructor **requires** `input` and `output` (raises if missing). It never reads `stages`.
    - Optional `env` / `exception`; if `env` is missing, `_peel_trailing_env_from_output` may pull a trailing env off `output`
    - Stores `group_mappings`, `section_index`, `compiler_config`, and an **instance** `Random` (`seed` or `rng`; never `random.seed`)
    - `skip: True` → prefix `#\t` (commented ASCA line); otherwise `\t`
    - `_build_alternatives`: optional-output peers first (whole-field `{…}` output, input not a whole-field set); else parallel-`∅` set branches
    - Each alternative is a full child `SoundChangeRule` (recurses; leaves compile via `_format`)
    - If alternatives exist: parent **freezes one** with `rng.randrange` and stores that child’s compiled `value` as the emitted line; `.alternatives` remains the full peer list for inventory
    - Else: `value = self._format()` at construction (compile once, store)
  - **Transformation — `_format` then `compile_asca_rule_string`**
    - `drop_mixed_parallel_null_columns` on `input` and `output` separately
    - Join ` > ` / ` / ` / ` // `
    - Then, in this exact order:
      - `normalize_asca_optional_grouping_ellipsis`
      - `apply_compiler_series_mappings` (`compiler_config.resolved_series_mappings(section_index)`)
      - `expand_index_subscript_references` (**implemented**: positional slots + identity subscripts → ASCA `X=n` / bare `n`)
      - `apply_section_local_abbreviations` (**no-op**: `return text`)
      - `normalize_asca_superscript_modifiers` (uses `group_mappings`)
      - `apply_asca_group_mappings_to_string`
      - `normalize_asca_length_marks`
      - `normalize_asca_tone_matrices`
      - `normalize_typographic_apostrophes`
      - `normalize_asca_ejective_marks`
      - `normalize_asca_breve_marks`
      - `expand_meta_notation` → tilde, parentheticals, input optionals, `drop_concatenated_deletion_column`
    - `group_mappings` / series mappings are **not** applied by `DiachronicSeries` itself; they are injected into each `SoundChangeRule` and applied only inside this pipeline
    - There is no `ASCA_COMPILE_STEP_NAMES` and no `DiachronicSeries` class (the spec still names both)

How the two classes share the work, in one picture:

```text
index section
    → DiachronicSeries
         title / citation / comment
         for each index rule:
              tilde-normalize stages
              expand stages → N−1 {input, output} steps
              each step → SoundChangeRule
                   maybe alternatives (optional outputs | parallel ∅)
                   join fields
                   compile_asca_rule_string → self.value
    → str(DiachronicSeries)  =  .rsca text
```