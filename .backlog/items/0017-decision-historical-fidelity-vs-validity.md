Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Fidelity-first editing vs compile validity and correction workflow.
Blocked by:

## Question

When a rule is **historically attested** but **does not compile**, how do we choose edits, hold-outs, and correction-pass scope?

## Answer

Prefer an **edit ladder** that preserves Index meaning where possible ([ADR-0010](../../docs/adr/0010-historical-fidelity-class-first-status.md)). Separate **rule status** / intentional hold-outs from **compile validation** failures in reports.

Run **correction passes** cluster-by-cluster (inventory-driven), not ad hoc one-off fixes. Document skips and manual review when fidelity blocks mechanical compile.

## Comments

- Migrated summary (2026-10-29): fidelity, workflow, and correction-template decisions merged.
