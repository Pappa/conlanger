Type: grilling
Status: resolved
Blocked by: None

# Grill: syllable-structure env resolution

Spawned from [Grill: parse-time ASCA env/exception strings vs structured `IndexContext`](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) (2026-10-17). Owner: corrected **107** prose-position targets (`U[-stress]`, `U[+stress]`, `#U[+stress]#`, …) are valid **Index / project** env surface, but many compiled rules **fail validation** today because the env lacks a focus **`_`** (or equivalent) under ASCA rules.

## Question

For **syllable-level** and **word-boundary** env strings in the applier-neutral index (with or without `_`), what is the SoT shape, when must parse inject or preserve `_`, and how does compile project to valid ASCA env/exception — without conflating Index notation with ASCA-only colon/`//` grammar?

## Examples to resolve (owner 2026-10-17)

| Index prose (107) | Target SoT env string (post-parse) | Known issue |
| --- | --- | --- |
| `unstressed syllables` | `U[-stress]` (not `%[-stress]`) | compile/validate may fail: no `_` |
| (stressed syllable — phrase TBD) | `U[+stress]` | same |
| `accented or stressed monosyllables` | `#U[+stress]#` (not `#_[+stress]`) | same |
| `final syllables` | `U#` (keep today) | underscore / focus policy TBD |

## Out of scope

- Moving `%`/`$` at stages (**[153](153-task-atomic-syllable-symbol-compile-migration.md)**).
- General `position.in` templates (**[156](156-task-indexcontext-position-in-relation.md)**) except where this grill locks syllable-specific compile behaviour.
- **Medial `#_, _#` merge** when `position.medial` — locked in [149 Answer](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md#answer) (compile merges with existing exception; no skip-if-exception).

## Deliverable

Policy + examples for parse vs compile; acceptance criteria for a follow-on **task** (fix 107 mappings + compile projection). Do **not** implement until this grill is **resolved**.

## Answer (2026-10-17)

- **SoT (parse):** Index project strings `U[-stress]`, `U[+stress]`, `#U[+stress]#`, `U#`, … in `env.context` — no injected `_` at parse.
- **Compile:** Syllable-stress whole env projects to ASCA `_ $[±stress]` (segment focus + syllable stress after `U`→`%`→`$`). Stressed monosyllable `#U[+stress]#` → `#_[+stress]`. Embedded `position.in` tails use `context in $[±stress]` (not comma-before-`in`). Mechanical `#U`/`U#` unchanged (ticket 98).
- **Implemented in:** [163](163-task-prose-position-env-string-fixes.md).
