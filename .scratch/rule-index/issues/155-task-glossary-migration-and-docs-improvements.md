Type: task
Status: resolved
Blocked by: 154

# Task: glossary migration and documentation improvements

Spawned from [Grill: ASCA-shaped syntax in the applier-neutral rule index](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) (2026-10-17).

## Question

Implement the documentation improvements **approved** from [Spike: agent-oriented improvements to project documentation](154-spike-agent-oriented-docs-improvements.md), including at minimum:

1. **Glossary migration** — extract domain terms from `CONTEXT.md` into root `GLOSSARY.md` per domain-modeling skill (implementation-free definitions); leave `CONTEXT.md` as project overview + pointers, or slim per spike recommendations.
2. **Sync pipeline / SoT docs** with [148](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) policy (stress postfix, `%`/`$`, dual feature configs, no arrows in cleaned fields) wherever spike ranks those as must-do.
3. **Fix broken or misleading links** and agent entrypaths identified by the spike.

## Acceptance

- Spike checklist items marked **must** are done; **should** items either done or explicitly deferred with a one-line reason on this ticket.
- `GLOSSARY.md` exists and follows the domain-modeling skill `GLOSSARY-FORMAT.md` (definitions only, no implementation).
- `CONTEXT.md` / `docs/SYSTEM.md` / `docs/agents/*` updated so humans and agents have a single obvious “start here” path.
- No requirement to run full regen; doc-only unless spike mandates a small doc example fix.

## Out of scope

- Implementing [153](153-task-atomic-syllable-symbol-compile-migration.md) or feature-config code splits (link from docs only).

## Answer

**Resolved 2026-10-17.** Created [GLOSSARY.md](../../../GLOSSARY.md); slimmed [CONTEXT.md](../../../CONTEXT.md); fixed `docs/system/*` ADR links; updated pipeline docs, [AGENTS.md](../../../AGENTS.md), [docs/agents/domain.md](../../../docs/agents/domain.md), [SYSTEM.md](../../../docs/SYSTEM.md), [spec](spec.md), [CONLANGER.md](../../../docs/CONLANGER.md). Spike **should** items 12 (redirect comment on applier-neutral-index-validation) and 8–11 done; **nice** items 13–16 deferred (map hygiene, per-ADR agent one-liners).
