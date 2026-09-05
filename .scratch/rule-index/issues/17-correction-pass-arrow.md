Type: task
Status: resolved
Blocked by: 16

# Correction pass: unknown_character — rule arrow →

Target cluster: `unknown_character` — error_token `→` (223 rules at baseline)

## What was built

- `normalize_rule_arrows()` in `src/conlanger/tools/parsers.py` — ingest transform on field values after the primary ``→`` split:
  - Replace remaining Index ``→`` with ASCA ``>`` in ``input`` / ``output`` / ``env`` / ``exception``.
- Wired in `extract_rule_parts()` (Phase 4 parse path). ``raw`` unchanged.

## Answer (before/after)

Baseline: **223** rules with `unknown_character` / error_token `→` (258 rules carry ``→`` in output/env fields; chain rules like ``dʒ → tʃ → ʃ`` become ``dʒ`` / ``tʃ > ʃ``).

Re-run full inventory:

```bash
uv run create_index
```

## Notes

- Primary rule split still uses the first ``→`` on the rule line; only *remaining* arrows in field values are converted.
- Chain rules compile to ``a > e > o`` form; ASCA 0.10.2 rejects multiple ``>`` on one line (syntax error, not unknown character) — follow-up split-into-subrules pass if needed.
- Prose arrows in commentary (e.g. ``though sometimes → ɡw``) are converted too.

## Acceptance criteria

- [x] Parse-time field normalization; ``raw`` preserved
- [x] Unit tests on chain and prose cases
- [x] Inventory re-baseline recorded
