Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Agent entry: GLOSSARY, SYSTEM, closure and quality gates.
Blocked by:

## Question

Where should **agents** read vocabulary, pipeline stages, and ticket closure expectations for rule-index work?

## Answer

Read order: **[GLOSSARY.md](../../GLOSSARY.md)** → **[docs/SYSTEM.md](../../docs/SYSTEM.md)** (parse → compile → validate) → relevant **ADRs** → this **backlog plan** and linked **decision** tickets (not legacy map Notes as glossary).

Close implementation with **`Status: resolved`**, **`## Answer`** where applicable, **`uv run check`**, and [backlog.md](../../docs/agents/backlog.md) § Closing a backlog item.

## Comments

- Migrated summary (2026-10-29): pipeline docs, glossary migration, agent retro tasks merged.
