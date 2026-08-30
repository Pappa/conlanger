Type: grilling
Status: ready-for-human
Blocked by:

# Grill: structured compile intermediate representation on SoundChangeRule

Owner (2026-08-21, after [ticket 92](92-grill-pydantic-compile-refactor.md)): hold **input** / **output** (and env/exception where it fits) as **collections** inside `SoundChangeRule` — sequences for condensed / **parallel-column** rules, ordered collections for `{…}` sets — so **optional outputs** and parallel-∅ **alternatives** are structural, not string-gated. **Do not fold into [ticket 93](93-pydantic-compile-refactor.md).** Run this grill **after [99](99-compiled-fields-join-at-render.md)** lands compiled field strings joined at render. **No code in this grill.**

Run `/grill-with-docs`.

## Question

What is the compile-time internal representation of a `SoundChangeRule`’s input, output, env, and exception — Index strings vs sequences of columns vs ordered set members vs a richer tree — so alternatives, **parallel columns**, and context fields can be detected and transformed without regex on blobs? YAML **stages** stay opaque ([ADR-0002](../../../docs/adr/0002-applier-neutral-yaml-rule-index.md), **optional outputs** in `CONTEXT.md`). Glossary: **Compile field**, **Compile-field intermediate representation**, **Parallel columns** in `CONTEXT.md`.

## Facts (do not re-litigate without new evidence)

- **93 + 99 first:** pydantic `BaseModel`s and per-field **string** transforms ([93](93-pydantic-compile-refactor.md) **resolved**). Compiled field attributes and join at `__str__` are [99](99-compiled-fields-join-at-render.md) — starting point for this grill is four compiled string attributes; owner now wants **raw + compiled** retained on typed field objects (see Round 1).
- **Parse does not detect alternatives.** First detection is compile (`_build_alternatives` / parallel expander).
- **Parallel columns** (formerly “condensed” in tickets): Index space-separated top-level segments (`c ɲ > ∅ n`; set columns `{r,h} > {∅,h}`). See tickets [60](60-correction-pass-parallel-column-null.md), [81](81-correction-pass-parallel-output-null.md).
- **Python `set` is unordered.** Inventory `alt_idx` and ASCA `{a,b}` are order-sensitive — prefer ordered sequences, not `set`.
- **Open overlap:** [ticket 71](71-grill-paren-and-parallel-set-notation.md) (`(h)ə{p,b}`, `e(C){V[…]}`) — optional-prefix parallel columns; **deferred** from v1 intermediate representation (Round 1).
- **Optional-length `(ː)`:** [ticket 104](104-correction-pass-parenthesized-optional-length-marker.md) — parenthesized optional length on segments, matrices (`V:[+front](ː)`), and templates (`V3(ː)`); distinct from matrix-suffix `]ː` ([79](79-correction-pass-matrix-suffix-length-marker.md)). **Not yet grilled** — session paused before Q6.
- Corpus YAML does **not** gain a structured alternatives field.

## Edge cases to grill (non-exhaustive)

1. **Column shape** — token list vs aligned input/output column pairs; space-separated IPA vs class letters vs matrices. **Deferred (Q1).**
2. **Set shape** — ordered list of members; nested `{…}` (tickets 69/70) vs parallel-column sets.
3. **Env / exception** — when a list/set, when a single string (`_`, `:{#_, _#}:`, prose). **Same field tier as I/O (Q3 settled).**
4. **When to parse into intermediate representation** — **Settled:** inside `compile_rule`, on pydantic field types (Q2).
5. **Alternatives** — fan-out from structure vs today’s string gates; still on `SoundChangeRule` (92 Q10). **Open (Q5).**
6. **Render** — intermediate representation → ASCA field strings then join (99 join point) vs → full `.rsca` line.
7. **Ticket 71** — **Settled:** defer; v1 covers parallel columns + `{…}` sets only (Q4).
8. **Transforms** — rewrite `compile/asca/` to walk intermediate representation, or stringify per step (defeats the point).
9. **Tests** — golden `.rsca` vs asserting structure; 93’s byte-identical bar may not apply.
10. **Optional-length `(ː)`** — [ticket 104](104-correction-pass-parenthesized-optional-length-marker.md): segment/matrix/template parenthesized length vs suffix `ː`; pipeline order (`length_marks` before `parenthetical` today); ticket 15 collapse vs `{segment, segment:[+long]}` expansion; interaction with `e(ː,j)` comma alternates. **Not yet grilled.**

