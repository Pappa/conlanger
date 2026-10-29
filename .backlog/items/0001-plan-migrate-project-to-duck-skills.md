Type: epic-duck:plan
Status: in-progress

## Destination

The project uses **duck-skills** (`epic-duck`, `rubber-duck`, and related skills) and the **`.backlog/`** tracker for planning and implementation, while **wayfinder** and **`.scratch/`** remain the source of truth for in-flight work until each effort is migrated deliberately.

## Notes

- **Two trackers today:** duck-skills items live under [`.backlog/`](../../.backlog/) ([backlog.md](../../docs/agents/backlog.md)); rule-index and legacy wayfinder work stay under [`.scratch/`](../../.scratch/) ([issue-tracker.md](../../docs/agents/issue-tracker.md)). Do not move or merge `.scratch/` trees unless a decision ticket says so.
- **Mixed conventions:** agent docs, triage labels, and skills still reference Matt Pocock **wayfinder** (`wayfinder:map`, `claimed`/`resolved`, map-led rule index). Take extra care when editing backlog files, docs, and `.scratch/` together.
- **Wayfinder analogue:** read the **wayfinder** skill (`/wayfinder`) and **Wayfinding operations** in [issue-tracker.md](../../docs/agents/issue-tracker.md) before migrating an effort.
- **Skills:** `epic-duck` for feature plans; `amigo-duck` before publishing children; `question-duck` when scope is still foggy.

## Decisions so far

- [Seed minimal epic-duck features for the three wayfinder efforts](0002-task-seed-wayfinder-epic-duck-features.md): three `epic-duck:plan` rows in `features.md` (cleaned rule index, data processing pipeline, sound-change generative model) with destinations only—no copy of `.scratch/rule-index/map.md` issue rows.
- [Wayfinder ticket migration policy](0006-decision-wayfinder-ticket-migration-policy.md): merge by **pipeline stage**; exclude `wontfix`/out-of-scope and superseded tickets from `.backlog/`; cap rule-index migration at **≤25** outcomes on **0003**; spikes deferred to [0007](0007-decision-wayfinder-spike-migration-policy.md).

## Not yet specified

- Per-effort policy: dual-write vs cutover from `.scratch/` to `.backlog/` children.
- Doc updates (`AGENTS.md`, `CONTEXT.md`, agent entrypaths) once migration execution starts on **0003**.
- Spike copy rules ([0007](0007-decision-wayfinder-spike-migration-policy.md)).

## Out of scope

- 1:1 import of all wayfinder issues from [.scratch/rule-index/map.md](../../.scratch/rule-index/map.md) (use merged summaries per **0006** on plan **0003** instead).

## Decisions

| Decision | Overview | Status |
|----------|----------|--------|
| [0006-decision-wayfinder-ticket-migration-policy.md](0006-decision-wayfinder-ticket-migration-policy.md) | Merge by pipeline stage, exclude dead tickets, cap rule-index at ≤25 outcomes. | resolved |
| [0007-decision-wayfinder-spike-migration-policy.md](0007-decision-wayfinder-spike-migration-policy.md) | Which wayfinder spikes become `.backlog/` spike items and findings locations. | ready |

## Tasks

| Task | Overview | Status |
|------|----------|--------|
| [0002-task-seed-wayfinder-epic-duck-features.md](0002-task-seed-wayfinder-epic-duck-features.md) | Add three minimal feature plans on `.backlog/` for the wayfinder-managed efforts. | resolved |
| [0008-task-execute-wayfinder-rule-index-migration.md](0008-task-execute-wayfinder-rule-index-migration.md) | Rule-index wayfinder → **0003** backlog migration (see **0006**); owned on plan **0003**. | resolved |

## Spikes

| Spike | Overview | Status |
|-------|----------|--------|
| | | |
