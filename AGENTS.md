## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: **`GLOSSARY.md`** (vocabulary) + **`CONTEXT.md`** (overview and doc map) + `docs/SYSTEM.md` + `docs/adr/`. See `docs/agents/domain.md`.

### Rule index (cleaned Index Diachronica)

When working on parse, compile, validate, or correction passes:

1. [GLOSSARY.md](GLOSSARY.md)
2. [docs/SYSTEM.md](docs/SYSTEM.md) — parse → compile → validate table
3. [docs/adr/0013-parse-compile-validate.md](docs/adr/0013-parse-compile-validate.md) — stage boundaries
4. [.scratch/rule-index/spec.md](.scratch/rule-index/spec.md) — effort spec

The wayfinder [.scratch/rule-index/map.md](.scratch/rule-index/map.md) indexes **closed decisions**; zoom the linked ticket for detail. Do not treat map **Notes** as glossary or as the only spec.

Local dev (pytest, ruff, ASCA fork): [docs/DEV.md](docs/DEV.md).

### Wayfinder ticket types

In this repo, the wayfinder ticket type **`spike`** is the local name for upstream mattpocock/skills **`research`**. Write `Type: spike` on tickets; when wayfinder (or related skills) say `research`, treat that as `spike`. Spikes are still resolved with the **`/research`** skill — do not invent a `/spike` skill, and do not rename paths like `.scratch/.../research/` (those are findings directories, not ticket types).
