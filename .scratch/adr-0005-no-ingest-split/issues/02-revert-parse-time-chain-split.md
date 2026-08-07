Type: task
Status: resolved
Blocked by: 01

# Revert parse-time chain split

## Question

Remove `expand_chained_rule_parts()` from `IndexDiachronicaParser` so chained rules (`a → b → c`, no env split criterion) remain **one corpus rule** with multi-segment `output`. Re-generate `data/diachronica/index_diachronica_parsed.yml` and update tests/fixtures that assumed row inflation from [ticket 18](../cleaned-rule-corpus/issues/18-correction-pass-chain-split.md).

**Acceptance:** parser emits one dict per HTML rule line for chain cases; `raw`/`source` unchanged; unit tests updated; inventory row count drops by ~135 vs post-18 baseline (order-of-magnitude check).

## Answer

**Done 2026-08-07.**

- Removed `expand_chained_rule_parts()` from `src/conlanger/tools/parsers.py`; `parse_rule_element` returns one corpus dict per HTML rule line.
- Regenerated `data/diachronica/index_diachronica_parsed.yml` via `uv run regenerate_corpus`.
- Tests updated: chain stays one row; e2e `chain-split` expects validation fail until [Compile-time chain expansion](03-compile-time-chain-expansion.md).

**Inventory (ASCA 0.10.2):**

| Metric | Before (post ticket 18) | After |
| --- | ---: | ---: |
| Corpus rules | 9317 | **9201** (−116 rows) |
| OK / total | 6518 / 9317 (70.0%) | **6395 / 9201 (69.5%)** (−123 ok) |

Regression window as expected until ticket 03.
