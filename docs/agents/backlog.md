# Issue tracker: Local markdown (`.backlog/`)

Plans, decisions, tasks, and spikes for **duck-skills** (`epic-duck`, `rubber-duck`, `spike-duck`, etc.) live under `.backlog/`.

## Conventions

### Index

- **Plan list**: `.backlog/features.md` — markdown table with columns **Plan**, **Overview**, **Status**.
  - **Plan**: link to the feature file, e.g. `[0003-plan-auth.md](items/0003-plan-auth.md)`.
  - **Overview**: one sentence (same as **Destination** on the feature file).
  - **Status**: workflow value from `docs/agents/ticket-statuses.md`.

### Shared numbering

All backlog items share one counter under `.backlog/items/`. Next number = one greater than the highest existing `NNNN` prefix (four digits, from `0001`). Deleted numbers are never reused.

| Kind | Path | `Type:` | Publisher |
|------|------|---------|-----------|
| Plan | `.backlog/items/<NNNN>-plan-<feature-slug>.md` | `epic-duck:plan` | epic-duck |
| Decision | `.backlog/items/<NNNN>-decision-<slug>.md` | `epic-duck:decision` | epic-duck |
| Planning task | `.backlog/items/<NNNN>-task-<slug>.md` | `epic-duck:task` | epic-duck |
| Planning spike (item) | `.backlog/items/<NNNN>-spike-<slug>.md` | `epic-duck:spike` | epic-duck |
| Implementation task | `.backlog/items/<NNNN>-task-<slug>.md` | `task` | rubber-duck |
| Implementation spike (item) | `.backlog/items/<NNNN>-spike-<slug>.md` | `spike` | rubber-duck |
| Spike (findings) | `.backlog/spikes/<NNNN>-<slug>.md` | (none) | spike-duck |

**Planning** items (`epic-duck:*`) support feature charting and refinement. **Implementation** items (`task`, `spike`) are for development work from **rubber-duck** sessions. Same **NNNN** counter for all rows.

### Common header

**`Type:` is always the first line.** Then `Status:`, then other fields in the order below. Omit `Blocked by:` when empty.

### Status

`needs-triage` · `needs-detail` · `ready` · `in-progress` · `resolved` · `wontfix` · `out-of-scope`

- **Canonical**: `Status:` on each item file. Update `features.md` and the feature’s **Decisions** / **Tasks** / **Spikes** tables in the same edit.
- **Plan**: starts `needs-detail`; becomes `in-progress` when the first child is created; `resolved` / `out-of-scope` only by explicit choice (see epic duck).
- **Child**: set `in-progress` when a session starts; `ready` when requirements are complete enough to pick up; `resolved` when done (spike item when the result file exists).

Full meanings: [ticket-statuses.md](./ticket-statuses.md).

### Plan file body

Metadata:

```markdown
Type: epic-duck:plan
Status: needs-detail
```

Section order:

1. **Destination**
2. **Notes**
3. **Decisions so far**
4. **Not yet specified**
5. **Out of scope**
6. **Decisions** — table: **Decision**, **Overview**, **Status**
7. **Tasks** — table: **Task**, **Overview**, **Status**
8. **Spikes** — table: **Spike**, **Overview**, **Status**

Plan, decision, task, and spike item files all live in `.backlog/items/`. Link children from the feature file with same-directory paths, e.g. `[0004-decision-login-flow.md](0004-decision-login-flow.md)`. Link spike results with `[0006-oauth.md](../spikes/0006-oauth.md)`.

### Decision, task, and spike shapes

See the **setup-duck-skills** seed (`backlog-local.md`) for full templates: decision and planning-task **Question** bodies; deliverable tasks with **Problem Statement**, **Description**, and **Acceptance Criteria** after **amigo-duck**; implementation `Type: task` / `Type: spike` with optional `Plan: (unanchored)`; spike findings under `.backlog/spikes/`.

### Blocking

