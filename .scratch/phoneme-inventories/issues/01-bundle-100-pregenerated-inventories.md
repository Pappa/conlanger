Status: needs-triage
Type: task

# Bundle ~100 pre-generated phoneme inventories

## Question

Curate and ship approximately **100 pre-generated phoneme inventories** with the library so users can run lexicon / sound-change workflows without executing the inventory GAN (ADR-0008).

## Notes

- Source may be GAN outputs, filtered PHOIBLE-like samples, or a mix — decide during implementation.
- Inventories should use the project glossary term **Phoneme inventory** and sit behind the same API as generated ones where practical.
- Related: ADR-0007 (pipeline), ADR-0008 (GAN + presets), data-prep ticket under `.scratch/data-processing-pipeline/` if regeneration from upstream data is required.

## Comments

> *Captured during grill-with-docs from `docs/CONLANGER.md` (Language phoneme inventory generation).*
