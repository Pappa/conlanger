Type: task
Status: needs-detail
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Correction pass for grouping letters on insertion rules after 0011.
Blocked by: 0011

## Problem Statement

The `incomplete_matrix` cluster includes insertion rules blocked until grouping-on-insertion policy exists.

## Description

Implement the correction pass per resolved policy on [0011](0011-decision-asca-grouping-insertion.md).

## Acceptance Criteria

- [ ] Target cluster rules compile or are explicitly held out with documented reason in **Answer**.
- [ ] Inventory ok delta recorded in **Answer**.
- [ ] **`Status: resolved`**; sync plan table; `uv run check` ([backlog.md](../../docs/agents/backlog.md) § Closing a backlog item).

## Comments
