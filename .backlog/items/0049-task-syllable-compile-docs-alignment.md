Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Align sound-change-applier docs with syllable underline-scope compile behaviour.
Blocked by: 0047, 0048

## Problem Statement

[`docs/system/sound-change-applier.md`](../../docs/system/sound-change-applier.md) describes `position.in` and syllable-stress compile output as `_ $[±stress]`, `_ %[+stress]…`, `context in $[±stress]`, and `#_[+stress]`. Tests and compile code emit **underline scopes** (`<(..)_(..)>:[±F]`, `#<(..)_(..)>:[+stress]#`, `context in <(..)_(..)>:[±stress]`). That drift caused incorrect fix guidance during task **0045**.

## Description

Update the **Structured `env` / `exception` (`IndexContext`)** table (and any cross-links in the same doc) to match post–**0046**–**0048** behaviour:

- Distinguish **whole-env syllable scope** (`<(..)_(..)>:[±F]`) from **segment-adjacent env** (`w_` + neighbour template, env sets with segment focus).
- Document classified `position.in` targets with examples from `tests/conlanger/compile/test_position_in_projection.py`.
- Remove or correct stale `_ $…` / `_ %…` / `in $[±stress]` rows unless a code path still emits them (cite test or source).

Optionally add a one-line pointer in [0045 spike](../spikes/0045-expected-underscore-syllable-compile-review.md) § TLDR that operator docs were corrected here.

**Out of scope:** Implementing compile changes (tasks **0046**–**0048**); unrelated `expected_underscore` families U1–U7.

## Acceptance Criteria

- [ ] `sound-change-applier.md` `position.in` and syllable-stress rows match actual compile output exercised by `uv run pytest tests/conlanger/compile/test_position_in_projection.py tests/conlanger/utils/test_syllable_position.py --no-cov`.
- [ ] Doc explicitly states that whole-env syllable conditions use underline structures, not a leading free `_` before `%` or `$`.
- [ ] No contradiction with [0039-index-syllable-position-u-hash](../spikes/0039-index-syllable-position-u-hash.md) or spike **0032** env focus rules.
- [ ] `uv run check` passes; **`Status: resolved`**; sync plan **Tasks** table.

## Comments
