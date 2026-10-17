Type: task
Status: ready-for-agent
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

- [ ] `normalize_bare_prose_position_env` / `apply_prose_position_env_conditions` emit target SoT strings.
- [ ] Compile + `validate_rules` behaviour documented in tests; inventory delta summarized after `create_index && compile_rules && validate_rules`.
- [ ] `raw` unchanged; ADR-0010 hold-outs respected.

## Out of scope

- **108** `//` structured split → [164](164-task-structured-double-slash-env-parse-compile.md).
- Parser pass order → [165](165-task-parser-env-pipeline-reorder.md).

## Related

- [107 correction pass](107-correction-pass-prose-env-positions.md) · [162](162-grill-syllable-structure-env-resolution.md) · [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md)
