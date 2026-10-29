Type: epic-duck:plan
Status: in-progress

## Destination

A **cleaned rule index** (applier-neutral YAML source of truth) derived from **Index Diachronica HTML**, where **index rules** **compile** to valid ASCA — with **historical fidelity** and a scalable correction workflow.

## Notes

- **Wayfinder source (authoritative until migrated):** [.scratch/rule-index/map.md](../../.scratch/rule-index/map.md) and `issues/` ([issue-tracker.md](../../docs/agents/issue-tracker.md)).
- **Agent entry:** [GLOSSARY.md](../../GLOSSARY.md), [docs/SYSTEM.md](../../docs/SYSTEM.md), ADRs under `docs/adr/` (especially parse → compile → validate).
- Do not treat map **Notes** as glossary; zoom linked tickets for detail.
- **Migration policy (plan 0001):** [0006](../items/0006-decision-wayfinder-ticket-migration-policy.md) — merge wayfinder issues by **parse / compile / validate / tooling** stage; **≤25** total **Decisions so far** + **Tasks** + **Spikes** rows; **~12–16** decision gists + **~6–9** rubber-duck **`Type: task`**; no **`Type: spike`** until [0007](../items/0007-decision-wayfinder-spike-migration-policy.md). Exclude `wontfix`/out-of-scope and superseded tickets from `.backlog/`; archaeology stays in `.scratch/`.

## Decisions so far

## Not yet specified

- Cutover policy for `.scratch/rule-index/` vs `.backlog/` for **new** tickets after migration.

## Out of scope

- Generative conlang modeling and PHOIBLE/WALS pipelines (separate feature plans **0004** and **0005**).

## Decisions

| Decision | Overview | Status |
|----------|----------|--------|
| | | |

## Tasks

| Task | Overview | Status |
|------|----------|--------|
| [0008-task-execute-wayfinder-rule-index-migration.md](0008-task-execute-wayfinder-rule-index-migration.md) | Populate **0003** from `.scratch/rule-index/` per decision **0006**. | ready |

## Spikes

| Spike | Overview | Status |
|-------|----------|--------|
| | | |
