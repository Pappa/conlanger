# Validate sound-change rules after applier compile

Automated validity checks run **after** an applier compiler turns the YAML rule index into a concrete backend (ASCA first; Brassica later). The HTML→YAML ingestion path may emit incomplete or still-mapped forms; failing ASCA syntax at parse time is not the gate.

## Considered Options

- **Post-compile validation (chosen)** — keeps the index applier-neutral; matches ADR-0001/0002.
- **Reject at HTML→YAML if not ASCA-valid** — faster ASCA loop; couples ingestion to ASCA.
- **Human review only** — too weak for the planned ASCA execution/test surface.

## Consequences

- ASCA CLI / library checks belong in the ASCA compiler and its tests, not as a hard requirement of every YAML field at ingest time.
- Metrics like `asca_errors.csv` from the transcript era are compiler/test feedback, not proof that the YAML schema is wrong.
- Brassica gains the same pattern later: compile, then validate with Brassica’s own checker.
