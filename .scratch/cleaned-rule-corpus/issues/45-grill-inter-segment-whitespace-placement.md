Type: grilling
Status: ready-for-agent
Blocked by: 44

# Grill: inter-segment whitespace placement

## Question

Lock the follow-on decisions from [Spike: inter-segment whitespace and phoneme boundaries](44-spike-inter-segment-whitespace.md) — especially whether applier-neutral SoT fields stay Index-shaped (compile-only Brassica spacing) or accept Brassica-style spaces in YAML.

Findings: [research/inter-segment-whitespace-phoneme-boundaries.md](../research/inter-segment-whitespace-phoneme-boundaries.md)

Prototype readout (UI explained + fixture dump): [research/parse-time-whitespace-prototype-results.md](../research/parse-time-whitespace-prototype-results.md)

## Scope

Grill questions from the spike Answer (one design tree). Do not implement.

## Blocked by

- [Spike: inter-segment whitespace and phoneme boundaries](44-spike-inter-segment-whitespace.md)

## Progress

### Q1 — SoT inter-segment spacing

Maintainer rejected A/B/C lock; requested prototype first → [Prototype: parse-time inter-segment whitespace feasibility](46-prototype-parse-time-inter-segment-whitespace.md) (**resolved**).

Provisional prototype verdict: segmentiser sketch go-with-limits; shipping parse-time ASCII-space SoT mutation leans no-go until parallel/Kind-B/matrix issues are solved. Resume grill using the readout doc above.