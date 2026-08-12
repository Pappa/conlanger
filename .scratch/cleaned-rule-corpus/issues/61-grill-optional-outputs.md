Type: grilling
Status: needs-grilling

# Grill: optional outputs + seeded randomness (with sporadic)

## Question

Index rules like `d → {∅,ð} / V_V` encode speaker variation (including null). ASCA 0.10.2 rejects `∅` inside sets. How should the cleaned corpus and ASCA compile/render path retain alternatives and choose one for emission — and how should the **same seeded-randomness design** also cover **sporadic** rules (apply vs skip) — without making unit tests unable to exercise every branch?

## Settled so far (grill 2026-08-09, paused; scope widened 2026-08-12; resumed 2026-08-12)

- Glossary term: **Optional outputs** (distinct from **sporadic**) — `CONTEXT.md`.
- **Detection (Q1):** gate is **input is not a whole-field set** and **output is a whole-field set** (e.g. `d → {∅,ð}`). Do **not** treat paired `{a,b} → {c,d}` as optional outputs. Unequal paired-set arity / UnevenSet shapes (e.g. `{ʔθ,ʔr} → {ʔ,j,∅}`) are **unresolvable as written** — not this RNG path; separate failure/correction cluster. **Nested sets:** out of scope here — track in a separate issue.
- YAML SoT: **unchanged** — keep opaque set strings in **stages** (e.g. `'{∅,ð}'`); no new structured field.
- Ticket 60 parallel-column nulls remain out of scope for set-internal `∅`; this ticket is the follow-on for that cluster (~45 inventory rows with `{∅`).
- **Shared RNG (owner intent 2026-08-12):** one randomness + seeding story for **two** use cases — (1) optional outputs (pick which alternative), (2) sporadic rules (apply vs skip). Design both together; do not ship optional-output choice without a plan for sporadic.

## Open / blocked on rethink

- **When to choose** an alternative: earlier lean was `str(DiachronicSeries)`; then revised to `SoundChangeRule` instantiation via `random` + caller `random.seed`.
- **Testability concern (owner pause):** instantiation-time `random.choice` means unit tests will not systematically exercise every alternative unless tests inject choice or enumerate members explicitly.
- Whether `SoundChangeRule` keeps `outputs: tuple[str, …]` plus selected `output`, or only the chosen string.
- Fixed seed for inventory/regen vs free seed for generative apply.
- Sporadic sample/skip probability, default rate, and whether inventory validation forces “always apply” / “always skip” / enumerate.
- Round 1 still open: Q2 (explode vs resolve), Q3 (testability), Q4 (freeze vs re-roll).

## Facts (do not re-litigate)

- ASCA rejects `d > {∅,ð} / V_V`; `d > ∅ / V_V` and `d > ð / V_V` are valid.
- `SoundChangeRule` today freezes compiled `value` in `__init__`; ignores `sporadic`.
- No RNG on the sound-change render path today.
- Corpus: ~85 `{∅` lines in parsed YAML; canonical Spanish examples at `index_diachronica_original.html:8156–8157`.

## Next grilling round (when resumed)

1. Round 1 remainder: Q2 resolve-at-compile vs corpus split; Q3 testability; Q4 freeze vs re-roll.
2. Then: shared seed API; `SoundChangeRule` shape; sporadic rate / inventory force-apply vs enumerate.
3. Follow-up issue: nested sets (not this ticket).

## References

- [Ticket 60](60-correction-pass-parallel-column-null.md) — set-internal `∅` out of scope
- [Ticket 19](19-correction-pass-sporadic-qualifier.md) — sporadic flag; sample/skip still aspirational
- ASCA 0.10.2 Insertion/Deletion; LonelySet notes in [asca-rule-validity.md](../research/asca-rule-validity.md)