- `Blocked by: 0004, 0006` — comma-separated shared item numbers (plan, decision, task, or spike).
- **Frontier** (per feature): lowest `NNNN` among that feature’s children with `needs-triage` or `needs-detail`, empty `Blocked by`, and not terminal (`resolved`, `wontfix`, `out-of-scope`).
- **Session pool** (per feature): unblocked children with **`Status: ready`** — preferred targets when working through the plan.
- **`in-progress`**: treat as likely owned by an active session (possibly another agent). **Confirm with the user** before modifying an `in-progress` child — **even if they named it** (wrong-ticket guard).
- **Choosing a child**: epic-duck does not auto-pick; offer up to **five** lowest `NNNN` from the **`ready`** pool (then `in-progress`, then frontier) and ask the user to select; if more match, state the count hidden and offer the full list.
- When any item becomes `resolved`, `wontfix`, or `out-of-scope`, remove its `NNNN` from every `Blocked by:` line in `.backlog/items/` (trim commas; delete the line if empty).

### Thread

Append discussion under `## Comments` on decisions, tasks, and spikes.

## Closing a backlog item

When finishing **`Type: task`**, **`Type: spike`**, or resolving a child under a feature plan:

1. Set **`Status: resolved`** on the item file (decisions: record **`## Answer`** when applicable).
2. Update the parent plan **Decisions** / **Tasks** / **Spikes** table and **`features.md`** when the plan’s status changes.
3. Run **`uv run check`** on a clean tree before push ([DEV.md](../DEV.md)).

## When a skill says "publish to the backlog"

Apply **amigo-duck** to the draft (planning **`Type: epic-duck:*`** or implementation **`Type: task`** / **`Type: spike`**), then create the item file(s) under `.backlog/items/` and update the parent feature’s **Decisions** / **Tasks** / **Spikes** tables when **`Plan:`** links to a feature (and `features.md` when **epic-duck** adds a feature).

## When a skill says "fetch the relevant ticket"

Read the path or file the user gave.

## Epic-duck operations

Used by **epic-duck**. A **feature plan** is the planning artifact; **decisions**, **tasks**, and **spike items** are children.

- **Plan file**: `.backlog/items/<NNNN>-plan-<slug>.md` with `Type: epic-duck:plan`.
- **Child decision**: `Type: epic-duck:decision`, `Plan:` backlink, `Status:`.
- **Child task**: `Type: epic-duck:task`, `Plan:` backlink, `Status:`.
- **Child spike**: `Type: epic-duck:spike`, result under `.backlog/spikes/`.
- **Resolve decision**: `## Answer`, `Status: resolved`, one bullet under feature **Decisions so far**, blocker sweep, refresh tables.
- **Resolve spike**: result file written, spike item `Status: resolved`, update **Spikes** table and **Decisions so far** when appropriate.
- **Unanchored implementation items**: `Plan: (unanchored)` + `needs-triage` until **epic-duck** sets a feature plan link.

### Starting a session (local)

1. Resolve which feature to open (user input: path, `NNNN`, slug, or close name match — confirm with user; or list `needs-detail` / `in-progress` from `features.md`; or chart a new feature).
2. **Git check** (once, before writes): if the feature file differs from `HEAD` (untracked file = plan-level change):
   - Hunks only under **Decisions** / **Tasks** / **Spikes** → warn that index tables changed; ask to continue.
   - Any change to plan sections (metadata, Destination, Notes, Decisions so far, fog, out of scope, or above **Decisions**) → list impact; ask how to proceed. Decline or wait → no writes.
3. Pick child (see epic-duck skill): user-named item (confirm if `in-progress`); else user selects from listed **`ready`** / **`in-progress`** / frontier candidates (up to five shown, overflow counted).

### Plan completion

When every child is terminal (`resolved`, `wontfix`, or `out-of-scope`) and **Not yet specified** is empty, ask whether the feature is `resolved`, `out-of-scope`, or still `in-progress` with more work.
