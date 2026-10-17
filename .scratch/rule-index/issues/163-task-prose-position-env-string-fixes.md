Type: task
Status: resolved
Blocked by: [162](162-grill-syllable-structure-env-resolution.md)

# Task: prose position env string fixes (ticket 107) + compile projection

Spawned from [Grill: parse-time ASCA env/exception strings vs structured `IndexContext`](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) (2026-10-17).

## Question

Implement owner-confirmed **107** prose-position targets in `prose_position_env.py` and wire **compile** projection per [Grill: syllable-structure env resolution](162-grill-syllable-structure-env-resolution.md) so regen inventory reflects valid ASCA where policy requires `_`/focus.

## Parse targets (149 Q2)

| Index prose | Was (code today) | Target SoT `env` string |
| --- | --- | --- |
| `unstressed syllables` | `%[-stress]` | `U[-stress]` |
| stressed syllable (phrase TBD from inventory) | — | `U[+stress]` |
| `accented or stressed monosyllables` | `#_[+stress]` | `#U[+stress]#` |
| `final syllables` / syllable-final variants | `U#` | keep `U#` |
| `between two vowels …` | `V_V` | keep until inventory says otherwise |
| `not universal?` | `_` + `sporadic` | keep |

Update `tests/conlanger/tools/ingest/test_prose_position_env.py` (remove TODOs where policy is now locked).

## Compile (162 + 149 Q5 medial)

- Project syllable env strings (`U[-stress]`, `U[+stress]`, `#U[+stress]#`, `U#`, …) to ASCA per **162** Answer; coordinate with [156](156-task-indexcontext-position-in-relation.md) templates where overlap exists.
- **Medial:** when `position.medial` is set, compile **merges** `#_, _#` into the exception string even if an exception already exists (149 Q5); accept dup/invalid risk until HTML-attested fixes.

## Acceptance

- [x] `normalize_bare_prose_position_env` / `apply_prose_position_env_conditions` emit target SoT strings.
- [x] Compile + `validate_rules` behaviour documented in tests; inventory delta summarized after `create_index && compile_rules && validate_rules`.
- [x] `raw` unchanged; ADR-0010 hold-outs respected.

## Answer (2026-10-17)

- **Parse:** `prose_position_env.py` — `U[-stress]`, `U[+stress]`, `#U[+stress]#`; optional leading `in` on unstressed/stressed syllable phrases.
- **Compile:** `syllable_position.project_syllable_stress_compiled_env` — whole-field → `_ $[±stress]` / `#_[+stress]`; `position.in` comma tails → `context in $[±stress]`.
- **Medial:** `merge_medial_boundary_exception` in `resolve_rule_env_exception_for_compile` (149 Q5).
- **Inventory** (`create_index && compile_rules && validate_rules`): **8281** OK (**+9** vs pre-regen **8272** on same asca 0.10.3); **9** ok-flips in changelog (e.g. `Northern-Middle-English-ʃ`, `Lydian-e,o`, `Mekens-k`, `Tunisian-Arabic-Vː_2`). `expected_underscore` −1; `unknown_grouping` U-host cluster −4.

## Out of scope

- **108** `//` structured split → [164](164-task-structured-double-slash-env-parse-compile.md).
- Parser pass order → [165](165-task-parser-env-pipeline-reorder.md).

## Related

- [107 correction pass](107-correction-pass-prose-env-positions.md) · [162](162-grill-syllable-structure-env-resolution.md) · [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md)
