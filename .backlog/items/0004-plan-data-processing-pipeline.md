Type: epic-duck:plan
Status: needs-detail

## Destination

Replace the temporary manual notebook data-preparation flow for PHOIBLE and WALS with a **repeatable, non-manual data processing pipeline** suitable for the generative conlang product arc ([ADR-0007](../../docs/adr/0007-generative-conlang-pipeline.md)).

## Notes

- **Wayfinder seed (authoritative until migrated):** [.scratch/data-processing-pipeline/issues/01-automate-phoible-wals-prep.md](../../.scratch/data-processing-pipeline/issues/01-automate-phoible-wals-prep.md).
- Today: one dialect phoneme inventory per language from PHOIBLE; WALS morphology/grammar parameters prepared similarly (see [docs/CONLANGER.md](../../docs/CONLANGER.md)).
- ADR-0007 excludes today’s notebook prep from architecture; this effort brings that work into a real pipeline.
- No wayfinder map for this feature — only the seed issue under `.scratch/data-processing-pipeline/`.

## Decisions so far

## Not yet specified

- Pipeline shape, orchestration, and artifact locations under `data/`.
- Relationship to notebook outputs (`.npz`) during transition.

## Out of scope

- Redesigning GAN or other model architectures (see **0005** for generative sound-change work).

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
