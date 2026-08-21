# Sound-change applier compile

Applier compile turns one **sound-change section** (corpus dict) into a concrete backend string. ASCA is the first backend; Brassica is deferred ([ADR-0001](./adr/0001-sound-change-applier-backends.md)).

Corpus YAML fields and `raw` are **never modified** — transforms apply only to the emitted applier string.

**Primary code:** [`compile/asca/pipeline.py`](../src/conlanger/tools/compile/asca/pipeline.py) (`compile_asca_rule_string`, `ASCA_COMPILE_STEP_NAMES`), [`rules.py`](../src/conlanger/tools/rules.py) (`DiachronicSeries`, `SoundChangeRule`), [`appliers/asca.py`](../src/conlanger/appliers/asca.py) (`validate_asca`).

**Related:** [ADR-0002](./adr/0002-applier-neutral-yaml-rule-corpus.md) (applier-neutral corpus), [ADR-0003](./adr/0003-validate-after-applier-compile.md) (validate after compile).

---

## Overview

```text
corpus section dict
        │
        ▼  DiachronicSeries(section, format="asca")
        │     holds section; assembles ASCA .rsca parts
        ▼  str(DiachronicSeries)  →  temporary .rsca
        ▼  validate_asca(...)  →  asca run <probe.wsca> --rules <file>
```

Parse-time transforms are documented in [index-diachronica-parser.md](./index-diachronica-parser.md). Inventory, compile validation, and the correction loop are in [validate.md](./validate.md).

---

## Section assembly

`DiachronicSeries` compiles one sound-change section to ASCA-ready `.rsca` text.

| Order | Part class | Condition | ASCA render prefix |
| ---: | --- | --- | --- |
| 1 | `RuleTitle` | always | `@ {index} - {section}` |
| 2 | `RuleCitation` | `section.get("citation")` | `# citation: …` |
| 3 | `RuleComment` | `section.get("comment")` | `\t# …` |
| 4+ | `SoundChangeRule` | each item in `section["rules"]` | `\t{compiled rule}` |

`str(DiachronicSeries)` joins parts with newlines → `.rsca` body shape.

`SoundChangeRule` requires `input`, `output`; optional `env`, `exception`. Corpus rules with `status: skipped` render as commented ASCA lines (`#\t` + `raw`); excluded from validation. Compiled text is stored in `value` at construction via `_format()`.

---

## Per-rule ASCA compile pipeline

Exact order in `compile_asca_rule_string` ([`compile/asca/pipeline.py`](../src/conlanger/tools/compile/asca/pipeline.py)), invoked from `SoundChangeRule._format`:

