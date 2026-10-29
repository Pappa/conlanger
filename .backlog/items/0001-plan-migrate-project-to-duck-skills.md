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
- [Wayfinder ticket migration policy](0006-decision-wayfinder-ticket-migration-policy.md): merge by **pipeline stage**; exclude `wontfix`/out-of-scope and superseded tickets from `.backlog/`; cap rule-index migration at **≤25** outcomes on **0003** (decisions + tasks); spikes deferred to [0007](0007-decision-wayfinder-spike-migration-policy.md).
- [Wayfinder spike migration policy](0007-decision-wayfinder-spike-migration-policy.md): **13** curated findings → `.backlog/spike/`; **`Type: spike`** on **0003** counted **separately** from the ≤25 cap; execution [0031](0031-task-execute-wayfinder-spike-migration.md).
- [Duck-skills cutover and `.scratch/` retirement](0045-decision-duck-skills-cutover-agent-docs-and-scratch.md): **`.backlog/` only** for new work; delete `.scratch/` last; no living `.scratch/` links; agent docs per `setup-duck-skills`; execute [0046](0046-task-align-agent-docs-post-cutover.md) → [0047](0047-task-remove-scratch-links-from-living-tree.md) → [0048](0048-task-delete-scratch-directory.md).

## Not yet specified

- _(empty — cutover policy decided in **0045**; execution on tasks **0046–0048**.)_

## Out of scope

- 1:1 import of all wayfinder issues from [.scratch/rule-index/map.md](../../.scratch/rule-index/map.md) (use merged summaries per **0006** on plan **0003** instead).

## Decisions

| Decision | Overview | Status |
|----------|----------|--------|
| [0006-decision-wayfinder-ticket-migration-policy.md](0006-decision-wayfinder-ticket-migration-policy.md) | Merge by pipeline stage, exclude dead tickets, cap rule-index at ≤25 outcomes. | resolved |
| [0007-decision-wayfinder-spike-migration-policy.md](0007-decision-wayfinder-spike-migration-policy.md) | Curated 13 spike findings; copy md only; spikes cap separate from ≤25. | resolved |
| [0045-decision-duck-skills-cutover-agent-docs-and-scratch.md](0045-decision-duck-skills-cutover-agent-docs-and-scratch.md) | Cutover, agent docs, living links, and fate of `.scratch/` before 0001 closes. | resolved |

## Tasks

| Task | Overview | Status |
|------|----------|--------|
| [0002-task-seed-wayfinder-epic-duck-features.md](0002-task-seed-wayfinder-epic-duck-features.md) | Add three minimal feature plans on `.backlog/` for the wayfinder-managed efforts. | resolved |
| [0008-task-execute-wayfinder-rule-index-migration.md](0008-task-execute-wayfinder-rule-index-migration.md) | First migration pass: merged **Decisions so far** and open tasks on **0003**. | resolved |
| [0031-task-execute-wayfinder-spike-migration.md](0031-task-execute-wayfinder-spike-migration.md) | Migrate 13 spike findings and items per **0007**. | resolved |
| [0046-task-align-agent-docs-post-cutover.md](0046-task-align-agent-docs-post-cutover.md) | Agent entrypaths per 0045; retire issue-tracker; delete implement-closure and doc-migration tests. | needs-detail |
| [0047-task-remove-scratch-links-from-living-tree.md](0047-task-remove-scratch-links-from-living-tree.md) | Strip or retarget all `.scratch/` paths in living tree. | needs-detail |
| [0048-task-delete-scratch-directory.md](0048-task-delete-scratch-directory.md) | Remove `.scratch/` after 0046 and 0047. | needs-detail |

## Spikes

| Spike | Overview | Status |
|-------|----------|--------|
| | | |
