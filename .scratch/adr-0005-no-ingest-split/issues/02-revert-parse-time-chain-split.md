Type: task
Status: open
Blocked by: 01

# Revert parse-time chain split

## Question

Remove `expand_chained_rule_parts()` from `IndexDiachronicaParser` so chained rules (`a → b → c`, no env split criterion) remain **one corpus rule** with multi-segment `output`. Re-generate `data/diachronica/index_diachronica_parsed.yml` and update tests/fixtures that assumed row inflation from [ticket 18](../cleaned-rule-corpus/issues/18-correction-pass-chain-split.md).

**Acceptance:** parser emits one dict per HTML rule line for chain cases; `raw`/`source` unchanged; unit tests updated; inventory row count drops by ~135 vs post-18 baseline (order-of-magnitude check).
