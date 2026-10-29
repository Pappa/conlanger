## Agent skills

### Backlog

Duck-skills planning and implementation items live under **`.backlog/`**. Rule-index and wayfinder work stays in **`.scratch/`** (unchanged). See `docs/agents/backlog.md`.

### Ticket status

**`.backlog/`** items use duck **`Status:`** strings (`needs-triage` through `out-of-scope`). Wayfinder **`.scratch/`** tickets and Matt Pocock triage roles are documented separately. See `docs/agents/ticket-statuses.md` and `docs/agents/triage-labels.md`.

### Issue tracker (`.scratch/` / wayfinder)

Issues for rule-index and wayfinder live as markdown under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`. When closing a ticket, follow [docs/agents/implement-closure.md](docs/agents/implement-closure.md).

### Domain docs

Single-context: **`GLOSSARY.md`** (vocabulary) + **`CONTEXT.md`** (overview and doc map) + `docs/SYSTEM.md` + `docs/adr/`. See `docs/agents/domain.md`.

### Rule index (cleaned Index Diachronica)

When working on parse, compile, validate, or correction passes:

1. [GLOSSARY.md](GLOSSARY.md)
2. [docs/SYSTEM.md](docs/SYSTEM.md) — parse → compile → validate table
3. [docs/adr/0013-parse-compile-validate.md](docs/adr/0013-parse-compile-validate.md) — stage boundaries
4. [.scratch/rule-index/map.md](.scratch/rule-index/map.md) + linked `issues/` tickets — effort decisions and open work

The wayfinder map indexes **closed decisions**; zoom the linked ticket for detail. Do not treat map **Notes** as glossary or as the only spec. Package layout: `ingest` (parse), `compile` (applier compile), `utils` (shared) — [index-diachronica-parser.md](docs/system/index-diachronica-parser.md) § Package imports.

Local dev (gate, pytest, ruff, ASCA fork): [docs/DEV.md](docs/DEV.md). Review standards: [docs/agents/coding-standards.md](docs/agents/coding-standards.md).

### Wayfinder ticket types

In this repo, the wayfinder ticket type **`spike`** is the local name for upstream mattpocock/skills **`research`**. Write `Type: spike` on tickets; when wayfinder (or related skills) say `research`, treat that as `spike`. Spikes are still resolved with the **`/research`** skill — do not invent a `/spike` skill, and do not rename paths like `.scratch/.../research/` (those are findings directories, not ticket types).
