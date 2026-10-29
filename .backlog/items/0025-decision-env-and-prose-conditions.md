Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Prose env, parallel nulls, syllable tails, identity exceptions (Family A).
Blocked by:

## Question

How should **prose environments**, **parallel outputs**, **syllable-position tails**, and **`! Host =`** identity exclusions be represented before ASCA compile?

## Answer

Prefer **structured IndexContext** over ASCA env literals in SoT ([ADR-0017](../../docs/adr/0017-structured-env-exception-indexcontext.md)). Prose env phrases, **double-slash** env, parallel **`∅`** outputs, and **`#U` / `U#`** tails are normalized via parse/compile stages documented in SYSTEM.md.

**Env-bound `! Host = RHS`** exclusions use **Family A** compile substitution into the env slot; Family B residuals and suffix policy remain open under decision **0009** and task **0010**.

## Comments

- Migrated summary (2026-10-29): env/prose correction cluster + early identity-exception pass merged.
