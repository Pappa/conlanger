Type: task
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Project syllable tails inside `:{…}:` env sets from `… in U[+F]` string envs.
Blocked by:

## Problem Statement

Twenty-one `expected_underscore` failures build ASCA env sets via **`project_position_in_compiled_field`**, but the syllable side of `seg_ in U[+open]` stays as `%[+lo]` / `%[+hi]` inside the set ([0045](../spikes/0045-expected-underscore-syllable-compile-review.md) family **F3**). Representative rules: Luwian-D-R, French-∅_6.

## Description

When string envs split on ` in ` and wrap as `:{left, right}:`, rewrite **right-hand syllable fragments** using the same underline-scope projection as tasks **0046** and **0047** (`<(..)_(..)>:[±F]`, not bare `%[±F]`). Apply in `project_position_in_compiled_field` (and call sites) after materialize where needed.

**In scope:** F3 rule keys listed in [0045 § F3](../spikes/0045-expected-underscore-syllable-compile-review.md) (Luwian-D-R, French-∅_6, Hittite-e, Gothic-iji_2, … — see triplet CSV `fix_family` = F3).

**Out of scope:** Prose-only tails inside sets (Hittite-e, Gothic-iji_2) — hold per env/prose policy **[0025](0025-decision-env-and-prose-conditions.md)** unless prose strip is already in scope elsewhere; do not block this task on full prose fidelity. F4 exception/`//` prose on Middle English `ɑ-e-o` and French-ò.

## Acceptance Criteria

- [x] For F3 representatives Luwian-D-R and French-∅_6, compiled env sets contain projected syllable scopes (e.g. `<(..)_(..)>:[+lo]`) instead of `%[+lo]` inside `:{…}:`.
- [x] At least 15 of 21 F3 rule keys no longer fail with `expected_underscore` solely due to bare `%[±F]` inside env sets (remainder documented in **Comments** with prose/`}:` blocker).
- [x] Unit tests cover `seg_ in U[+lo]` → `:{seg_, <(..)_(..)>:[+lo]}:` (or validated equivalent).
- [x] `uv run check` passes; **`Status: resolved`**; sync plan **Tasks** table.

## Comments

Inventory (2026-11-07): `expected_underscore` **83 → 70** (−13). **12 / 21** F3 family rows no longer `expected_underscore`; **all 6** F3 rows that had bare `%[±F]` in env sets (triplet CSV) are projected — Luwian-D-R, French-∅_6, Hittite-e, Gothic-iji_2, Tataltepec-Chatino-l-n, Yaitepec-Chatino-lʲ. **9** F3 rows remain `expected_underscore` for prose/`}:` env-set splits (American-English-j, Polish-Cʲ, Proto-Bantu/Manenguba C₁/C₂, Old-Provençal, Chilliwack/Nooksack) — out of scope per ticket. Several cleared rows still **FAILED** `syntax_other` (syllable tier stress/tone only).
