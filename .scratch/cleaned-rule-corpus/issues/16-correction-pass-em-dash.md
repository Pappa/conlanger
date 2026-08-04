Type: task
Status: resolved
Blocked by: 15

# Correction pass: unknown_character — em dash —

Target cluster: `unknown_character` — error_token `—` (266 rules at baseline)

## What was built

- `strip_leading_index_rule_marker()` in `src/conlanger/tools/rules.py` — ASCA compile transform (not ingest):
  - Strip leading `— ` (U+2014 em dash + optional space) from each rule field (`input`, `output`, `env`, `exception`) before assembly.
- Wired in `RuleChange._compile_rule_text()` at **instantiation**, ASCA only, before group mappings and length marks.
- Corpus dict fields and `raw` unchanged.

## Answer (before/after)

Baseline: **266** rules with `unknown_character` / error_token `—` (265/266 leading `—` on `input`).

Smoke re-check: **157 / 266** now pass with leading-marker strip; 1 inline em dash; remainder fail other classes.

Re-run full inventory:

```bash
uv run python -m conlanger.scripts.regenerate_corpus
```

## Notes

- Index Diachronica uses `—` to mark sub-rule lines under a numbered entry, not as a phonological segment.
- Inline `—` in env (1 rule) left for a later cluster.

## Acceptance criteria

- [x] Class-first ASCA compile transform; corpus stays applier-neutral
- [x] Unit + ASCA integration tests on representative fixtures
- [x] Smoke before/after metrics recorded
