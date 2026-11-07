Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Project structured `position.in` open/closed and stress-on-syllable targets to ASCA underline scopes.
Blocked by:

## Problem Statement

Twelve `expected_underscore` failures use structured `env.position.in` with syllable features (`U[+hi]`, `U[+lo]`, `#U:[+stress]`, `U[+long -stress]`, …). Materialize emits bare `%[+F]` or `#%:[+stress]` with no valid underline scope, so ASCA rejects the env ([0045 spike](../spikes/0045-expected-underscore-syllable-compile-review.md) family **F2**).

## Description

Extend **`project_position_in_target()`** / **`materialize_position_in_asca()`** so unclassified Index open/closed and multi-feature syllable targets follow the same pattern as existing stress classification: **`<(..)_(..)>:[±F…]`**, and word-initial stressed syllable **`#<(..)_(..)>:[+stress]`** — no leading free `_` and no bare `%[±F]` for whole-env `position.in`.

**In scope rule keys (family F2 in triplet CSV):** Egyptian-Arabic-aj-aw, Luwian-V_2, French-è, French-è_3, French-ò_2, French-é, French-é_2, French-ó (both steps), French-ó_3, French-a_3, Papabuco-Chatino-ẽ_3.

**References:** [0039-index-syllable-position-u-hash](../spikes/0039-index-syllable-position-u-hash.md), `tests/conlanger/compile/test_position_in_projection.py`, `tests/conlanger/utils/test_syllable_position.py`.

**Out of scope:** F3 env-set tails (task **0048**); F4 exception prose and `//` tails on Kentish `ɑ-e-o` / French-ò (env syllable scope only when exception stays Index-shaped); unrelated U1–U7 rows in [0045](../spikes/0045-expected-underscore-syllable-compile-review.md).

## Acceptance Criteria

- [ ] `project_position_in_target` classifies at least `U[+hi]`, `U[+lo]`, `#U:[+stress]`, and `U[+long -stress]` with expected strings matching underline-scope tests (no leading free `_`).
- [ ] Rules in the F2 list above compile to env strings that pass `validate_rules` for their inventory rows (or are explicitly held out in **Comments** with reason if exception/`//` still fails).
- [ ] `expected_underscore` count drops for those rule keys in a fresh inventory run; delta recorded in **Comments**.
- [ ] `uv run check` passes; **`Status: resolved`**; sync plan **Tasks** table.

## Comments
