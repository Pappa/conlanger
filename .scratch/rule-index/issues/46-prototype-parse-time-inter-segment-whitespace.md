Type: prototype
Status: resolved
Blocked by: 44

# Prototype: parse-time inter-segment whitespace feasibility

## Question

Is it **feasible** to insert inter-segment (phoneme/grapheme) whitespace into rule fields **at HTML→YAML parse time**, such that the applier-neutral index carries spaced strings — without destroying Index meaning (especially parallel condensed parts) or making ASCA compile validation worse?

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

- Merging into `IndexDiachronicaParser` or regenerating the full index
- Shipping a production correction pass
- Implementing a Brassica compiler
- Resolving the full grill tree (that waits on this prototype’s results)

## Acceptance criteria

- [x] Throwaway prototype artifact linked from this ticket (script, notebook, or scratch module — not production path)
- [x] Fixture table: Index string → spaced candidate → notes / pass-fail
- [x] Written feasibility verdict: go / no-go / go-with-limits for parse-time SoT spacing
- [x] Open questions fed back to [Grill: inter-segment whitespace placement](45-grill-inter-segment-whitespace-placement.md)

## Prototype artifact

- [prototypes/parse-time-inter-segment-whitespace.html](../prototypes/parse-time-inter-segment-whitespace.html) — throwaway shareable demo (open in a browser). Pure segmentiser in the first `<script>` module; page shell is disposable.

**Run:** open that HTML file (double-click or IDE preview). No install.

## Blocked by

- [Spike: inter-segment whitespace and phoneme boundaries](44-spike-inter-segment-whitespace.md)

## Answer

**How to read the demo + fixture dump for later review** (maintainer found the live UI hard to interpret):

- Findings (spike-style): [research/parse-time-whitespace-prototype-results.md](../research/parse-time-whitespace-prototype-results.md)
- CSV: [research/parse-time-whitespace-prototype-results.csv](../research/parse-time-whitespace-prototype-results.csv)

**Verdict (provisional, for grill):** segmentiser sketch is **go-with-limits**; shipping parse-time ASCII-space SoT mutation leans **no-go** until parallel vs phoneme spaces, class+matrix attachment, and Kind B bracket spaces are solved. Placement policy locked by [Grill: inter-segment whitespace placement](45-grill-inter-segment-whitespace-placement.md) (**resolved** 2026-09-06): compile-only; parallel spaces = field tokens at compile.

