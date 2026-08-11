Type: task
Status: resolved
Blocked by: 12

# Correction pass: unknown_grouping (class letters at compile)

Target cluster: `unknown_grouping` — Index class letters from `group_mappings.csv` (317 rules at baseline)

## What was built

- `PhonologicalRuleSet` (`src/conlanger/tools/phonological_ruleset.py`) holds one applier-neutral section and delegates to `DiachronicSeries`.
- Index class letters from `data/asca/group_mappings.csv` expand in `RuleChange` during ASCA string emission (not in the corpus dict).
- `corpus_inventory.validate_corpus_rule` validates via `PhonologicalRuleSet(...).to_sound_change_ruleset()`.

## Answer (before/after)

Baseline (ticket 12 inventory, no compile mappings): **317** `unknown_grouping` failures; top tokens `E` (81), `U` (59), `R` (55), `B` (36), `T` (25).

Smoke re-check on the same 317 rows after compile mappings (ASCA 0.10.2, baseline probe wordlist):

- **~186 / 317** now pass `validate_asca` outright (~59% of the cluster).
- Remaining failures shift to other classes (`expected_underscore`, prose-in-env, unmapped `M`/`Y`/`I`/`X`, or letters in contexts the tokenizer still misses).

Re-run full inventory to refresh CSV/summary:

```bash
uv run regenerate_corpus
```

## Acceptance criteria

- [x] Target cluster named and sized in ticket body before work begins
- [x] Class-first transform implemented; no silent meaning-changing rewrites (uses validated CSV from spike 09)
- [x] Smoke before/after metrics recorded in ticket **Answer**
- [x] Tests added for mapping expansion and ASCA validation of known fixtures
