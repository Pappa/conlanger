Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: IndexRule lifecycle, normalisation passes, IndexContext compile resolution.
Blocked by:

## Question

What **parse-time model** carries index rules, surface normalisation, and structured env/exception into compile?

## Answer

Introduce typed **`IndexRule`** lifecycle: parse raw rule lines, run **normalisation passes**, attach structured **env/exception** (IndexContext), then compile to ASCA without round-tripping ASCA through YAML SoT ([ADR-0016](../../docs/adr/0016-parse-pipeline-order-and-raw-semantics.md), [ADR-0017](../../docs/adr/0017-structured-env-exception-indexcontext.md)).

**`raw`** retains Index surface for fidelity; compiled fields are derived at compile/inventory time.

## Comments

- Migrated summary (2026-10-29): IndexRule/IndexContext implement + refactor arc merged.
