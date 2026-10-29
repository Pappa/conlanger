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
