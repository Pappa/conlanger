# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

## Wayfinder / workflow statuses

Wayfinder tickets (`.scratch/<effort>/issues/`) also use workflow statuses on the `Status:` line. These are **not** triage roles, but `/triage` should recognize them:

| Status in our tracker | Triage equivalent   | Meaning                                                                 |
| --------------------- | ------------------- | ----------------------------------------------------------------------- |
| `needs-grilling`      | `ready-for-human`   | Grill session needed before the ticket is ready for an agent or merge   |
| `claimed`             | *(in progress)*     | Owner is actively working the ticket                                    |
| `resolved`            | *(closed)*          | Done; answer recorded under `## Answer`                                 |
| `partially resolved`  | `needs-grilling`    | Legacy — prefer `needs-grilling` when deferred grill work remains       |

Matt Pocock skills and wayfinder often file grilling tickets as `needs-grilling`. Keep that string on the ticket; triage maps it to **`ready-for-human`**.

Edit the right-hand column to match whatever vocabulary you actually use.
