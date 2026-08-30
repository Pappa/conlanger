# Cleaned rule index — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **50** (one per index rule)

## Rules
- OK: **49** (98.0%)
- Fail: **1** (2.0%)
- Skipped: **0** (0.0%)

## Sections

- All OK: **3 / 4** (75.0%)
- Some OK: **1 / 4** (25.0%)
- None OK: **0 / 4** (0.0%)
- Sections skipped: **0 / 4** (0.0%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 1 | `unknown_character` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 1 | `+` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| — | _(none)_ | — |

### unknown_grouping

| count | error_token |
|------:|-------------|
| — | _(none)_ |


## Field isolation blame (error rows)

| count | blame |
|------:|-------|
| 1 | `env` |

## Notes

- Inventory runs per index rule via `DiachronicSeries` + `validate_asca`.
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
- Field blame OK rows: [asca-field-isolation-success.csv](asca-field-isolation-success.csv)
- Field blame fail rows: [asca-field-isolation-error.csv](asca-field-isolation-error.csv)
- Grouping errors: [grouping_errors.csv](grouping_errors.csv)
- Character errors: [character_errors.csv](character_errors.csv)
- Underscore errors: [underscore_errors.csv](underscore_errors.csv)
