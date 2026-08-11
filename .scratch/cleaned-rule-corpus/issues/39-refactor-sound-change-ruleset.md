Type: task
Status: resolved
Blocked by:

# Refactor DiachronicSeries and compile subcomponents

## Question

Refactor `DiachronicSeries`, `RuleChange`, and related compile helpers in `src/conlanger/tools/rules.py` so the code structure mirrors the documented applier compile pipeline — without changing observable compile output unless a documented ordering fix requires it.

## Context

Grill session (2026-08-07): implementation details are **deferred** until pipeline documentation and ASCA transform ordering are complete. This ticket is a **placeholder**; scope is written after [37](37-document-sound-change-pipeline.md) and [38](38-spike-asca-compile-transform-order.md) resolve.

Current pain: `rules.py` mixes applier formatting (`RuleTitle`, `RuleCitation`, …), top-level ASCA normalizers, and assembly in `DiachronicSeries` / `RuleChange`. Glossary: **`PhonologicalRuleSet`** is the applier-neutral section container; **`DiachronicSeries`** is the applier render/compile output layer ([CONTEXT.md](../../../CONTEXT.md)).

## Scope (resolved)

**In scope (done):**

- `src/conlanger/tools/asca_compile/` package: one module per transform + `pipeline.py` with `ASCA_COMPILE_STEP_NAMES` and `compile_asca_rule_string`.
- `rules.py` retains section assembly classes; re-exports transform helpers for existing callers/tests.
- No-op placeholders for planned steps 3, 4, 10 (`planned.py`) wired in documented order ([spike 38](../research/asca-compile-transform-order.md)).
- `docs/sound-change-applier.md` updated to reference pipeline module and order integers.

**Out of scope (unchanged):**

- Renaming `DiachronicSeries` / `RuleChange`.
- Brassica compiler abstraction.
- Implementing planned transforms (separate tickets).

## Acceptance criteria

- [x] Ticket body updated with concrete scope after 37 + 38 (claim work only then).
- [x] Code mirrors documented compile pipeline.
- [x] Full pytest + ruff gate passes.
- [x] No undocumented change to compiled ASCA strings for the existing test corpus.

## Comments
