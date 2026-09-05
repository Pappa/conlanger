Type: task
Status: resolved
Blocked by: 15

# Correction pass: unknown_character — em dash —

Target cluster: `unknown_character` — error_token `—` (266 rules at baseline)

## What was built

- `strip_leading_index_list_marker()` in `src/conlanger/tools/parsers.py` — ingest transform on the full rule line (not stored in ``raw``):
  - Strip leading `— ` (U+2014 em dash + optional space) before field split.
- Wired in `extract_rule_parts()` (Phase 4 parse path), applier-neutral.
- Corpus ``input`` / ``output`` / ``env`` / ``exception`` no longer carry the list marker; ``raw`` unchanged.

## Answer (before/after)

Baseline: **266** rules with `unknown_character` / error_token `—` (265/266 leading `—` on `input`).

Smoke re-check: **157 / 266** now pass with leading-marker strip; 1 inline em dash; remainder fail other classes.

Re-run full inventory:

```bash
uv run create_index
```

## Notes

- Index Diachronica uses `—` as a list-item starter on sub-rule lines, not as a phonological segment.
- Inline `—` in env (1 rule) left for a later cluster.

## Acceptance criteria

- [x] Class-first parse transform; ``raw`` preserved
- [x] Unit + ASCA integration tests on representative fixtures
- [x] Smoke before/after metrics recorded
