## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Wayfinder ticket types

In this repo, the wayfinder ticket type **`spike`** is the local name for upstream mattpocock/skills **`research`**. Write `Type: spike` on tickets; when wayfinder (or related skills) say `research`, treat that as `spike`. Spikes are still resolved with the **`/research`** skill — do not invent a `/spike` skill, and do not rename paths like `.scratch/.../research/` (those are findings directories, not ticket types).
