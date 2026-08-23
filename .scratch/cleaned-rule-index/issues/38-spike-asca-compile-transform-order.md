Type: spike
Status: resolved
Blocked by:

# Spike: ASCA compile transform ordering (planned steps)

## Question

Where in the applier compile pipeline should each **planned but unimplemented** ASCA compile transform run relative to the seven implemented steps — and why?

## Context

Grill session (2026-08-07): [Document the sound-change rule pipeline](37-document-sound-change-pipeline.md) lists implemented transforms with fixed order; planned transforms stay `Order: TBD` until this spike resolves them. Scope is **ASCA only** — not Brassica ordering or projection.

Open ordering questions called out in [map.md](../map.md) (subscript notation): e.g. positional slots / identity subscripts vs `group_mappings` vs length-mark normalization.

## Planned transforms to order (ASCA compile)

Investigate and assign slot numbers for **all** of the following (expand list if doc ticket 37 surfaces additional planned rows):

| Transform | Primary research / notes |
|-----------|-------------------------|
| Positional slots → ASCA reference syntax (`C=1`, bare `n`) | [positional-slots-and-identity-subscripts.md](../research/positional-slots-and-identity-subscripts.md) |
| Identity subscripts → ASCA reference syntax (`V=0`, bare `0`) | same |
| Section-local abbreviations (e.g. Athabaskan `TŠ`) | [06-resolve-applier-unsupported-abbreviations.md](06-resolve-applier-unsupported-abbreviations.md); cluster-driven |
| Meta-notation (retroflex `X̣`, `(…X)` repetition, tone superscripts, …) | [subscript-notation-index-asca-brassica.md](../research/subscript-notation-index-asca-brassica.md); no global expansion yet |

**Out of scope:** Brassica compile path; parse-time transforms (documented in `docs/index-diachronica-parser.md`).

## What to investigate

1. **Dependency analysis** — for each planned transform, what must already be true in the rule string (expanded class letters? normalized length marks? bracket-safe segments?) before it can run safely.
2. **Prototype where needed** — minimal Python or scripted probes applying transforms in candidate orders on representative rules from research fixtures / inventory clusters; run `validate_asca` when a full rule string is producible.
3. **Interaction with implemented steps** — document conflicts if a planned transform were run too early or too late (e.g. reference syntax on tokens that `group_mappings` would mangle).
4. **Compound / edge cases** — call out rules that need a separate implementation ticket (e.g. `mV₀`, `C₁ˤC₂`) without blocking the happy-path ordering recommendation.

## Deliverable

Findings markdown under `.scratch/cleaned-rule-index/research/` (e.g. `asca-compile-transform-order.md`) containing:

- Updated pipeline table fragment: all planned rows with recommended `Order` integers and rationale.
- Explicit “rejected orderings” notes where alternatives were tried.
- Open questions suitable for follow-on **task** tickets (implementation), not more ordering spikes.

Update `docs/sound-change-applier.md` TBD rows if ticket 37 has landed (otherwise leave findings for 37 follow-up edit).

## Acceptance criteria

- [x] Research file written with cited primary sources (code, ASCA 0.10.2 docs, existing `.scratch` research).
- [x] Every planned transform in scope has a recommended order relative to the seven implemented steps.
- [x] At least positional/identity vs `group_mappings` ordering is decided with evidence (prototype or ASCA probe).
- [x] Brassica explicitly excluded.
- [x] Recommendation suitable to unblock [Refactor DiachronicSeries](39-refactor-sound-change-ruleset.md).

## Answer

Findings: [research/asca-compile-transform-order.md](../research/asca-compile-transform-order.md)

Renumbered ASCA compile pipeline (10 steps): insert **Order 3** `expand_index_subscript_references` (positional + identity) and **Order 4** `apply_section_local_abbreviations` before existing group mappings; **Order 10** `expand_meta_notation` (cluster-driven, last). Section-local before group mappings is **mandatory** (`TS > ts` probe). Refs before length marks is **mandatory** (extend length pass for `\dː`). Ticket 37 can paste the §6 table fragment into `docs/sound-change-applier.md`.

## Comments
