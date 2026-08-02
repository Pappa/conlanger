Status: needs-triage
Type: task

# Automate PHOIBLE and WALS data preparation pipeline

## Question

Replace the temporary manual notebook data-preparation flow (`prepare_phoible_data.ipynb`, `prepare_wals_data.ipynb` and their `.npz` outputs) with a repeatable, non-manual data processing pipeline suitable for the generative conlang product arc (ADR-0007).

## Notes

- ADR-0007 explicitly excludes today’s notebook prep from architecture; this ticket is the follow-up to bring that work into a real pipeline.
- Today: one dialect phoneme inventory per language from PHOIBLE → array/dataset; WALS morphology/grammar parameters prepared similarly.
- Out of scope for this ticket: redesigning the GAN architectures themselves.

## Comments

> *Captured during grill-with-docs from `docs/README.md` (Data Preparation section).*
