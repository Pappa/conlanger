Type: task
Status: ready-for-human
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

1. `uv run regenerate_corpus --update-series-mappings` baseline.
2. Close A–E per backlog (extractor fixes and/or authored CSV rows with HTML evidence).
3. Re-run coverage report + confidence tests; bump regression floors only when justified.
4. Regen corpus / inventory; note ok + section-complete deltas.

## Acceptance criteria

- [x] In-scope gaps closed or explicitly deferred with reason
- [x] Coverage report regenerated; tests green
- [x] Inventory before/after recorded

## Resolution (2026-08-12)

**Extractor (`series_extract.py`):**
- Length-mark merge (`ː`) in `_tokenize_rule_side`; trailing gloss strip
- Relaxed parallel I/O: mixed non-series slots + braced series members
- Collectives from inventory tables (not only citations) → §17 `hₓ`
- Lowest-priority digit attestation for series tokens named only in rule fields

**Coverage:** **101/101 (100%)** in-scope; CSV **107** rows (was 60). Families 6/10/17/30/46 all 100%.

**Inventory:** before **7456/9201 ok (81.0%)**, **248/714** sections all OK → after **7462/9201 ok (81.1%)**, fail **1739** (−6 fails; +6 ok flips). Sections all OK unchanged at **248/714**.

## References

- [series-mappings-coverage-backlog.md](../series-mappings-coverage-backlog.md)
- [series-mappings-coverage.md](../series-mappings-coverage.md)
- ADR-0004
