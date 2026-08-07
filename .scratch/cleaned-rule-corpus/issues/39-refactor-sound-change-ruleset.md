Type: task
Status: needs-triage
Blocked by: 37

# Refactor SoundChangeRuleSet and compile subcomponents

## Question

Refactor `SoundChangeRuleSet`, `RuleChange`, and related compile helpers in `src/conlanger/tools/rules.py` so the code structure mirrors the documented applier compile pipeline — without changing observable compile output unless a documented ordering fix requires it.

## Context

Grill session (2026-08-07): implementation details are **deferred** until pipeline documentation and ASCA transform ordering are complete. This ticket is a **placeholder**; scope is written after [37](37-document-sound-change-pipeline.md) and [38](38-spike-asca-compile-transform-order.md) resolve.

Current pain: `rules.py` mixes applier formatting (`RuleTitle`, `RuleCitation`, …), top-level ASCA normalizers, and assembly in `SoundChangeRuleSet` / `RuleChange`. Glossary: **`PhonologicalRuleSet`** is the applier-neutral section container; **`SoundChangeRuleSet`** is the applier render/compile output layer ([CONTEXT.md](../../../CONTEXT.md)).

## Preconditions (do not start until unblocked)

1. [Document the sound-change rule pipeline in docs/](37-document-sound-change-pipeline.md) — `docs/sound-change-applier.md` with full transform table.
2. [Spike: ASCA compile transform ordering](38-spike-asca-compile-transform-order.md) — planned transforms have assigned order.

## Scope (to be refined in Answer when unblocked)

**In scope (intent):**

- Explicit ordered compile pipeline (named steps matching docs).
- File/module split as needed for clarity; preserve public imports used by tests and `phonological_ruleset.py`.
- Tests remain green; no dependency additions without owner approval.

**Explicitly not decided yet:**

- Renaming `SoundChangeRuleSet` / `RuleChange`.
- Brassica compiler abstraction.
- Implementing planned transforms (separate implementation tickets expected).

## Notes

- Treat `docs/sound-change-applier.md` as the spec for step names and order after ticket 37.
- Follow TDD (`/tdd`) for any behaviour-changing fixes discovered during refactor.
- `validate_asca` and existing test fixtures are the regression gate.

## Acceptance criteria

- [ ] Ticket body updated with concrete scope after 37 + 38 (claim work only then).
- [ ] Code mirrors documented compile pipeline.
- [ ] Full pytest + ruff gate passes.
- [ ] No undocumented change to compiled ASCA strings for the existing test corpus.

## Comments
