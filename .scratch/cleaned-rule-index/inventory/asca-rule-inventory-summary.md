# Cleaned rule index — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9840** (one per index rule)

## Rules
- OK: **8385** (85.2%)
- Fail: **843** (8.6%)
- Skipped: **612** (6.2%)

## Sections

- All OK: **417 / 714** (58.4%)
- Some OK: **268 / 714** (37.5%)
- None OK: **4 / 714** (0.6%)
- Sections skipped: **25 / 714** (3.5%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 256 | `syntax_other` |
| 138 | `runtime_other` |
| 122 | `unknown_character` |
| 115 | `expected_underscore` |
| 58 | `invalid_ipa` |
| 36 | `expected_number` |
| 32 | `prose_or_expected_arrow` |
| 23 | `unknown_feature` |
| 20 | `nested_brackets` |
| 14 | `stuff_after_word_bound` |
| 11 | `unknown_grouping` |
| 9 | `diacritic_prereq` |
| 3 | `panic_other` |
| 2 | `format_error` |
| 2 | `runtime_delete_only_segment` |
| 2 | `other` |

## Common Errors

### syntax_other

| count | error_token |
|------:|-------------|
| 20 | `)` |
| 18 | `ʷ` |
| 17 | `(` |
| 10 | `:` |
| 9 | `''` |
| 8 | `/` |
| 6 | `>` |
| 6 | `∅` |
| 6 | `ʼ` |
| 5 | `_` |

### runtime_other

| count | description |
|------:|-------------|
| 8 | `Runtime Error: Unknown reference '3' | {i3,ə1} > ə1 | ^ @ Rule 1, Line 1` |
| 7 | `Runtime Error: Unknown reference '3' | {a3,ə3} > ə3 | ^ @ Rule 1, Line 1` |
| 7 | `Runtime Error: Unknown reference '1' | {i1,ə1} > ə1 | ^ @ Rule 1, Line 1` |
| 7 | `Runtime Error: Unknown reference '3' | {i3,e3} > {ə3,i3} | ^ @ Rule 1, Line 1` |
| 5 | `Runtime Error: Unknown reference '1' | {a1,i1} > ə1 | ^ @ Rule 1, Line 1` |
| 5 | `Runtime Error: Unknown reference '3' | {u3,ə3} > ə3 | ^ @ Rule 1, Line 1` |
| 5 | `Runtime Error: Unknown reference '3' | {a3,i3} > ə3 | ^ @ Rule 1, Line 1` |
| 5 | `Runtime Error: Unknown reference '1' | a1 > ə1 | ^ @ Rule 1, Line 1` |
| 4 | `Runtime Error: Unknown reference '3' | V3h > V3:[+long] / _C | ^ @ Rule 1, Line 1` |
| 4 | `Runtime Error: Unknown reference '3' | {i3,ə1} > i3 | ^ @ Rule 1, Line 1` |

### unknown_character

| count | error_token |
|------:|-------------|
| 22 | `̣` |
| 13 | `₂` |
| 11 | `̊` |
| 6 | `̺` |
| 6 | `ŕ` |
| 5 | `ː` |
| 5 | `͜` |
| 5 | `ₙ` |
| 4 | `̂` |
| 4 | `̻` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 6 | `M` |
| 3 | `Y` |
| 1 | `I` |
| 1 | `X` |

### expected_underscore

| count | error_token |
|------:|-------------|
| 72 | `''` |
| 17 | `,` |
| 17 | `/` |
| 2 | `*` |
| 2 | `ʷ` |
| 1 | `:` |

### nested_brackets

| count | description |
|------:|-------------|
| 2 | `Syntax Error: Cannot have nested brackets of the same type | {V:[+stress](C)CaCV,VC:[+stress](C)CaCV} > {V:[+stress]((C)CaCV,VC:[+stress]((C)CaCV} / _# | ^ @ Rule 1, Line 1` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | e o u æ ø y > {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i} / _Ca | ^ @ Rule 1, Line 1` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | {{ɣ, ɣʷ, xʷ},x} > ɡ | ^ @ Rule 1, Line 1` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | m n ŋ t {{ɣ,ʁ} > {k,q}} / _# | ^ @ Rule 1, Line 1` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | V > ∅ / #%%(_)%(%(_)%) // _[-stress] | ^ @ Rule 1, Line 1` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | {æ,e}:[+long](w(a)) > a:[+long] | ^ @ Rule 1, Line 1` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | w > ∅ / C_ɹ for some C (toward(s), quart(er), sword) | ^ @ Rule 1, Line 1` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | ʃ > is (except in the west or extreme east, where the outcome was some flavor of (i)(t)ʃ) | ^ @ Rule 1, Line 2` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | nVs dVs > n(V(s)) {ʒ,ʒVʒ} | ^ @ Rule 1, Line 1` |
| 1 | `Syntax Error: Cannot have nested brackets of the same type | V=1 kV=2 > 2:[+long] / #((C)V(C))(C)_# | ^ @ Rule 1, Line 1` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 5 | `weak` | `man` |
| 3 | `initial` | `nasal` |
| 3 | `palatalized` | `latrl` |
| 2 | `fricative` | `rhotic` |
| 1 | `highpitch` | `high` |
| 1 | `lowpitch` | `voice` |
| 1 | `posttonic` | `sonor` |
| 1 | `ejective` | `contin` |
| 1 | `alveolopalatal` | `consonantal` |
| 1 | `intertonic` | `anterior` |

### expected_number

| count | error_token |
|------:|-------------|
| 4 | `d` |
| 3 | `{` |
| 3 | `j` |
| 3 | `ɒ` |
| 3 | `r` |
| 2 | `N` |
| 2 | `C` |
| 2 | `s` |
| 2 | `a` |
| 2 | `u` |

### prose_or_expected_arrow

| count | error_token |
|------:|-------------|
| 21 | `ˀ` |
| 2 | `*` |
| 2 | `)` |
| 2 | `/` |
| 1 | `}` |
| 1 | `ʱ` |
| 1 | `:` |
| 1 | `̥` |
| 1 | `ʷ` |

## Notes

- Inventory runs per index rule via `DiachronicSeries` + `validate_asca`.
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
- Field blame OK rows: [asca-field-isolation-success.csv](asca-field-isolation-success.csv)
- Field blame fail rows: [asca-field-isolation-error.csv](asca-field-isolation-error.csv)
- syntax_other: [syntax_other_errors.csv](syntax_other_errors.csv)
- runtime_other: [runtime_other_errors.csv](runtime_other_errors.csv)
- unknown_character: [unknown_character_errors.csv](unknown_character_errors.csv)
- unknown_grouping: [unknown_grouping_errors.csv](unknown_grouping_errors.csv)
- expected_underscore: [expected_underscore_errors.csv](expected_underscore_errors.csv)
- nested_brackets: [nested_brackets_errors.csv](nested_brackets_errors.csv)
- unknown_feature: [unknown_features_errors.csv](unknown_features_errors.csv)
- expected_number: [expected_number_errors.csv](expected_number_errors.csv)
- prose_or_expected_arrow: [prose_or_expected_arrow_errors.csv](prose_or_expected_arrow_errors.csv)
