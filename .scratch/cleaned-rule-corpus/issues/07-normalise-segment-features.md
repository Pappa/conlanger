Type: task
Blocked by: 01, 03

# Normalise segment feature matrices for appliers

## Question

How should Index Diachronica feature notation in corpus rule strings (e.g. `[+voiced]`, `[+sibilant]`) be normalised so ASCA and Brassica compilers accept them — which synonyms map to which canonical names, when normalisation runs (ingest vs compile), and what remains applier-neutral in the cleaned corpus?

## Notes

- Primary ASCA reference: [Segment Features](https://github.com/Girv98/asca-rust/blob/master/doc/doc.md#segment-features), [Using Distinctive Features](https://github.com/Girv98/asca-rust/blob/master/doc/doc.md#using-distinctive-features), [Feature Shorthands](https://github.com/Girv98/asca-rust/blob/master/doc/doc.md#feature-shorthands).
- Known HTML→ASCA mismatches already seen: `voiced`→`voice`, `sibilant`→`strident`; spacing/`[+ voice]` variants; colon attachment `C:[+voice]` vs `C[+voice]`.
- Related to but distinct from [Resolve abbreviations unsupported by ASCA and Brassica](06-resolve-applier-unsupported-abbreviations.md) (class/series tokens vs feature matrices).
- Skills: `/research` for ASCA/Brassica feature surfaces; grilling if neutral-vs-ASCA-shaped storage is the decision.
