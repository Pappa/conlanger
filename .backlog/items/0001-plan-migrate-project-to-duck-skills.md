Type: epic-duck:plan
Status: resolved

## Destination

The project uses **duck-skills** (`epic-duck`, `rubber-duck`, and related skills) and **`.backlog/`** as the sole operational tracker for planning and implementation on features **0003**, **0004**, and **0005**. Legacy wayfinder material is retired from the working tree (see git history).

## Notes

- **Tracker:** [`.backlog/`](../../.backlog/) — conventions in [backlog.md](../../docs/agents/backlog.md).
- **Cutover:** completed via [0045](0045-decision-duck-skills-cutover-agent-docs-and-scratch.md) → [0046](0046-task-align-agent-docs-post-cutover.md) → [0047](0047-task-remove-scratch-links-from-living-tree.md) → [0048](0048-task-delete-scratch-directory.md).
- **Skills:** `epic-duck` for feature plans; `amigo-duck` before publishing children; `question-duck` when scope is still foggy.

## Decisions so far

- [Seed minimal epic-duck features for the three wayfinder efforts](0002-task-seed-wayfinder-epic-duck-features.md): three `epic-duck:plan` rows in `features.md` (cleaned rule index, data processing pipeline, sound-change generative model) with destinations only—no copy of the legacy rule-index map issue rows.
- [Wayfinder ticket migration policy](0006-decision-wayfinder-ticket-migration-policy.md): merge by **pipeline stage**; exclude `wontfix`/out-of-scope and superseded tickets from `.backlog/`; cap rule-index migration at **≤25** outcomes on **0003** (decisions + tasks); spikes deferred to [0007](0007-decision-wayfinder-spike-migration-policy.md).
- [Wayfinder spike migration policy](0007-decision-wayfinder-spike-migration-policy.md): **13** curated findings → `.backlog/spike/`; **`Type: spike`** on **0003** counted **separately** from the ≤25 cap; execution [0031](0031-task-execute-wayfinder-spike-migration.md).
- [Duck-skills cutover and legacy tree retirement](0045-decision-duck-skills-cutover-agent-docs-and-scratch.md): **`.backlog/` only** for new work; legacy wayfinder tree deleted; agent docs per `setup-duck-skills`.

## Not yet specified

- _(empty.)_

## Out of scope

- _(empty.)_

## Decisions

| Decision | Overview | Status |
|----------|----------|--------|
| [0006-decision-wayfinder-ticket-migration-policy.md](0006-decision-wayfinder-ticket-migration-policy.md) | Merge by pipeline stage, exclude dead tickets, cap rule-index at ≤25 outcomes. | resolved |
| [0007-decision-wayfinder-spike-migration-policy.md](0007-decision-wayfinder-spike-migration-policy.md) | Curated 13 spike findings; copy md only; spikes cap separate from ≤25. | resolved |
| [0045-decision-duck-skills-cutover-agent-docs-and-scratch.md](0045-decision-duck-skills-cutover-agent-docs-and-scratch.md) | Cutover, agent docs, living links, and legacy tree retirement. | resolved |

## Tasks

| Task | Overview | Status |
|------|----------|--------|
| [0002-task-seed-wayfinder-epic-duck-features.md](0002-task-seed-wayfinder-epic-duck-features.md) | Add three minimal feature plans on `.backlog/` for the wayfinder-managed efforts. | resolved |
| [0008-task-execute-wayfinder-rule-index-migration.md](0008-task-execute-wayfinder-rule-index-migration.md) | First migration pass: merged **Decisions so far** and open tasks on **0003**. | resolved |
| [0031-task-execute-wayfinder-spike-migration.md](0031-task-execute-wayfinder-spike-migration.md) | Migrate 13 spike findings and items per **0007**. | resolved |
| [0046-task-align-agent-docs-post-cutover.md](0046-task-align-agent-docs-post-cutover.md) | Agent entrypaths per 0045; retire issue-tracker; delete implement-closure and doc-migration tests. | resolved |
| [0047-task-remove-scratch-links-from-living-tree.md](0047-task-remove-scratch-links-from-living-tree.md) | Strip legacy wayfinder path references from the living tree. | resolved |
| [0048-task-delete-scratch-directory.md](0048-task-delete-scratch-directory.md) | Remove legacy wayfinder directory after 0046 and 0047. | resolved |

## Spikes

| Spike | Overview | Status |
|-------|----------|--------|
| | | |
