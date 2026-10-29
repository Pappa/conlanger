Type: task
Status: resolved
Plan: [0001-plan-migrate-project-to-duck-skills.md](0001-plan-migrate-project-to-duck-skills.md)
Overview: Retype open wayfinder grill backlog items as epic-duck decisions on plan 0003.
Blocked by:

## Problem Statement

[Wayfinder ticket migration](0008-task-execute-wayfinder-rule-index-migration.md) filed four open **grill** wayfinder tickets as rubber-duck **`Type: task`** items (**0009**, **0011**, **0013**, **0014** on plan **0003**). Their bodies ask for a binding **`## Answer`**, not implementation deliverables.

That conflicts with:

- **Wayfinder** — **`grilling`** tickets are HITL **decisions** ([issue-tracker.md](../../docs/agents/issue-tracker.md) child ticket `Type:`; wayfinder skill **Grilling** ticket type).
- **Plan 0003 Notes** — closed wayfinder grills migrated as **`Type: epic-duck:decision`** with **`## Answer`** ([0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)).
- **0006** — open frontier grills should follow the same **decision** shape as closed grills; the migration table row that lists them as **`Type: task`** was a filing mistake, not a policy exception.

Follow-on compile work (**0010**, **0012**) correctly stays **`Type: task`**.

## Description

For each grill item below, convert the backlog record to **`Type: epic-duck:decision`** on plan **0003** without changing shared **`NNNN`** or wayfinder source links:

| NNNN | Wayfinder source |
|------|------------------|
| **0009** | [167-grill-index-identity-exception-env-splice.md](../../.scratch/rule-index/issues/167-grill-index-identity-exception-env-splice.md) |
| **0011** | [125-grill-asca-grouping-insertion.md](../../.scratch/rule-index/issues/125-grill-asca-grouping-insertion.md) |
| **0013** | [129-grill-section-mappings-feature-matrices-yaml-compile.md](../../.scratch/rule-index/issues/129-grill-section-mappings-feature-matrices-yaml-compile.md) |
| **0014** | [170-grill-composed-chain-path-inventory-policy.md](../../.scratch/rule-index/issues/170-grill-composed-chain-path-inventory-policy.md) |

Per file:

1. Set **`Type: epic-duck:decision`** and keep **`Plan:`** **0003**.
2. Replace deliverable sections with decision shape: **`Overview`**, **`## Question`** (from current problem/description), empty **`## Answer`** until resolved, **`## Comments`** (preserve migration notes; cite wayfinder paths in comments only if needed for archaeology).
3. Rename the file to **`<NNNN>-decision-<slug>.md`** (drop `task-grill` / `task` prefix in the slug; keep the same **NNNN**).
4. Set **`Status:`** to match current readiness (**0009** stays **`in-progress`** if grill work is active; others **`ready`** when the question is already sharp).
5. Remove grill-specific acceptance criteria that duplicate decision closure (**Answer** + **`Status: resolved`** per [implement-closure.md](../../docs/agents/implement-closure.md) applies when the decision is resolved later, not in this task).

Update plan **0003**:

- Move the four rows from **Tasks** to **Decisions** (accurate **Overview** / **Status**).
- Leave **0010** and **0012** in **Tasks**; verify **`Blocked by:`** still references the same **NNNN** after renames.
- Refresh **Notes** / **Decisions so far** gists that mention “0009–0010” grill vs task roles if wording implies **0009** is implementation work.

Update plan **0001** **Tasks** table: add this item; mark **`Status: resolved`** when done.

Optional hygiene (same PR/session if small):

- Add a one-line **Comments** note on **0006** that open frontier **grilling** tickets become **`epic-duck:decision`**, not rubber-duck **`Type: task`**.

## Out of Scope

- Resolving the four decisions (grill sessions — **question-duck** / **grilling**).
- Retyping **0010** or **0012** (implementation tasks).
- Changing `.scratch/` wayfinder files.

## Acceptance Criteria

- [x] **0009**, **0011**, **0013**, and **0014** exist as **`Type: epic-duck:decision`** files named **`<NNNN>-decision-*.md`** with **`Plan:`** **0003** and a **`## Question`** section; no **`Type: task`** grill duplicates remain under those numbers.
- [x] Plan **0003** **Decisions** table lists all four; **Tasks** table lists only implementation follow-ons (**0010**, **0012**, etc.) plus any non-grill tasks.
- [x] **0010** **`Blocked by:`** still blocks on **0009**; **0012** on **0011** (by number or correct renamed path).
- [x] Plan **0003** indexed outcome count stays **≤25** per **0006** (re-table only; no new scope).
- [x] Plan **0001** **Tasks** row for **0030** shows **`Status: resolved`** when complete.

## Answer

Retyped **0009**, **0011**, **0013**, **0014** to **`epic-duck:decision`** on plan **0003** (2026-10-29). Plan **0003** **Tasks** now holds **0010** / **0012** plus resolved **0008**; **Decisions** table lists four open frontier decisions. **0006** Comments amended.

## Comments

- 2026-10-29: Filed after epic-duck review — grill frontier mis-typed during **0008** execution.
- 2026-10-29: Executed via dev-duck.
