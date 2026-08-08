Type: prototype
Status: ready-for-agent
Blocked by: 44

# Prototype: parse-time inter-segment whitespace feasibility

## Question

Is it **feasible** to insert inter-segment (phoneme/grapheme) whitespace into rule fields **at HTML→YAML parse time**, such that the applier-neutral corpus carries spaced strings — without destroying Index meaning (especially parallel condensed parts) or making ASCA compile validation worse?

## Context

- Spike [Spike: inter-segment whitespace and phoneme boundaries](44-spike-inter-segment-whitespace.md) recommended **compile-only** Brassica spacing and Index-shaped SoT (ASCA 0.10.2 is space-optional; Index I/O spaces mostly mark parallel parts).
- Findings: [research/inter-segment-whitespace-phoneme-boundaries.md](../research/inter-segment-whitespace-phoneme-boundaries.md) · [research/inter-segment-whitespace-examples.csv](../research/inter-segment-whitespace-examples.csv).
- Maintainer chose **not** to lock A/B/C placement yet: build a throwaway prototype first ([Grill: inter-segment whitespace placement](45-grill-inter-segment-whitespace-placement.md)).

## What to prototype

Cheap, throwaway experiment (via `/prototype`) that:

1. Segmentises a **small fixture set** of Index-shaped `input`/`output`/`env` strings (glued, parallel-spaced, digraphs, `ː`, matrices, class letters, subscript compounds — pull examples from the spike CSV).
2. Inserts candidate inter-segment spaces with an explicit boundary algorithm (document assumptions).
3. Shows before/after strings and, where useful, ASCA `validate_asca` / Brassica-shaped readability side by side.
4. Surfaces failure modes: parallel-part ambiguity, affricate ties vs spaces, matrices, subscripts.

## Out of scope

- Merging into `IndexDiachronicaParser` or regenerating the full corpus
- Shipping a production correction pass
- Implementing a Brassica compiler
- Resolving the full grill tree (that waits on this prototype’s results)

## Acceptance criteria

- [ ] Throwaway prototype artifact linked from this ticket (script, notebook, or scratch module — not production path)
- [ ] Fixture table: Index string → spaced candidate → notes / pass-fail
- [ ] Written feasibility verdict: go / no-go / go-with-limits for parse-time SoT spacing
- [ ] Open questions fed back to [Grill: inter-segment whitespace placement](45-grill-inter-segment-whitespace-placement.md)

## Blocked by

- [Spike: inter-segment whitespace and phoneme boundaries](44-spike-inter-segment-whitespace.md)
