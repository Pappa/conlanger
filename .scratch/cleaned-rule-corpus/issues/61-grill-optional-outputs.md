Type: grilling
Status: needs-grilling

# Grill: optional outputs for unpaired Index output sets

## Question

Index rules like `d → {∅,ð} / V_V` and `ɡ → {∅,ɣ} / V_V` encode speaker variation (including null). ASCA 0.10.2 rejects `∅` inside sets. How should the cleaned corpus and ASCA compile/render path retain alternatives and choose one for emission — without making unit tests unable to exercise every alternative?

## Settled so far (grill 2026-08-09, paused)

- Glossary term: **Optional outputs** (distinct from **sporadic**) — `CONTEXT.md`.
- Trigger (provisional): explode when **input is not a set** and **output is a set**; do not treat paired `{a,b} → {c,d}` as optional outputs.
- YAML SoT: **unchanged** — keep opaque set strings in **stages** (e.g. `'{∅,ð}'`); no new structured field.
- Ticket 60 parallel-column nulls remain out of scope for set-internal `∅`; this ticket is the follow-on for that cluster (~45 inventory rows with `{∅`).

## Open / blocked on rethink

- **When to choose** an alternative: earlier lean was `str(DiachronicSeries)`; then revised to `SoundChangeRule` instantiation via `random` + caller `random.seed`.
- **Testability concern (owner pause):** instantiation-time `random.choice` means unit tests will not systematically exercise every alternative unless tests inject choice or enumerate members explicitly.
- Whether `SoundChangeRule` keeps `outputs: tuple[str, …]` plus selected `output`, or only the chosen string.
- Set-detection heuristic (whole-field `{…}`).
- Fixed seed for inventory/regen vs free seed for generative apply.
- Relationship to future sporadic sample/skip (still unimplemented on render).

## Facts (do not re-litigate)

- ASCA rejects `d > {∅,ð} / V_V`; `d > ∅ / V_V` and `d > ð / V_V` are valid.
- `SoundChangeRule` today freezes compiled `value` in `__init__`; ignores `sporadic`.
- No RNG on the sound-change render path today.
- Corpus: ~85 `{∅` lines in parsed YAML; canonical Spanish examples at `index_diachronica_original.html:8156–8157`.

## Next grilling round (when resumed)

Start from testability: how should tests force or enumerate each optional output without relying on chance? Then re-decide selection timing and `SoundChangeRule` shape.

## References

- [Ticket 60](60-correction-pass-parallel-column-null.md) — set-internal `∅` out of scope
- [Ticket 19](19-correction-pass-sporadic-qualifier.md) — sporadic flag; sample/skip still aspirational
- ASCA 0.10.2 Insertion/Deletion; LonelySet notes in [asca-rule-validity.md](../research/asca-rule-validity.md)
