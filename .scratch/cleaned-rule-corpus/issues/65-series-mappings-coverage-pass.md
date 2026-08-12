Type: task
Status: ready-for-agent
Blocked by:

# Series mappings coverage pass (backlog A–E)

Raise in-scope `series_mappings.csv` coverage beyond the ticket-28 baseline (**78/101 = 77.2%**; **23** gaps). Extraction + parse-time expansion already ship ([28](28-extract-correspondence-series-mappings-from-html.md), [27](27-implement-parse-time-correspondence-series-expansion.md)); this ticket **authors/fixes rows and extractor gaps** from [series-mappings-coverage-backlog.md](../series-mappings-coverage-backlog.md).

Priority: on the frontier, but **after** [62](62-correction-pass-tone-features.md) / [63](63-correction-pass-near-miss-unknown-character.md) unless unblocked parallel work is available.

## Scope (from backlog)

| Item | Est. pairs | Notes |
| --- | ---: | --- |
| A. Parallel rule I/O (family 10) | ~8 | Paiwan/Rukai; braced alternates |
| B. Omotic x-series | ~2 | `x₁`, `x₂` at §6.1.2.1 |
| C. PIE vowel+laryngeal compounds | ~11 | `eh₂`, `ih₁`, … |
| D. Collectives | ~1–10 | lowercase `hₓ` only; Greek `Hₓ` out of scope |
| E. Vowel-index series (§46) | ~2 | `i₂`, `æ₂` |

Out of scope here: positional/identity ([41](41-correction-pass-subscript-edge-cases.md)); uppercase section-local (`Sh₂`, `S₁`) — backlog F.

## What to build

1. `uv run extract_series_mappings` baseline.
2. Close A–E per backlog (extractor fixes and/or authored CSV rows with HTML evidence).
3. Re-run coverage report + confidence tests; bump regression floors only when justified.
4. Regen corpus / inventory; note ok + section-complete deltas.

## Acceptance criteria

- [ ] In-scope gaps closed or explicitly deferred with reason
- [ ] Coverage report regenerated; tests green
- [ ] Inventory before/after recorded

## References

- [series-mappings-coverage-backlog.md](../series-mappings-coverage-backlog.md)
- [series-mappings-coverage.md](../series-mappings-coverage.md)
- ADR-0004
