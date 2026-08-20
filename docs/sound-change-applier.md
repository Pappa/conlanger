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

Parse-time transforms are documented in [index-diachronica-parser.md](./index-diachronica-parser.md). Corpus validation workflow is in [applier-neutral-corpus-validation.md](./applier-neutral-corpus-validation.md).

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

`SoundChangeRule` requires `input`, `output`; optional `env`, `exception`. `skip: True` → commented prefix (`#\t`); excluded from validation. Compiled text is stored in `value` at construction via `_format()`.

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

Compile validation is stage 4 of the sound-change pipeline. It runs **after** applier compile, not at HTML→YAML ingest ([ADR-0003](./adr/0003-validate-after-applier-compile.md)).

### `validate_asca`

Module: [`appliers/asca.py`](../src/conlanger/appliers/asca.py)

```python
validate_asca(
    rule: DiachronicSeries,
    *,
    probe_words: Path | None = None,
    timeout: float = 15.0,
) -> bool  # raises ASCAValidationError

validate_asca_syntax(rule: str, *, timeout: float = 15.0) -> bool
validate_asca_part(part: ASCARulePart, fragment: str, *, timeout: float = 15.0) -> bool
resolve_asca_bin() -> str | None  # ASCA_BIN env, then PATH
```

**Binary resolution:** `ASCA_BIN` if set, else `shutil.which("asca")`. Same helper for `validate_asca`, `run_asca`, and the field helpers. Install the fork with `validate` per [DEV.md](./DEV.md#asca-sound-change-rule-validation).

**Flow:**

1. `_active_rule_changes(rule)` — collect `SoundChangeRule` parts whose rendered line does **not** start with `#` (skipped rules render as `#\t…`).
2. Error if no active rules.
3. Resolve asca binary (`ASCA_BIN` or `PATH`; expects **0.10.x**, fork **0.10.3+** for `validate`).
4. Write `str(rule)` (+ trailing newline) to temp `check.rsca`.
5. Resolve probe wordlist (see below).
6. When the binary supports `validate`: `subprocess.run([asca, "validate", "-r", rsca_path], …)` — fast syntax/structure fail (Tiers 1–3).
7. `subprocess.run([asca, "run", words_path, "--rules", rsca_path], …)` — still required for inventory `ok` (Tier 4).
8. Non-zero exit → `ASCAValidationError` with cleaned stderr.
9. Also fail if stderr contains `Syntax Error` or `Runtime Error` even on exit 0.

**Field helpers** (fork `validate` only; for later field isolation — inventory does **not** use these for `ok`):

- `validate_asca_syntax("a > b / _")` → `asca validate -s …`
- `validate_asca_part("env", "#_")` → `asca validate -s … -f context` (`env` maps to ASCA `context`)

**Inventory integration** (`corpus_inventory.py`): each corpus rule → `_mini_section` → `DiachronicSeries(mini, group_mappings=…)` → `validate_asca(..., probe_words=fixture)`.

### Probe wordlist

| Source | Path / content |
| --- | --- |
| Default (validator internal) | `a`, `ba`, `kata`, `sami`, `ntu` (5 words) |
| Inventory / tests fixture | `tests/fixtures/asca_probe_words.wsca` (same 5 words) |
| Override | `probe_words=` argument or `ASCA_PROBE_WORDS` env var |

**Purpose:** `asca run` exercises parse **and** apply (Tier 1–4 in validity research). Not parse-only.

**Limits** ([ticket 10](../.scratch/cleaned-rule-corpus/issues/10-rule-derived-probe-synthesis.md) wontfix):

- ~98% of inventory failures are Tier 1–2 syntax — baseline probes suffice for clustering.
- Tier 4 runtime errors (lonely sets, insertion+env, deletion-only-segment) may be **under-detected** when probes don't match rule shape — acceptable for correction-loop clustering.

### ASCA validation tiers

See [asca-rule-validity.md](../.scratch/cleaned-rule-corpus/research/asca-rule-validity.md) §5 for ASCA constraint detail:

| Tier | Stage | Caught by `validate_asca`? |
| --- | --- | --- |
| 1 | Lexer | Yes (`validate` when available, else `run`) |
| 2 | Parser | Yes |
| 3 | `split_into_subrules` (first apply) | Yes (`validate` when available, else `run`) |
| 4 | Runtime apply | Yes via `run` — probe-dependent |

### Skipped rules

Corpus `skip: True` → `#\t{rule}` in ASCA output. `_active_rule_changes` excludes them; inventory marks `ok=True`, description `"held-out (commented rule)"`.

---

## Pipeline placement

| Stage | Doc |
| --- | --- |
| Index Diachronica parse | [index-diachronica-parser.md](./index-diachronica-parser.md) |
| Applier-neutral corpus validation | [applier-neutral-corpus-validation.md](./applier-neutral-corpus-validation.md) |
| **Applier compile** (this page) | — |
| **Compile validation** | [Compile validation](#compile-validation) (this page) |

See also [SYSTEM.md](./SYSTEM.md#pipeline-stages-new).
