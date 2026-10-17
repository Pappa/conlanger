Type: spike
Status: ready-for-agent
Blocked by: None

# Spike: agent-oriented improvements to project documentation

Spawned from [Grill: ASCA-shaped syntax in the applier-neutral rule index](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) (2026-10-17). Owner wants documentation changes (including glossary extraction) grounded in a deliberate audit, not an ad-hoc move.

## Question

What changes to **repo documentation** (structure, navigation, glossary placement, pipeline docs, ADR cross-links, agent entrypoints) would most improve **agent** comprehension and reduce wrong assumptions — without duplicating implementation detail that belongs in code or `.scratch` tickets?

## Scope

- **In scope:** `CONTEXT.md`, `docs/` (`CONLANGER.md`, `SYSTEM.md`, `docs/system/*`, `docs/adr/`), `AGENTS.md`, `docs/agents/*`, relationship to `.scratch/rule-index/` research and map Notes.
- **Out of scope:** rewriting correction-pass tickets; changing parse/compile code; publishing external docs.

## Method (suggested)

- Inventory current agent-facing surfaces (what skills/rules already point at).
- Compare to domain-modeling conventions (`GLOSSARY.md` vs glossary-in-`CONTEXT.md`, ADR triggers).
- Sample failure modes from recent agent work (parse vs compile confusion, SoT vs ASCA, glossary terms).
- Produce a **prioritised recommendation list** (must / should / nice) with file-level actions.

## Deliverable

Findings markdown under `.scratch/rule-index/research/agent-oriented-docs-improvements.md` (or repo `docs/` only if owner prefers — default scratch). Feeds [155](155-task-glossary-migration-and-docs-improvements.md).

## Resolve with

`/research` skill; close with answer + link on ticket.
