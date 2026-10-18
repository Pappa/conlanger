Type: spike
Status: resolved
Blocked by: None

# Spike: ASCA compile projection for `IndexContext.position.in`

Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-10-18). Blocks [174](174-task-position-in-asca-compile-projection.md). Builds on resolved [156](156-task-indexcontext-position-in-relation.md) (materialize `in {v}`), [98](98-correction-pass-syllable-position-u-hash.md) / [research/index-syllable-position-u-hash.md](../research/index-syllable-position-u-hash.md) (`#U` / `U#`), and [162](162-grill-syllable-structure-env-resolution.md) / [163](163-task-prose-position-env-string-fixes.md) (syllable-stress env).

## Question

At **compile time only** (no parse changes), how should **`position.in`** and legacy env strings that contain **`in <target>`** (e.g. `C_CV in U[-stress]`, `in U#`) project to **valid ASCA** environment / exception text — including composition with non-empty **`context`**, other **`position`** keys (`adjacent_to`, `near`, `medial`), and existing string env material?

**Do not implement** [174](174-task-position-in-asca-compile-projection.md) until this spike is **resolved** and findings are linked from the map.

## Baseline (corpus at ticket spawn)

| Shape | Count (approx.) | Notes |
| --- | ---: | --- |
| Structured YAML `position.in` only | **38** | No `context` + `in` split yet; targets include `U[±stress]`, `U[+hi]` / `U[+lo]`, `U:[+stress]`, `#U`, prose outliers (`the`, `prefixes`, …) |
| String `env` / `exception` with embedded `in U…` / `in #U` | **50+** | e.g. `C_CV in U[-stress]` — stays one string at parse; compile must handle without parse extraction |

Today: structured `in` → `in {v}` at [`materialize_index_rule_env_exception`](../../../src/conlanger/compile/resolve_index_rule.py); some targets later rewrite in [`syllable_position.py`](../../../src/conlanger/compile/tools/asca/syllable_position.py) during the per-field ASCA pipeline. That split is hard to reason about and is not fully covered (e.g. `U[+lo]` may remain `in U:[+lo]`).

## Research tasks

1. **ASCA primary sources** (fork pinned in [DEV.md](../../../docs/DEV.md)) — syllable membership, stress, word-edge syllables:
   - [Syllable structure matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching)
   - [Underline structures](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#underline-structures) / environment sets (reuse ticket 98 probe conclusions where applicable)
   - Whether literal Index `in …` is ever valid ASCA or always a compile rewrite

2. **Inventory table** — classify every rule with structured `position.in` and every string env/exception matching embedded `in <target>` (regex or script); columns: `rule_id`, field, Index surface, target class, proposed ASCA env/exception, validation probe result, defer/manual if prose.

3. **Target-class mapping** — for each class, document ASCA output and semantics at `_`:
   - Mechanical `#U`, `U#`, `#U, U#` (ticket 98)
   - Syllable stress / height / feature matrices on `U` (`U[+stress]`, `U[-stress]`, `U:[+stress]`, `U[+lo]`, …)
   - Segment / set targets if present in `in`
   - Interaction with **`context` + `in`** (comma-join policy per [144](144-implement-indexcontext-compile-resolution.md) / [163](163-task-prose-position-env-string-fixes.md))

4. **Compile placement (owner 2026-10-18)** — recommend **one** compile-only integration point (no ingest/parser edits):
   - **Option B1:** extend projection in / around [`materialize_index_rule_env_exception`](../../../src/conlanger/compile/resolve_index_rule.py) / [`project_index_context.py`](../../../src/conlanger/compile/project_index_context.py) so `position.in` (and merged `context` + `in`) emit ASCA-ready strings; or
   - **Option B2:** add an explicit **post-materialize** compile transform (before or after existing per-field pipeline) that rewrites `in …` tails and `#U` / `U#` on env/exception strings only.

   Criteria: single documented behaviour, testable without relying on accidental string equality between materialize and a late pipeline pass; reuse ticket 98 ASCA targets via shared helpers.

5. **Relation to [156](156-task-indexcontext-position-in-relation.md)** — state whether default `position_templates.in` remains for unclassified targets or is retired once B1/B2 handles syllable classes.

## Deliverable

Findings markdown under [`.scratch/rule-index/research/`](../research/) (suggested name: `position-in-asca-compile-projection.md`) with inventory appendix or CSV, probe references, and a **recommended option B1 vs B2** for [174](174-task-position-in-asca-compile-projection.md).

## Answer (2026-10-18)

- **Findings:** [position-in-asca-compile-projection.md](../research/position-in-asca-compile-projection.md) + [inventory CSV](../research/position-in-asca-compile-projection.csv) (**68** rows: **38** structured `position.in`, **30** embedded phonological `in` tails; **15** manual/defer).
- **ASCA:** Editorial Index `in …` is **never** valid ASCA; compile must rewrite (probed on fork 0.10.3).
- **Placement:** **B2** — post-materialize env/exception rewriter in the ASCA field pipeline (extend [`syllable_position.py`](../../../src/conlanger/compile/tools/asca/syllable_position.py)); keep [`materialize_index_rule_env_exception`](../../../src/conlanger/compile/resolve_index_rule.py) applier-neutral (`in {v}` per [156](156-task-indexcontext-position-in-relation.md)).
- **Defer (174 out of automated scope):** Middle English / Yupik prose `#U` tails; Blackfoot `O_ in #U` prefix+edge; Chatino `U[+long -stress]`; morpho `in prefixes` / `in the` / `Pre-Livonian`; open/closed `U[+lo]` until ASCA feature policy is locked.

## Acceptance

- [x] Findings file committed under `research/` — [position-in-asca-compile-projection.md](../research/position-in-asca-compile-projection.md) (+ [CSV](../research/position-in-asca-compile-projection.csv))
- [x] Every structured `position.in` row has a proposed compile outcome or explicit defer
- [x] Embedded string env `in <target>` patterns covered in the same mapping table
- [x] ASCA doc citations + minimal `asca validate` probes for non-obvious classes
- [x] Clear handoff: implementation checklist for [174](174-task-position-in-asca-compile-projection.md)

## Out of scope

- Parse-time extraction of embedded `in` into structured `position` (deferred; compile must accept current YAML shapes).
- Dialect `in … dialects` ([manual_mappings.yml](../../../config/parser/manual_mappings.yml)).
- Changing applier-neutral SoT strings in YAML.

## Related

- [156](156-task-indexcontext-position-in-relation.md), [163](163-task-prose-position-env-string-fixes.md), [143](143-implement-index-rule-normalisation-passes.md) (parse extraction v1 for whole-field `in`)