| Step | Status | Order | Rationale | What breaks if reordered |
| --- | --- | ---: | --- | --- |
| Drop mixed parallel null columns | implemented | 0 | Index parallel-column `∅`/`*` beside other segments → omit null tokens before join (`c ɲ > ∅ n` → `c ɲ > n`). Pure `x > ∅` unchanged. | Must run on separate `input`/`output` fields **before** join — ASCA deletion/insertion rules require bare null sides. |
| Expand parallel output null branches | implemented | 0b | `∅` inside output correspondence sets (`{r,h} > {∅,h}`, `{m,ɲ} n > {ɲ,∅} {ŋ,∅}`) → `SoundChangeRule.alternatives` with per-branch compiled rules; inventory `alt_idx`. Uneven multi-column branch counts out of scope. | Runs via `_build_parallel_null_set_alternatives` after optional-output detection (ticket 66). |
| Join corpus fields | implemented | 1 | Concatenate `input`, `output`, optional `env` / `exception` with ASCA separators (` > `, ` / `, ` // `). | Must be first string join — later steps operate on the full rule string. |
| `normalize_asca_optional_grouping_ellipsis` | implemented | 2 | Index optional ellipsis → ASCA forms: trailing `(C…)` → `(C,0)`; leading `(…C)` → `(..)C`. Skips `[…]` matrices. | **Before group_mappings:** patterns target bare class letters (`C`, `V`, `S`) in parentheses. After expansion, `(C,0)` targets are harder to match reliably. |
| `apply_compiler_series_mappings` | implemented | 2b | Correspondence-series indices → segments from `data/compiler_config.yml` (`global` + longest-prefix `sections`). Replaces `PIE_LARYNGEAL_ALIASES` (`h₁→h`, `h₂→x`, `h₃→ɣʷ`). Unmapped indices stay literal. | **Before positional/identity subscripts:** mapped `h₁` must not be mistaken for a slot. Substring replace (so `eh₂` → `ex`). |
| `apply_asca_group_mappings` | implemented | 5 | Expand Index class letters from `group_mappings.csv` to ASCA groupings/matrices; handle `Kʷ`, `K(ʷ)`, optional labial pairs; skip `[…]`. | **Before length/ejective:** length on class letters (`Vː`) and set patterns assume letter tokens. |
| `normalize_asca_length_marks` | implemented | 6 | Index `ː` / `(ː)` → `:[+long]` on segments, groupings, sets, optional-length-with-comma; also inter-matrix `]ː[` → `, +long][` (e.g. `V:[+stress]ː[tone: 51]`). | **Before ejective:** `ts:[+long]ʼ` must become `ts:[+long,+cg]`, not fail on post-matrix `ʼ`. **After group_mappings:** set suffix / grouping length patterns operate on expanded tokens where needed. **Before tone merge:** inter-matrix length must land as `[+long]` so adjacent `[tone: N]` can merge. |
| `normalize_asca_tone_matrices` | implemented | 6b | After length, merge adjacent `[tone: N]` into the prior matrix (`V:[+long][tone: 51]` → `V:[+long, tone: 51]`) and ensure `seg[tone:` → `seg:[tone:`. Index `[+… tone]` → `[tone: N]` is parse-time (`feature_mappings.csv` `mapping_kind=tone`). | **After length:** length creates the adjacent-matrix shape ASCA rejects. **Before ejective:** tone merge must see clean `[+long]` matrices. |
| `normalize_typographic_apostrophes` | implemented | 7 | U+2019 (typographic apostrophe) → U+02BC (modifier letter apostrophe / ejective mark) on segments and class letters. | **Before ejective:** ejective normalizer only sees `ʼ`. If after ejective, curly apostrophes remain unconverted. |
| `normalize_asca_ejective_marks` | implemented | 8 | `segment:[feat]ʼ` → `+cg` in matrix; `{…}ʼ` → per-member `:[+cg]`; bare `segmentʼ` → `segment:[+cg]`. | **After length + apostrophe:** depends on normalized `[+long]` matrices and correct `ʼ` character. |
| `normalize_asca_breve_marks` | implemented | 8b | Index breve vowels (`j̆`, `ɨ̆`, `ə̆`, `ă`, `æ̆`, `ŏ`, `ŭ`) → bare segment (Tai glides) or `:[-long]` (Scots/Tanacross extra-short). Decomposes NFC precomposed breve letters first. | **After ejective:** breve segments are unrelated to `ʼ`. **After parse IPA map:** Tai `ı̆` is already `j̆` before compile. |
| `expand_meta_notation` | implemented | 10 | Tilde, parentheticals (including spaced parallel `(əw)` unwrap), input optionals, then drop `}∅` concatenated deletion columns ([pass 82](../.scratch/cleaned-rule-corpus/issues/82-correction-pass-output-env-slash-boundary.md)). | **Last string step:** residual output/env boundary after other meta handlers. |
| Positional slots → ASCA refs | planned | 3 | `C₁C₂ → C₂` → `C=1 C=2 > 2` (declare `X=n`, invoke bare `n`). | **Before group_mappings** ([spike 38](../.scratch/cleaned-rule-corpus/research/asca-compile-transform-order.md)). |
| Identity subscripts → ASCA refs | planned | 3 | `V₀V₀ → V₀` → `V=0 V=0 > 0`; env `h → ʔ / V₀V₀` → `h > ʔ / _ V=0 V=0`. | Same step as positional; compounds (`mV₀`, `CʔV₀`) need separate tokenization ticket. |
| Section-local abbreviations | planned | 4 | Expand Athabaskan / section-specific tokens (e.g. `TŠ`, `TS`) via hand-authored abbreviation rows. | **Before group_mappings** — `TS` must not be split into `T`+`S` ([spike 38](../.scratch/cleaned-rule-corpus/research/asca-compile-transform-order.md)). |
| Residual meta-notation | spike needed | 10 | Retroflex `X̣`, `(…X)` repetition, tone superscripts `Xⁿ`, etc. still cluster-driven. | Same `expand_meta_notation` slot; further handlers as new tickets. |

**Research:** [positional-slots-and-identity-subscripts.md](../.scratch/cleaned-rule-corpus/research/positional-slots-and-identity-subscripts.md), [subscript-notation-index-asca-brassica.md](../.scratch/cleaned-rule-corpus/research/subscript-notation-index-asca-brassica.md).

---

## Brassica

Future backend; compile transforms and validation will mirror the [ADR-0003](./adr/0003-validate-after-applier-compile.md) pattern.

---

## Compile validation

Compile validation is part of the **validate** stage ([validate.md — Compile validation](./validate.md#compile-validation)). It runs **after** applier compile, not at HTML→YAML ingest ([ADR-0003](./adr/0003-validate-after-applier-compile.md)).

Corpus `status: skipped` → `#\t{raw}` in ASCA output; `_active_rule_changes` excludes them from validation. See [validate.md](./validate.md) for `validate_asca` API, probe wordlists, validation tiers, and inventory integration.

---

## Pipeline placement

| Stage | Doc |
| --- | --- |
| Index Diachronica parse | [index-diachronica-parser.md](./index-diachronica-parser.md) |
| **Applier compile** (this page) | — |
| Validate | [validate.md](./validate.md) |

See also [SYSTEM.md](./SYSTEM.md#pipeline-stages-new).
