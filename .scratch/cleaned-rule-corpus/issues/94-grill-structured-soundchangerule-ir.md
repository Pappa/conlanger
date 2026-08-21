Type: grilling
Status: ready-for-human
Blocked by: 93

# Grill: structured compile IR on SoundChangeRule

Owner (2026-08-21, after [ticket 92](92-grill-pydantic-compile-refactor.md)): hold **input** / **output** (and env/exception where it fits) as **collections** inside `SoundChangeRule` — sequences for condensed / **parallel-column** rules, ordered collections for `{…}` sets — so **optional outputs** and parallel-∅ **alternatives** are structural, not string-gated. **Do not fold into [ticket 93](93-pydantic-compile-refactor.md).** Run this grill **after 93** lands the pydantic + per-field **string** compile. **No code in this grill.**

Run `/grill-with-docs`.

## Question

What is the compile-time internal representation of a `SoundChangeRule`’s input, output, env, and exception — Index strings vs sequences of columns vs ordered set members vs a richer tree — so alternatives, condensed (parallel-column) rules, and context fields can be detected and transformed without regex on blobs? YAML **stages** stay opaque ([ADR-0002](../../../docs/adr/0002-applier-neutral-yaml-rule-corpus.md), **optional outputs** in `CONTEXT.md`).

## Facts (do not re-litigate without new evidence)

- **93 first:** pydantic `BaseModel`s, per-field **string** transforms, join at render, alternatives on `SoundChangeRule` from raw I/O strings ([92 Answer](92-grill-pydantic-compile-refactor.md), [ADR-0014](../../../docs/adr/0014-per-field-asca-compile.md)).
- **Parse does not detect alternatives.** First detection is compile (`_build_alternatives` / parallel expander).
- **“Condensed” in this repo** = Index **parallel columns** (`c ɲ > ∅ n`; set columns `{r,h} > {∅,h}`). See tickets [60](60-correction-pass-parallel-column-null.md), [81](81-correction-pass-parallel-output-null.md).
- **Python `set` is unordered.** Inventory `alt_idx` and ASCA `{a,b}` are order-sensitive — prefer ordered sequences, not `set`.
- **Open overlap:** [ticket 71](71-grill-paren-and-parallel-set-notation.md) (`(h)ə{p,b}`, `e(C){V[…]}`) — optional-prefix parallel columns; may share this IR or stay separate.
- Corpus YAML does **not** gain a structured alternatives field.

## Edge cases to grill (non-exhaustive)

1. **Column IR** — token list vs aligned input/output column pairs; space-separated IPA vs class letters vs matrices.
2. **Set IR** — ordered list of members; nested `{…}` (tickets 69/70) vs parallel-column sets.
3. **Env / exception** — when a list/set, when a single string (`_`, `:{#_, _#}:`, prose).
4. **When to parse strings into IR** — at `SoundChangeRule` init before string transforms, after some transforms, or a dedicated builder.
5. **Alternatives** — fan-out from IR members vs today’s string gates; still on `SoundChangeRule` (92 Q10).
6. **Render** — IR → ASCA field strings then join (93 join point) vs IR → full `.rsca` line.
7. **Ticket 71** — in scope here, blocked by this, or still its own grill.
8. **Transforms** — rewrite `compile/asca/` to walk IR, or stringify per step (defeats the point).
9. **Tests** — golden `.rsca` vs asserting IR; 93’s byte-identical bar may not apply.

## Outcomes

- Recorded IR for the four compile fields; ordered-collection rule (not `set`).
- Handle now / defer / won’t-fix vs ticket 71.
- Implementation follow-on ticket — **no code in this grill**.
