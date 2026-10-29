# Ticket status vocabulary

Every **`.backlog/`** item (plans, decisions, tasks, spike items) uses one workflow field: **`Status:`**.

| Status | Meaning |
|--------|---------|
| `needs-triage` | Maintainer must evaluate or route; workflow state not yet decidable without human input. |
| `needs-detail` | Waiting on clarity (reporter, fog, incomplete requirements). |
| `ready` | Requirements complete and well-defined; OK for a human or AFK agent to **start** work on this item. |
| `in-progress` | A session is actively working this item. |
| `resolved` | Done; outcome recorded. |
| `wontfix` | Closed with **no action**. |
| `out-of-scope` | Consciously excluded from the plan destination. |

When a skill says **“set ready”**, set **`Status: ready`** after requirements pass **amigo-duck** where that gate applies.

Edit this table only when the duck workflow model changes (record rationale in `docs/adr/`).

## Matt Pocock triage roles (GitHub / generic skills)

Some upstream skills speak in triage **roles** rather than these `Status:` strings. Map roles using [triage-labels.md](./triage-labels.md) (`needs-info`, `ready-for-agent`, etc.). That file is for label vocabulary, not for `.backlog/` item workflow.

## Wayfinder (`.scratch/` only)

Wayfinder tickets under `.scratch/<effort>/issues/` use **`Status:`** on their own vocabulary. They are **not** required to use the duck table above. See [issue-tracker.md](./issue-tracker.md) and the wayfinder subsection in [triage-labels.md](./triage-labels.md).

| Status in `.scratch/` | Typical meaning |
| --------------------- | ---------------- |
| `needs-grilling` | Grill session needed before the ticket is ready for an agent or merge |
| `claimed` | Owner is actively working the ticket |
| `resolved` | Done; answer under `## Answer` |
| `partially resolved` | Legacy — prefer `needs-grilling` when deferred grill work remains |

When **epic-duck** and **wayfinder** both appear in one conversation, use the tracker named by the skill or path the user gave — do not assume statuses are interchangeable without mapping.
