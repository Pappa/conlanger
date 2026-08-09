# Corpus rules store a `stages` list, not `input`/`output`

The cleaned rule corpus represents each Index Diachronica rule line as one corpus rule whose change spine is an ordered **`stages`** list of opaque Index-shaped strings (length 2 = single step; length ≥ 3 = chain; `stages: []` + `status: skipped` = hold-out). YAML no longer carries `input`/`output`. Parse isolates at most one `env` and one `exception` on the rule, then splits the spine on every `→`. Compile still expands only at compile time into adjacent ASCA pairs, stamping that same rule-level `env`/`exception` on each emitted step. This supersedes storing chains as `" > "` inside a string `output` and the earlier rejection of a structured spine in favour of opaque `input`/`output` strings (ADR-0005 amendment / no-ingest-split ticket 01), while keeping one corpus rule per HTML line.

## Considered Options

- **Opaque `input`/`output` strings with chain in `output` (previous)** — works, but hides chain structure and forced first-vs-last arrow split games.
- **Union `input: str | list[str]`** — dual meaning for `input`; every consumer branches on type.
- **Uniform `stages` for all rules (chosen)** — one shape; length encodes single-step vs chain; compile expands adjacent pairs.

## Consequences

- One-shot schema cutover: parse, compile, inventory, and docs must move together; no dual-read of legacy `input`/`output`.
- Ticket 03 schema answer and ADR-0005 “opaque strings only / no steps array” guidance need syncing to this ADR.
- Field-isolation and any tooling that blames `input`/`output` must blame **stage index** (or derived pair ends) instead.
