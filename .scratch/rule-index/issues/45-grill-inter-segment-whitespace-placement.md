Type: grilling
Status: resolved
Blocked by: None

# Grill: inter-segment whitespace placement

## Question

Lock the follow-on decisions from [Spike: inter-segment whitespace and phoneme boundaries](44-spike-inter-segment-whitespace.md) — especially whether applier-neutral SoT fields stay Index-shaped (compile-only Brassica spacing) or accept Brassica-style spaces in YAML.

Findings: [research/inter-segment-whitespace-phoneme-boundaries.md](../research/inter-segment-whitespace-phoneme-boundaries.md)

Prototype readout (UI explained + fixture dump): [research/parse-time-whitespace-prototype-results.md](../research/parse-time-whitespace-prototype-results.md)

## Scope

Grill questions from the spike Answer (one design tree). Do not implement.

## Settled (grill closed 2026-09-06; owner confirmed)

| Id | Decision |
|----|----------|
| Q1 | **No parse-time inter-segment spacing in YAML.** Applier-neutral **stages** stay Index-shaped. Brassica inter-segment spacing is an **applier compiler** transform only when Brassica compile exists ([ADR-0001](../../../docs/adr/0001-sound-change-applier-backends.md)). |
| Q2 | Index ASCII spaces mean **parallel field tokens at compile** ([ADR-0015](../../../docs/adr/0015-compile-field-intermediate-representation.md)), not phoneme boundaries. No separate parse-time “parallel spaces → commas” policy. |
| Q3 | **Affricate ties**, **`C[+voice]`** attachment, and **Kind B** bracket-internal spacing are **out of scope** for this grill — file narrow correction-pass or compile tickets only when a concrete inventory cluster or Brassica work demands them. |
| Q4 | **Structured segment arrays in YAML** — not v1. Compile uses **field tokens** per [ticket 94](94-grill-structured-soundchangerule-ir.md); richer trees deferred. |

## Answer

Owner confirmed (2026-09-06). **Compile-only Brassica inter-segment spacing; Index-shaped SoT.** Rejects parse-time ASCII-space mutation in YAML (prototype #46 lean no-go affirmed). Parallel Index spaces are modeled as **parallel tokens** at ASCA compile, not as inter-segment phoneme boundaries. Brassica multigraph inventory and spacing emission wait on Brassica compiler work.

## Progress

### Q1 — SoT inter-segment spacing

Maintainer rejected A/B/C lock; requested prototype first → [Prototype: parse-time inter-segment whitespace feasibility](46-prototype-parse-time-inter-segment-whitespace.md) (**resolved**).

Provisional prototype verdict: segmentiser sketch go-with-limits; shipping parse-time ASCII-space SoT mutation leans no-go until parallel/Kind-B/matrix issues are solved. Resume grill using the readout doc above.

**2026-09-06:** Confirmatory grill — locked compile-only; parse-time SoT mutation rejected.

## Session summary

**2026-09-06 — Confirmatory round:** Owner yes to all three frontier questions (SoT fork, parallel spaces = field tokens, leftover mechanics → narrow tickets). Grill closed.
