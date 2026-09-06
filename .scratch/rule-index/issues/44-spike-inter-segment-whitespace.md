Type: spike
Status: resolved

# Spike: inter-segment whitespace and phoneme boundaries

## Question

How should Index Diachronica rule fields gain **inter-segment whitespace** so the **applier-neutral** cleaned index matches ASCA and Brassica’s space-separated phoneme convention — including how to detect **digraph / trigraph** graphemes and phoneme boundaries around length markers, feature matrices, class letters, sets, and subscript compounds?

## Why now

Map fog (deferred from [Normalise segment feature matrices for appliers](07-normalise-segment-features.md)): **Whitespace tokenisation for ASCA**. Maintainer intent: spaced segments should live in the applier-neutral SoT, not only at applier compile. That policy still needs evidence before implementation.

## Scope of this spike

1. **Primary sources** — How ASCA **0.10.2** and Brassica tokenise / require whitespace between segments (official docs + relevant parser behaviour). Distinguish inter-segment spaces from spaces inside feature matrices (`[+high tone]`).
2. **Corpus survey** — Sample Index / cleaned YAML input/output/env sides: already-spaced vs glued; digraph/trigraph candidates; interaction with `ː`/`ˑ`, `[+…]`, `{…}`, class letters, correspondence-series / positional / identity subscripts.
3. **Boundary algorithm sketch** — Propose a deterministic segmentation approach (tables, longest-match, IPA inventory, etc.) with known failure modes and open questions.
4. **Placement recommendation** — Evidence for parse-time SoT spacing vs compile-only (feed a follow-on grill / ADR if needed). Do **not** implement the transform in this spike.

## Out of scope

- Shipping a correction pass or mutating `index_diachronica_parsed.yml`
- Brassica compiler implementation (ADR-0001)
- Resolving bracket-internal feature-name spacing alone (related; note overlap, do not own as the deliverable)

## Deliverables

- Findings markdown under `.scratch/rule-index/research/` (cite primary sources)
- Optional supporting CSV or example table of digraph/trigraph / boundary cases if useful
- Explicit follow-on: grill questions + implementation ticket shape

## Acceptance criteria

- [x] ASCA and Brassica whitespace / segment-token rules cited from primary sources
- [x] Corpus sample documents glued vs spaced patterns and digraph/trigraph candidates with counts or representative examples
- [x] Boundary algorithm sketch + failure modes written down
- [x] Recommendation: SoT (parse-time) vs compile-only, with open grill questions listed
- [x] Findings linked from this ticket’s **Answer**; no production code change required to resolve

## Blocked by

- None (inventory + docs already exist; builds on deferred note from ticket 07)

## Answer

**Compile-only for Brassica inter-segment spaces; keep Index-shaped SoT.** ASCA 0.10.2 does **not** require space-separated phonemes (IPA trie + optional whitespace); Brassica does. Index I/O spaces mostly mean **parallel condensed parts**, not phoneme boundaries. Digraph problem for ASCA is **ties** (`t͡ʃ`), not spaces.

Findings: [research/inter-segment-whitespace-phoneme-boundaries.md](../research/inter-segment-whitespace-phoneme-boundaries.md) · examples: [research/inter-segment-whitespace-examples.csv](../research/inter-segment-whitespace-examples.csv).

### Grill / follow-on (for parent session)

1. Confirm reject parse-time SoT spacing (or explicitly accept Brassica-shaped SoT / ADR-0002 amend)?
2. Index parallel spaces → ASCA commas: parse or compile?
3. Affricate ties at ASCA compile: always vs cluster-driven?
4. Who authors Brassica multigraph inventory?
5. Kind B `[+high tone]` spacing — schedule under feature ingest?
6. Future structured `segments: […]` IR?

No implementation ticket filed; Brassica spacing ticket only after Brassica compiler work. Placement grill [45](45-grill-inter-segment-whitespace-placement.md) **resolved** 2026-09-06 (compile-only; parallel spaces = field tokens).
