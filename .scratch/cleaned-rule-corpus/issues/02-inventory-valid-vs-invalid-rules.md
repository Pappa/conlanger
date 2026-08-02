Type: task
Status: resolved
Blocked by: 01

# Inventory which current rules compile and which fail

## Question

Against the current Index Diachronica–derived artifacts (`index_diachronica_original.html` and/or provisional YAML/XML), produce a recorded inventory of rules that **compile/validate under ASCA** vs those that **fail**, with enough section/index identity to analyse failure classes later.

## Notes

- Depends on [What counts as a valid ASCA rule string?](01-valid-asca-rule-string.md) for criteria (and any chosen CLI/library check).
- Brute-force ASCA CLI checks are acceptable; also need a durable recorded corpus of results (e.g. CSV alongside the rule identity).
- This ticket gathers evidence for decisions — it does not itself define the correction policy (see correction-workflow ticket).
- Existing `notebooks/data/asca_errors.csv` / related files may be reusable starting points.
- Criteria used: [asca-rule-validity.md](../research/asca-rule-validity.md).

## Answer

Ran a fresh per-rule inventory against provisional ASCA-flavoured YAML `notebooks/data/index_diachronica_ai.yml` with `asca 0.9.3` (`asca run` + probe wordlist), via `scripts/inventory_asca_rules.py`.

| metric | value |
|--------|------:|
| rules checked | 9721 |
| ok | 5554 (57.1%) |
| fail | 4167 (42.9%) |

Top failure classes: `syntax_other` (2652), `nested_brackets` (585), `expected_underscore` (333), `unknown_feature` (217), `prose_or_expected_arrow` (153).

**Artifacts:**
- [../inventory/asca-rule-inventory.csv](../inventory/asca-rule-inventory.csv) — one row per rule (`section_index`, `section_name`, `rule_idx`, `syntax`, `ok`, `returncode`, `error`, `error_class`)
- [../inventory/asca-rule-inventory-summary.md](../inventory/asca-rule-inventory-summary.md)

Note: `ok` is full `asca run` success on the probe wordlist (not parse-only); a small slice is runtime (`runtime_delete_only_segment`, etc.). This is evidence for correction-policy tickets, not the cleaned corpus itself.
