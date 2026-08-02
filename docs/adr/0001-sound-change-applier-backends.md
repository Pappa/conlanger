# ASCA first, multi-applier capable

Conlanger will treat ASCA (`asca-rust`) as the default sound-change applier for execution code and tests, because that is where near-term work will land. At the same time, the package must keep a clear boundary so Brassica (or another sound-change applier) can be used later without rewriting the Index Diachronica ingestion pipeline from scratch.

## Considered Options

- **ASCA-only forever** — faster short term; locks the whole stack to one syntax and CLI.
- **Applier-neutral from day one with no ASCA bias** — cleaner long term; slows the ASCA execution/test work that is needed now.
- **ASCA-first with an explicit multi-applier boundary** — chosen: ship ASCA hard, keep the door open for Brassica.

## Consequences

- Prefer interfaces and corpus shapes that can compile or adapt to more than one applier.
- Do not scatter raw ASCA CLI calls through unrelated modules without a single applier boundary.
- Brassica support may stay “in principle” until a later ADR adopts it for real.
