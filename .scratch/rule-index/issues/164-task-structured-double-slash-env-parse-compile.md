Type: task
Status: ready-for-agent
Blocked by: [162](162-grill-syllable-structure-env-resolution.md)

# Task: structured double-slash env/exception (ticket 108) at parse + ASCA at compile

Spawned from [Grill: parse-time ASCA env/exception strings vs structured `IndexContext`](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) (2026-10-17). Policy: **149 Q3**.

## Question

Refactor `double_slash_env.py` so parse **splits** Index ` // ` into structured **`IndexContext`** env and exception (no ASCA `//` grammar or ASCA-only tails in persisted YAML), and **compile** builds the ASCA env/exception strings (including `//` and exception tails).

## Acceptance

- [ ] `apply_double_slash_env_conditions` persists structured `env` / `exception` (`context`, `position`, `dialect` per [144](144-implement-indexcontext-compile-resolution.md)); no Tier C ASCA literals written at parse.
- [ ] Compile projection reproduces today’s compiled lines for a representative fixture set (smoke + prior **108** inventory examples).
- [ ] Tests: `test_double_slash_env.py` updated; compile round-trip tests added or extended.
- [ ] Regen inventory delta documented.

## Out of scope

- **107** string mapping fixes → [163](163-task-prose-position-env-string-fixes.md).
- Global parser reorder → [165](165-task-parser-env-pipeline-reorder.md) (may land in same PR if small).

## Related

- [108 correction pass](108-correction-pass-double-slash-env.md) · [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) · [162](162-grill-syllable-structure-env-resolution.md)
