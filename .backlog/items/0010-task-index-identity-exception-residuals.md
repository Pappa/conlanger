Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Fix `! Host =` compile residuals after task 0009.
Blocked by: 0009

## Problem Statement

After Family B input narrowing, compiled rules still leave `// Host = RHS` tails that ASCA cannot parse. Some mechanical ok-flips remain where env implies the host slot (for example `_#` with `C = t` on input `C`).

## Description

Implement compile fixes per **0009** **Answer**: omit or empty `exception` when Family B narrows input; recover env-infer cases; re-run inventory and document delta on `expected_number` and remaining hold-outs. Add unit tests for representative rules (including Anejom-C-shaped cases). Do not rewrite YAML `exception` at parse time ([ADR-0010](../../docs/adr/0010-historical-fidelity-class-first-status.md)).

## Acceptance Criteria

- [ ] Compiled output omits invalid `// Host = RHS` tails after Family B narrowing.
- [ ] Inventory re-run documents ok delta and lists remaining hold-outs per **0009**.
- [ ] Unit tests cover fixed representative rules.
- [ ] **`Status: resolved`** with **Answer** per implement-closure.

## Comments
