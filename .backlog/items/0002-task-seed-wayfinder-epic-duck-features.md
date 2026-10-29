Type: epic-duck:task
Status: resolved
Plan: [0001-plan-migrate-project-to-duck-skills.md](0001-plan-migrate-project-to-duck-skills.md)
Overview: Add three minimal epic-duck feature plans that correspond to wayfinder-managed efforts, without importing their issue lists.
Blocked by:

## Problem Statement

Planning is split between **wayfinder** (`.scratch/`, map-led rule index) and **duck-skills** (`.backlog/`). Agents need a single duck-skills index for the three long-running product efforts without prematurely copying hundreds of wayfinder tickets or breaking mixed Matt Pocock / duck-skills conventions.

## Description

Create **minimal** `epic-duck:plan` features on `.backlog/features.md` that mirror these wayfinder efforts:

1. **Cleaned rule index** — wayfinder map [.scratch/rule-index/map.md](../../.scratch/rule-index/map.md) (only this effort has a map).
2. **Data processing pipeline** — seed issue [.scratch/data-processing-pipeline/issues/01-automate-phoible-wals-prep.md](../../.scratch/data-processing-pipeline/issues/01-automate-phoible-wals-prep.md).
3. **Sound-change generative model** — seed issue [.scratch/sound-change-sequences/issues/01-generative-sound-change-sequences.md](../../.scratch/sound-change-sequences/issues/01-generative-sound-change-sequences.md).

Each new plan gets a **Destination** aligned with the wayfinder destination or seed question, **Notes** that link the `.scratch/` path and remind readers that wayfinder tickets stay authoritative until migrated, and empty **Decisions** / **Tasks** / **Spikes** tables (no children yet). Do **not** copy individual items from the rule-index map or other `.scratch` issue directories.

This task lives under plan **0001 Migrate project to duck-skills**, which records the migration context and follow-on fog in its **Not yet specified** section.

## Acceptance Criteria

- [x] `.backlog/features.md` lists plan **0001** plus three new plans (**0003**, **0004**, **0005**) with one-sentence overviews and workflow **Status** values.
- [x] Each of **0003**, **0004**, and **0005** is a valid `epic-duck:plan` file under `.backlog/items/` with **Destination**, **Notes**, **Decisions so far**, **Not yet specified**, **Out of scope**, and empty child tables.
- [x] **0003** notes point to `.scratch/rule-index/map.md` and state that map issues are not duplicated on the backlog yet.
- [x] **0004** and **0005** notes point to their `.scratch/<feature>/` directories and seed issue files.
- [x] Plan **0001** links this task in its **Tasks** table and records the outcome under **Decisions so far** when done.
- [x] No files under `.scratch/` are moved, renamed, or deleted as part of this task.

## Answer

Created plans **0003** (cleaned rule index), **0004** (data processing pipeline), and **0005** (sound-change generative model) with minimal bodies and updated **0001** / `features.md` accordingly. Wayfinder artifacts under `.scratch/` are unchanged.

## Comments
