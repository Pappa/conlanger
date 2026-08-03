Status: needs-triage
Type: task

# Generative sound-change sequences (GAN or next-in-sequence)

## Question

Design and implement a model that proposes **plausible ordered sequences of sound-change rules** from the Index Diachronica–derived rule corpus — e.g. a GAN over sequences, or a next-in-sequence / sequence model — for proto-root shaping and later historical evolution.

## Notes

- Documented under **Future Work** in `docs/CONLANGER.md`; not locked as near-term architecture (no ADR yet).
- Must consume the applier-neutral **rule corpus** (ADR-0002) and emit **sound-change sequences** (see `CONTEXT.md`).
- Curated/selected attested sequences remain a supported path; this ticket is the generative path.
- Model family is intentionally open: GAN vs next-in-sequence to be chosen during the work.
- Depends on a usable cleaned/structured corpus (related wayfinder: cleaned YAML SoT).

## Comments

> *Captured during grill-with-docs from `docs/CONLANGER.md` (Sound change rules / Future Work).*
