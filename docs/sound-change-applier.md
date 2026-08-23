# Sound-change applier compile

Applier compile turns one **sound-change section** (index dict) into a concrete backend string. ASCA is the first backend; Brassica is deferred ([ADR-0001](./adr/0001-sound-change-applier-backends.md)).

Corpus YAML fields and `raw` are **never modified** — transforms apply only to the emitted applier string.

**Primary code:** [`compile/asca/pipeline.py`](../src/conlanger/tools/compile/asca/pipeline.py) (`compile_asca_rule_fields`, `compile_asca_field_pre_subscript`, `compile_asca_field_post_subscript`), [`rules.py`](../src/conlanger/tools/rules.py) (pydantic `DiachronicSeries`, `SoundChangeRule`), [`appliers/asca.py`](../src/conlanger/appliers/asca.py) (`validate_asca`). See [ADR-0014](./adr/0014-per-field-asca-compile.md).

**Related:** [ADR-0002](./adr/0002-applier-neutral-yaml-rule-index.md) (applier-neutral index), [ADR-0003](./adr/0003-validate-after-applier-compile.md) (validate after compile).

---

## Overview

```text
index section dict
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

`SoundChangeRule` requires `input`, `output`; optional `env`, `exception`. Corpus rules with `status: skipped` render as commented ASCA lines (`#\t` + `raw`); excluded from validation. Compiled text is stored in `value` at construction via per-field compile ([ADR-0014](./adr/0014-per-field-asca-compile.md)).

---

## Per-rule ASCA compile pipeline

Per-field transforms run on `input`, `output`, `env`, and `exception` separately at `SoundChangeRule` construction; cross-field subscript expansion shares a `declared` set (output last); fields join only when building `value` ([`compile_asca_rule_fields`](../src/conlanger/tools/compile/asca/pipeline.py), [`SoundChangeRule`](../src/conlanger/tools/rules.py)).

| Step | Status | Order | Rationale | What breaks if reordered |
| --- | --- | ---: | --- | --- |
| Drop mixed parallel null columns | implemented | 0 | Index parallel-column `∅`/`*` beside other segments → omit null tokens before join (`c ɲ > ∅ n` → `c ɲ > n`). Pure `x > ∅` unchanged. | Must run on separate `input`/`output` fields **before** compile — ASCA deletion/insertion rules require bare null sides. |
| Expand parallel output null branches | implemented | 0b | `∅` inside output correspondence sets (`{r,h} > {∅,h}`, `{m,ɲ} n > {ɲ,∅} {ŋ,∅}`) → `SoundChangeRule.alternatives` with per-branch compiled rules; inventory `alt_idx`. Uneven multi-column branch counts out of scope. | Runs via `_build_parallel_null_set_alternatives` after optional-output detection (ticket 66). |
| Per-field pre-subscript transforms | implemented | 2–5 | Each field: ellipsis → series mappings → section-local abbreviations → superscript modifiers → group mappings. | Cross-field subscripts must see expanded class letters per field before shared `declared` binding. |
| Cross-field subscript expansion | implemented | 3 | `expand_subscript_references_across_fields`: input declares, env/exception next, output last. | **Before post-subscript length marks** — ref digits like `0ː` need length normalization after expansion. |
| Per-field post-subscript transforms | implemented | 6–10 | Each field: length → tone → apostrophe → ejective → breve → meta notation. | Length/tone/ejective order unchanged from spike 38. |
| Join compiled fields | implemented | render | `input > output / env // exception` into `SoundChangeRule.value`. | Join is render-only; no join-then-rewrite pipeline. |

**Research:** [positional-slots-and-identity-subscripts.md](../.scratch/cleaned-rule-index/research/positional-slots-and-identity-subscripts.md), [subscript-notation-index-asca-brassica.md](../.scratch/cleaned-rule-index/research/subscript-notation-index-asca-brassica.md).

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
