Type: epic-duck:decision
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Policy for inventory `no composed chain paths from stages` failures.
Blocked by:

## Question

Multi-stage rules fail inventory when no composed chain path matches: each step’s compiled input must equal the previous step’s compiled output. At least three corpus rules hit this after composed-chain enumeration (split vs merged stage I/O, stress materialization mismatches).

Decide inventory policy: strict per-step equality vs allowed merged sets, and whether fixes belong in code, SoT edits, or documented hold-outs (`status: skipped` / comments per historical-fidelity policy).

Wayfinder source: `.scratch/rule-index/issues/170-grill-composed-chain-path-inventory-policy.md`.

## Answer

## Comments

- Retyped from **`Type: task`** per [0030](0030-task-retype-open-grill-frontier-as-decisions.md) (2026-10-29).
