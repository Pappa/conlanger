Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Populate plan 0003 from `.scratch/rule-index/` using the pipeline-stage merge policy in decision 0006.
Blocked by:

## Problem Statement

The cleaned rule index effort still lists **~173** wayfinder tickets under `.scratch/rule-index/`, while duck-skills planning lives on plan **0003** with empty **Decisions so far** and **Tasks** tables. Agents need a compressed, actionable **`.backlog/`** view without 1:1 ticket copies or resurrecting dead scope.

## Description

Execute the migration policy in [0006-decision-wayfinder-ticket-migration-policy.md](0006-decision-wayfinder-ticket-migration-policy.md) (**Answer** section) against [.scratch/rule-index/map.md](../../.scratch/rule-index/map.md) and `.scratch/rule-index/issues/`.

1. **Inventory** wayfinder issue files; drop **Q2** terminals (`wontfix`, out-of-scope) and **Q3** superseded-only tickets (map strike-through, explicit supersede chains).
2. **Group** remaining tickets by **pipeline stage** (parse, compile, structured env / IndexContext, validate / inventory / CLI, foundation / policy, docs / agent environment) and merge similar **correction-pass** work within each stage.
3. **Author** plan **0003** **Decisions so far** (~12–16 merged gists for closed foundation, grills, and finished stage work where the decision still binds today).
4. **Create** rubber-duck **`Type: task`** items under `.backlog/items/` (~6–9 total) for:
   - **Open frontier** wayfinder tickets (`claimed`, `ready-for-agent`, `needs-grilling`) — **one backlog task each**, not merged with closed work;
   - Merged **closed** stage buckets that still need explicit acceptance criteria for regression or documentation.
5. Each new or updated backlog item includes **problem**, **outcome**, **acceptance criteria**, and a **source list** (links to merged `.scratch/rule-index/issues/NN-*.md` files).
6. Leave plan **0003** **Spikes** table **empty** until [0007](../items/0007-decision-wayfinder-spike-migration-policy.md) resolves; link `.scratch/.../research/` from summaries when useful.
7. **Do not** move, rename, or delete `.scratch/` files; `.scratch/` remains archaeology and interim authority until a later cutover decision.

## Notes

- Open frontier (approximate, re-verify at execution): [167](../../.scratch/rule-index/issues/167-grill-index-identity-exception-env-splice.md) (claimed), [168](../../.scratch/rule-index/issues/168-task-index-identity-exception-residuals.md) (ready-for-agent), [125](../../.scratch/rule-index/issues/125-grill-asca-grouping-insertion.md), [126](../../.scratch/rule-index/issues/126-correction-pass-asca-grouping-insertion.md), [129](../../.scratch/rule-index/issues/129-grill-section-mappings-feature-matrices-yaml-compile.md), [170](../../.scratch/rule-index/issues/170-grill-composed-chain-path-inventory-policy.md) (needs-grilling) — adjust if status changed.
- Cap: **≤25** indexed rows on **0003** (**Decisions so far** bullets + **Tasks** table + **Spikes** table combined).
- Sync **0003** **Tasks** / **Decisions so far** / **features.md** (**0003** → `in-progress` when work starts).

## Out of Scope

- Migrating `.scratch/data-processing-pipeline/` or `.scratch/sound-change-sequences/` (plans **0004**, **0005**).
- Creating **`Type: spike`** backlog items (blocked on **0007**).
- Doc cutover (`AGENTS.md`, `CONTEXT.md`) and dual-write policy (still fog on **0001**).

## Acceptance Criteria

- [ ] Plan **0003** **Decisions so far** lists **12–16** bullets; each links to detail or merged backlog items and cites merged wayfinder issue numbers in the child item or gist text.
- [ ] **≤25** total indexed outcomes on **0003** (count **Decisions so far** lines + rows in **Tasks** + **Spikes**); **Spikes** remains empty.
- [ ] **6–9** new **`Type: task`** files exist under `.backlog/items/` with `Plan:` **0003**, each satisfying the merged-item content bar (problem, outcome, acceptance criteria, source list).
- [ ] Every open-frontier wayfinder ticket listed in **Notes** (or current equivalent after status scan) has its **own** **`Type: task`** on `.backlog/` unless terminal or superseded under **0006**.
- [ ] No `.backlog/` item corresponds to a **`wontfix`** / out-of-scope wayfinder ticket or a superseded-only ticket per **0006** Q2–Q3.
- [ ] Plan **0003** **Tasks** table lists all new task items with accurate **Overview** and **Status** (`ready` or `needs-detail` as appropriate).
- [ ] `.scratch/rule-index/` tree is unchanged aside from optional comment pointers agents may add later (no file moves/deletes in this task).

## Comments
