Type: task
Status: resolved
Blocked by: 17

# Correction pass: chained rules — parse-time split

Target cluster: `syntax_other` — multi-`>` chains without env/exception (140+ at baseline after arrow normalization)

## Analysis: env/exception on chained rules

Of **258** rules with chain notation in the corpus:

| | count |
|---|------:|
| With `env` | 126 |
| With `exception` | 5 |
| With both | 4 |
| **No env and no exception** | **131** |

Of the 131 without env/exception, **113** have ` > ` in `output` after arrow normalization and are split candidates.

## What was built

- `expand_chained_rule_parts()` in `src/conlanger/tools/parsers.py`
- Wired in `IndexDiachronicaParser.parse_rule_element()` — returns a list of rule dicts
- Split criterion: no `env`, no `exception`, and `output` contains ` > ` with 2+ segments
- Each step becomes `{input: prev, output: next}`; shared `raw`/`source` preserved
- Chains **with** env/exception stay one row (e.g. `{θ,l} → r → l / V_V`)

## Answer (before/after)

Smoke on 113 split candidates: **44 / 113** pass ASCA after split (0 regressions).

Full inventory: **5592 / 9336 ok (59.9%)**, up from 5456 / 9201 (+136 ok, +135 corpus rows from expansion).

## Notes

- Corpus rule count increases (one HTML line → N sequential rules).
- Prose with embedded ` > ` may over-split; no env gate is the confidence criterion per spec discussion.

## Acceptance criteria

- [x] Parse-time split for no-env/no-exception chains
- [x] Unit + ASCA integration tests
- [x] Inventory re-baseline recorded
