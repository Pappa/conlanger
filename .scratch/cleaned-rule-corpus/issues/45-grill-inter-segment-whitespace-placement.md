Type: grilling
Status: ready-for-agent
Blocked by: 44, 46

# Grill: inter-segment whitespace placement

## Question

Lock the follow-on decisions from [Spike: inter-segment whitespace and phoneme boundaries](44-spike-inter-segment-whitespace.md) — especially whether applier-neutral SoT fields stay Index-shaped (compile-only Brassica spacing) or accept Brassica-style spaces in YAML.

Findings: [research/inter-segment-whitespace-phoneme-boundaries.md](../research/inter-segment-whitespace-phoneme-boundaries.md)

## Scope

Grill questions from the spike Answer (one design tree). Do not implement.

## Blocked by

- [Spike: inter-segment whitespace and phoneme boundaries](44-spike-inter-segment-whitespace.md)
- [Prototype: parse-time inter-segment whitespace feasibility](46-prototype-parse-time-inter-segment-whitespace.md) — Q1 diverted here; resume grill after prototype verdict

## Progress

### Q1 — SoT inter-segment spacing

Maintainer rejected A (affirm compile-only) / B (Brassica-shaped SoT) / C (defer without experiment).

**Decision so far:** investigate parse-time insertion feasibility via prototype before locking placement. Ticket: [Prototype: parse-time inter-segment whitespace feasibility](46-prototype-parse-time-inter-segment-whitespace.md).