## Outcomes

- [ ] Recorded intermediate representation for the four compile fields; ordered-collection rule (not `set`). **Q1 deferred.**
- [x] Handle now / defer vs ticket 71 — **defer** (Q4).
- [ ] **Review [104](104-correction-pass-parenthesized-optional-length-marker.md)** — policy and layer for parenthesized optional length `(ː)`; unblock implementation follow-on.
- [ ] Implementation follow-on ticket — **no code in this grill**.

## Settled (Round 1 — session paused 2026-08-30)

| Id | Decision |
|----|----------|
| Q2 | Parse inside `compile_rule` (not at pydantic init, not ephemeral-only inside pipeline). Typed pydantic field objects — **`RuleInput`**, **`RuleOutput`**, **`RuleEnv`** (exception reuses **`RuleEnv`**) — each holding **Index-raw and compiled ASCA** views (do not overwrite raw when compiling). Join at render reads compiled strings from these objects. |
| Q3 | Same as Q2 — env and exception use the same field tier (`RuleEnv`), not a separate string-only path. |
| Q4 | **Defer ticket 71** from v1 intermediate representation. v1 covers **parallel columns** and `{…}` sets only; `(h)ə{p,b}` / Family A–B shapes stay in parenthetical / cartesian string layer for now; extend structure in a follow-on after v1 lands. |

## Open (resume next session)

| Id | Status | Notes |
|----|--------|-------|
| Q1 | **Deferred** | Owner prefers a **rich** compile-field intermediate representation long-term (reliable for full rule syntax) but concerned about scope; **no shape locked**. Next round: phased v1 (columns + ordered sets) vs full tree, or explicit deferral criteria. |
| Q5 | **Open** | Owner unsure whether optional-output (66) and parallel-∅ (81) detection should move off string gates onto structure. Depends partly on Q1. |
| Q6 | **Not asked** | Ticket 104 `(ː)` policy — collapse vs `{segment, segment:[+long]}` expansion. |
| Q7–Q9 | **Not asked** | Transform walk, render helpers, test bar. |

## Session summary (2026-08-30)

**Round 1** of `/grill-with-docs`. Clarified terminology: use **compile-field intermediate representation** in docs (not “IR”). Added glossary entries in `CONTEXT.md`: **Compile field**, **Compile-field intermediate representation**, **Parallel columns**.

Owner direction differs from ticket 99’s “four compiled string attributes only”: compile fields should be **pydantic wrappers** retaining both Index-raw and compiled ASCA (`RuleInput` / `RuleOutput` / `RuleEnv`). Intermediate representation shape (Q1) and alternative detection source (Q5) remain open. Ticket 71 explicitly out of v1 scope. Session ended before ticket 104 and transform/render/test questions.

**Next frontier when resumed:** resolve Q1 (possibly as phased v1), then Q5, Q6, and transform/render/test round.

## Comments

> *This was generated by AI during triage.*

**2026-08-29:** [93](93-pydantic-compile-refactor.md) is `resolved` for `.rsca` emit. This grill stays blocked on [99](99-compiled-fields-join-at-render.md) (compiled field attributes + join at render).

**2026-08-30 (am):** [99](99-compiled-fields-join-at-render.md) resolved — grill unblocked on dependency chain. Added [104](104-correction-pass-parenthesized-optional-length-marker.md) to Facts, edge case 10, and Outcomes; review during session.

**2026-08-30 (pm):** Round 1 grill session — partial settle (Q2–Q4); Q1 deferred; Q5 open; Q6+ not reached. Glossary updated. Status stays `ready-for-human` until frontier empty.
