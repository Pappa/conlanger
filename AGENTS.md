## Agent skills

### Backlog

Planning and implementation items live under **`.backlog/`**. See `docs/agents/backlog.md`.

### Ticket status

**`.backlog/`** items use duck **`Status:`** strings (`needs-triage` through `out-of-scope`).

See `docs/agents/ticket-statuses.md`.

### Domain docs

Single-context: **`GLOSSARY.md`** (vocabulary) + **`CONTEXT.md`** (overview and doc map) + `docs/SYSTEM.md` + `docs/adr/`. See `docs/agents/domain.md`.

### Rule index (cleaned Index Diachronica)

When working on parse, compile, validate, or correction passes:

1. [GLOSSARY.md](GLOSSARY.md)
2. [docs/SYSTEM.md](docs/SYSTEM.md) — parse → compile → validate table
3. [docs/adr/0013-parse-compile-validate.md](docs/adr/0013-parse-compile-validate.md) — stage boundaries
4. Feature plan [.backlog/items/0003-plan-cleaned-rule-index.md](.backlog/items/0003-plan-cleaned-rule-index.md) — open decisions and tasks

Package layout: `ingest` (parse), `compile` (applier compile), `utils` (shared) — [index-diachronica-parser.md](docs/system/index-diachronica-parser.md) § Package imports.

**Spikes:** backlog **`Type: spike`** items; findings under `.backlog/spikes/`. Resolve with **`/spike-duck`**.

Local dev (gate, pytest, ruff, ASCA fork): [docs/DEV.md](docs/DEV.md). Review standards: [docs/agents/coding-standards.md](docs/agents/coding-standards.md).
