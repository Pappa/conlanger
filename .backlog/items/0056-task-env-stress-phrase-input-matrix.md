Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Strip env stress prose to comment and attach [±stress] to rule input (pass D3).
Blocked by:

## Problem Statement

`apply_stress_conditions` and `normalize_stress_conditions` still follow legacy pass 22 behavior: they reshape env strings for an old ASCA focus convention and often leave English `when stressed` / `when unstressed` in **environment** `context`. About 136 rules in `data/diachronica/index_diachronica.yml` still carry that prose in `env`. The parser carries an open TODO at the call site. **GLOSSARY** **Environment** and product intent require capture-not-discard: stress qualifiers become **rule comment**, and segment stress at the change site becomes `[-stress]` or `[+stress]` on the rule **input** (first **stages** member), not lingering env prose.

## Description

Rewrite pass **D3** so it matches **GLOSSARY** and ticket **134** input-matrix merge patterns (`apply_prose_conditional_env_conditions`).

**Detect and strip** (env and exception `context`):

- Trailing or comma-prefixed `when stressed` / `when unstressed` (case-insensitive).
- **Full stress tail** from the `when …` anchor through following qualifiers on the same env field (e.g. `unless primarily stressed`, `(?)` glued to the phrase). Captured text goes to **rule comment** via `merge_comment`.
- After a `#` host in env, strip the same stress tail to comment (today partial); do not leave the phrase in `context`.

**Apply input matrix** when stripping indicates segment stress on the changed token at `_`:

- `when stressed` → attach `[+stress]` to the first **stages** input (merge with an existing postfix matrix if present, e.g. `V[+mid]` → `V[+mid,+stress]` or equivalent canonical form).
- `when unstressed` → attach `[-stress]`.

**Exception (user decision):** `when neither vowel is stressed` — capture phrase to comment only; keep env such as `V_V` unchanged; do **not** add an input matrix.

**Out of scope for this ticket** (other passes own these):

- Whole-env bare `/ stressed` or `/ unstressed` (manual mapping or future dedicated pass).
- Syllable prose (`in unstressed syllables` → `U[-stress]`) — `apply_prose_position_env_conditions`.
- Conditional env (`if the *seg is not stressed`, unstressed penult) — `apply_prose_conditional_env_conditions`.

Update unit tests in `tests/conlanger/tools/ingest/test_transforms.py`. **Do not discard return values in tests** (today `test_normalize_stress_conditions` binds `captures` to `_`). Each parametrized case must assert **every** value the helper returns—at minimum `cleaned` env string and `captures` list; if the API adds a third value (e.g. `input_matrix: str | None` for `[±stress]`), assert that too on the same cases. `test_apply_stress_conditions` must assert the full rule shape affected by the pass: `stages`, `env`/`exception`, and `comment` when captures merge. Prefer tuple fixtures `(text, expected_cleaned, expected_captures, …)` over env-only expected strings.

Align `docs/system/index-diachronica-parser.md` step D3 and `docs/system/validate.md` pass 22 wording with behavior. Regenerate the index YAML so stress prose no longer appears in env/exception `context` for handled patterns.

## Acceptance Criteria

- [ ] `a → i / _C(C), when stressed` parses to `env: _C(C)`, `comment` containing the full stress tail, input stage with `[+stress]` on `a`.
- [ ] `V → ∅ / C_# when unstressed ! …` parses to `env: C_#`, stress tail in `comment`, input `V` with `[-stress]`.
- [ ] `V_V, when neither vowel is stressed` parses to `env: V_V`, phrase in `comment`, input **unchanged** (no `[-stress]`).
- [ ] Env-only `… when stressed unless primarily stressed` captures the **entire** tail in `comment` and applies `[+stress]` to input; env loses the tail.
- [ ] `#_ when unstressed` strips tail to `comment` and applies `[-stress]` to input (not comment-only).
- [ ] `test_normalize_stress_conditions` parametrization asserts **all** return values per row (`cleaned`, `captures`, and any added matrix flag); no ignored tuple slots.
- [ ] `test_apply_stress_conditions` parametrization asserts `stages`, env/exception, and `comment` wherever the pass mutates them.
- [ ] `uv run pytest tests/conlanger/tools/ingest/test_transforms.py --no-cov` passes.
- [ ] Fresh `uv run create_index` yields no `when stressed` / `when unstressed` substrings in `env` or `exception` `context` for rules covered by the patterns above (material drop from the current ~136 occurrences).
- [ ] D3 row in `docs/system/index-diachronica-parser.md` describes comment strip + input matrix, not “ASCA env with `_` focus prefix”.
- [ ] `uv run check` passes on a clean tree after changes.

## Comments

- Rubber-duck session (2026-11-22): user confirmed neighbour-vowel exception, full-tail comment capture, task-only outcome.
- 2026-11-22: require full return-value coverage in `normalize_stress_conditions` / `apply_stress_conditions` unit tests (no `_` discards).