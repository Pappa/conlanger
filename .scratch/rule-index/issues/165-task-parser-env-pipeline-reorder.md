Type: task
Status: resolved
Blocked by: [163](163-task-prose-position-env-string-fixes.md), [164](164-task-structured-double-slash-env-parse-compile.md)

# Task: parser env pipeline reorder (149 Q4)

Spawned from [Grill: parse-time ASCA env/exception strings vs structured `IndexContext`](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) (2026-10-17).

## Question

Reorder post-`init()` env passes in `IndexDiachronicaParser` so structured capture (**143** position extraction, **108** split) is not undermined by passes that still emit ASCA-only literals at parse, and retire any remaining Tier C ASCA writers (`%[-stress]`, `#_[+stress]`, ASCA `//` tails, colon matrices in `context`).

## Target order (149 Answer)

After stress (22) and prose conditional (134):

1. Index env prose → **Index/project strings** or **structured `IndexContext`** (107 + 143; no ASCA Tier C at parse).
2. **108** mechanical ` // ` split into structured env/exception (see [164](164-task-structured-double-slash-env-parse-compile.md)).
3. Feature/IPA on `context` strings (119 family).
4. Position extraction / dialect passes as needed.
5. No pass after structured capture re-introduces ASCA env literals.

Document final order in `parser.py` module docstring and, if needed, `docs/system/index-diachronica-parser.md`.

## Acceptance

- [x] `parser.py` pass order matches policy; grep confirms no parse module writes Tier C ASCA env strings post-reorder.
- [x] Full test suite + `uv run create_index && uv run compile_rules && uv run validate_rules` with no unexpected inventory regression beyond documented deltas from **163**/**164**.
- [x] Syllable editorial strip (`apply_syllable_position_editorial_strip`) placement justified or moved per [150](150-grill-parse-compile-module-seams.md) (optional note in PR; full seam grill not required to close).

## Answer (2026-10-18)

- **Order:** After `init()`, series (D0) and D1–D3 (sporadic, glosses, stress), env block is conditional **134** → prose position **107** → double-slash **108** → syllable editorial strip **98** → feature/IPA **119** → position extraction **143** → dialects. Documented in `parser.py` module docstring and Phase D table in `docs/system/index-diachronica-parser.md`.
- **Tier C:** No parse-time writers for `%[-stress]`, `#_[+stress]`, or ASCA `//` tails in env modules after **163**/**164**; passthrough of HTML literals unchanged.
- **Syllable strip:** Stays immediately after **107**/**108**, before feature/IPA — normalizes mechanical `in #U`/`in U#` on final `context` strings without importing compile ([150](../issues/150-grill-parse-compile-module-seams.md)).
- **Inventory:** Regen unchanged vs **164** baseline (9260 OK).

## Related

- [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) · [163](163-task-prose-position-env-string-fixes.md) · [164](164-task-structured-double-slash-env-parse-compile.md) · [143](143-implement-index-rule-normalisation-passes.md)
