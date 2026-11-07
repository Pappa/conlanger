Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Map whole-field `U[±F]` / `%[±F]` env strings to syllable underline scopes.
Blocked by:

## Problem Statement

When the entire env is a syllable-class feature matrix (e.g. `U[-nas]` → compiled `%[-nas]`), ASCA reports `expected_underscore` because `%[±F]` is not a valid syllable-scope env ([0045](../spikes/0045-expected-underscore-syllable-compile-review.md) family **F1**; representative `Miami-Illinois-s-ʃ`).

## Description

Extend **`project_syllable_stress_compiled_env`** / **`_compile_syllable_stress_env_from_raw`** (and related syllable-position pass hooks) so whole-field syllable matrices project to **`<(..)_(..)>:[±F]`** — underscore only inside the underline template, same as `U[±stress]` / `%[±stress]`, not a leading free `_` before `%`.

**In scope rule keys (family F1):** Miami-Illinois-s-ʃ.

**References:** `src/conlanger/compile/tools/asca/syllable_position.py`, `tests/conlanger/utils/test_syllable_position.py`.

**Out of scope:** Structured `position.in` (task **0046**); string env `… in U[+open]` splits inside env sets (task **0048**).

## Acceptance Criteria

- [ ] Whole-field env raw forms such as `U[-nas]` and post-mapping `%[-nas]` rewrite to `<(..)_(..)>:[-nas]` (or equivalent validated ASCA syllable scope) before validate.
- [ ] `Miami-Illinois-s-ʃ` inventory row is no longer `expected_underscore` after compile + validate (or held out in **Comments** with explicit blocker).
- [ ] New or extended unit tests mirror `_SYLLABLE_STRESS_ENV_RAW` patterns for at least one non-stress feature matrix.
- [ ] `uv run check` passes; **`Status: resolved`**; sync plan **Tasks** table.

## Comments
