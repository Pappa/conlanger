# ASCA rule inventory summary

- Source YAML: `notebooks/data/index_diachronica_ai.yml`
- Probe words: `notebooks/data/words/asca/weirdness_0.5.wsca`
- Checker: `asca 0.9.3` via `scripts/inventory_asca_rules.py`
- Criteria: `.scratch/cleaned-rule-corpus/research/asca-rule-validity.md`
- Rows: **9721** (one per provisional corpus rule)
- OK: **5554** (57.1%)
- Fail: **4167** (42.9%)

## Failure classes

| count | error_class |
|------:|-------------|
| 2652 | `syntax_other` |
| 585 | `nested_brackets` |
| 333 | `expected_underscore` |
| 217 | `unknown_feature` |
| 153 | `prose_or_expected_arrow` |
| 74 | `stuff_after_word_bound` |
| 56 | `runtime_other` |
| 30 | `runtime_delete_only_segment` |
| 26 | `diacritic_prereq` |
| 24 | `expected_number` |
| 16 | `unknown_grouping` |
| 1 | `empty_io_panic` |

## Notes

- `ok` means `asca run` returned 0 on the probe wordlist (parse + apply). Some failures are runtime on that wordlist (`runtime_delete_only_segment`), not pure syntax.
- Inventory is against provisional ASCA-flavoured YAML (`index_diachronica_ai.yml`), not yet the cleaned schema corpus.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
