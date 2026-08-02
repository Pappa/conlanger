# Generative conlang pipeline as product arc

Conlanger’s intended product arc is: generate a phoneme inventory, build a lexicon, apply sequences of sound changes to evolve the language over “history,” then produce downstream artifacts (translations, grammar document, sample audio). Grammar/morphology and phonotactics participate in that evolution where modelled.

**Out of this ADR:** the current PHOIBLE/WALS **Data Preparation** notebooks are a temporary manual process, not the architectural shape of ingest. Automating that work is tracked separately as an implementation ticket, not as pipeline architecture here.

Sound-change ingestion and appliers (ADRs 0001–0006) implement the evolution stage of this arc.

## Considered Options

- **Lock the full generative arc (chosen), excluding manual notebook prep as architecture** — keeps the README’s destination without elevating throwaway data wrangling.
- **Sound-change tooling only** — too narrow relative to the stated product.
- **README as brainstorm only** — no durable product claim for later agents.

## Consequences

- Specs and wayfinder maps should orient to inventory → lexicon → sound-change evolution → outputs.
- Do not treat `prepare_phoible_data.ipynb` / `prepare_wals_data.ipynb` as the long-term data platform.
- See `.scratch/data-processing-pipeline/issues/01-automate-phoible-wals-prep.md` for the follow-up build.
