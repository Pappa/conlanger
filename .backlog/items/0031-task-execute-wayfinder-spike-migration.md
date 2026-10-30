Type: task
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Copy 13 curated spike findings to `.backlog/spikes/` and add resolved `Type: spike` items on plan 0003 per decision 0007.
Blocked by:

## Problem Statement

Living `docs/` and `src/` still reference spike findings under `legacy wayfinder rule-index research/`, while plan **0003**’s **Spikes** table is empty per the interim **0006** policy. [0007](../items/0007-decision-wayfinder-spike-migration-policy.md) defines which spikes migrate and how; implementers need executable backlog items and canonical findings paths under `.backlog/spikes/`.

## Description

Execute the **Answer** in [0007-decision-wayfinder-spike-migration-policy.md](../items/0007-decision-wayfinder-spike-migration-policy.md):

1. Allocate **13** new shared **`NNNN`** values for **`Type: spike`** items and matching `.backlog/spikes/<NNNN>-<slug>.md` files.
2. **Copy** the 13 source markdown files from `legacy wayfinder rule-index research/`; strip artefact-dependent sections and links (CSVs, scripts, probe dirs) in the copies only.
3. Create **10** spike items converted from wayfinder spike issues and **3** retroactive spike items (positional slots, subscript notation, ejective notation) with best-effort summaries and **source lists**.
4. Set each spike item **`Status: resolved`** and populate plan **0003** **Spikes** table.
5. Update links in `docs/` and `src/` that currently target `legacy wayfinder rule-index research/` for migrated files so they target `.backlog/spikes/…`.
6. Do **not** modify links inside the legacy wayfinder tree.

## Acceptance Criteria

- [x] Thirteen files exist under `.backlog/spikes/` matching the curated list in **0007** (filenames use backlog `NNNN` slugs).
- [x] Thirteen **`Type: spike`** items exist under `.backlog/items/`, each with **`Plan:`** **0003**, **`Result:`** link, and **`Status: resolved`**.
- [x] Copied findings contain no references that require unmigrated artefacts (probe paths, `scan_*.py`, CSV appendices) unless rewritten as prose-only.
- [x] `docs/system/index-diachronica-parser.md`, `docs/system/sound-change-applier.md`, `docs/system/validate.md`, and `src/conlanger/compile/tools/asca/clicks.py` link to `.backlog/spikes/` for the migrated topics they currently cite from `legacy wayfinder`.
- [x] Plan **0003** **Spikes** table lists all thirteen items with synced **Overview** and **Status**.
- [x] the legacy wayfinder tree content is unchanged except as incidental to read-only copy source.

## Notes

- Execution may assign spike item numbers after **0031**; keep **Result:** paths and table rows consistent.
- Spike rows do not count toward the **≤25** decisions + tasks cap on **0003** (**0007**).
