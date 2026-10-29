Type: epic-duck:plan
Status: needs-detail

## Destination

Design and implement a model that proposes **plausible ordered sequences of sound-change rules** from the Index Diachronica–derived rule index — for example a GAN over sequences or a next-in-sequence model — for proto-root shaping and later historical evolution.

## Notes

- Documented as future work in [docs/CONLANGER.md](../../docs/CONLANGER.md); no ADR locks model family yet (GAN vs next-in-sequence remains open).
- Must consume the applier-neutral **rule index** ([ADR-0002](../../docs/adr/0002-applier-neutral-yaml-rule-index.md)) and emit **sound-change sequences** ([CONTEXT.md](../../CONTEXT.md)).
- Depends on a usable cleaned/structured index — track progress on plan **0003** (cleaned rule index).
- Curated attested sequences remain a supported path; this plan covers the generative path.

## Decisions so far

## Not yet specified

- Model family and training data strategy.
- When to chart implementation tasks on `.backlog/` vs continue wayfinder-style the legacy wayfinder tree tickets.

## Out of scope

- Building the cleaned rule index itself (plan **0003**).
- PHOIBLE/WALS ingestion pipeline (plan **0004**).

## Decisions

| Decision | Overview | Status |
|----------|----------|--------|
| | | |

## Tasks

| Task | Overview | Status |
|------|----------|--------|
| | | |

## Spikes

| Spike | Overview | Status |
|-------|----------|--------|
| | | |
