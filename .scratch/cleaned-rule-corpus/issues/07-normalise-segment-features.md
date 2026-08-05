Type: grilling
Status: resolved
Blocked by: 01, 03

# Normalise segment feature matrices for appliers

## Question

How should Index Diachronica feature notation in corpus rule strings (e.g. `[+voiced]`, `[+sibilant]`) be normalised so ASCA and Brassica compilers accept them — which synonyms map to which canonical names, when normalisation runs (ingest vs compile), and what remains applier-neutral in the cleaned corpus?

## Notes

- ASCA reference: [Segment Features](https://github.com/Girv98/asca-rust/blob/master/doc/doc.md#segment-features), [Feature Shorthands](https://github.com/Girv98/asca-rust/blob/master/doc/doc.md#feature-shorthands).
- Distinct from [Resolve abbreviations unsupported by ASCA and Brassica](06-resolve-applier-unsupported-abbreviations.md) (**class letter** / **symbol** vs **feature matrix**).

## Answer

Domain term: **Feature matrix** — see `CONTEXT.md`.

- Synonym replacement at **HTML→YAML ingest** inside `[...]` only; target ASCA canonical names via `data/asca/feature_mappings.csv`; **`raw`** unchanged.
- Unmapped names: no invented mappings → **validation report** (ADR-0010).
- **`group_mappings.csv`** co-located under `src/conlanger/data/asca/`.
- **Whitespace tokenisation** — map fog, not this ticket.
- Compile ordering vs abbreviations — deferred to ticket 06.
- Optional **`mappings`** argument on compile path; format fixed at instantiation.
