# Implement closure checklist

Use this when finishing work on a `.scratch/<feature>/issues/*.md` ticket (including `/implement`).

## Ticket file

1. Set `Status: resolved` near the top — never `done` on wayfinder children ([triage-labels.md](./triage-labels.md)).
2. For decision tickets (`grilling`, resolved spikes with a binding answer), record the outcome under `## Answer`.
3. Append discussion under `## Comments` when useful.

## Wayfinder map

When the ticket is indexed on `.scratch/<effort>/map.md` (Notes or Decisions-so-far):

1. Strike through resolved ticket links using the existing map style (`~~[title](path)~~`).
2. Add a one-line pointer to the resolution (date, gist, link to PR or doc) if the map pattern calls for it.
3. Do not duplicate long policy in map **Notes** — link to `docs/` or the ticket body instead.

## Repo hygiene

1. Run `uv run check` on a clean tree before push.
2. Install hooks once per clone: `uv run pre-commit install` ([DEV.md](../DEV.md)).

No automated `check_scratch_sync` script — this checklist is the source of truth for map/ticket alignment.
