Type: task
Blocked by: 49

# Parser config: IPA mapping confidence levels

Target: wire `data/parser_config.yml` into `IndexDiachronicaParser` so IPA mapping confidence thresholds are configurable instead of hardcoded in `ipa_mappings_dict()`.

Spawned from triage of [Correction pass: IPA letter mappings](49-correction-pass-ipa-letter-mappings.md) (2026-08-08).

## Problem

[Correction pass 49](49-correction-pass-ipa-letter-mappings.md) seeded `data/common/ipa_mapping.csv` with high, medium, low, and defer rows. `ipa_mappings_dict()` currently applies only `confidence == "high"` (hardcoded). The config file `data/parser_config.yml` already lists the desired runtime levels:

```yaml
ipa_mapping:
  confidence:
    - high
    - medium
```

…but nothing loads or reads it yet.

## What to build

1. When `IndexDiachronicaParser` is executed, load parser config from `data/parser_config.yml` (default path; allow override for tests).
2. In `ipa_mappings_dict()`, use the `ipa_mapping.confidence` list from config to determine which CSV rows are included (instead of hardcoding `"high"`).
3. Pass loaded config (or the resolved confidence set) through the parse path so `apply_ipa_mappings()` uses the configured levels.
4. Unit tests: default config includes high+medium; custom config with `["high"]` only; missing/empty config falls back sensibly (document behaviour).

### Out of scope

- Adding new config keys beyond IPA mapping confidence
- Applying `low` or `defer` rows at runtime (config should not include them by default)
- Full inventory re-baseline (run after merge; record uplift in **Answer**)

## Policy

- Parse-time mapping only; `raw` unchanged.
- Config is the single source of truth for which confidence levels are active at runtime; CSV remains the mapping table.

## Acceptance criteria

- [ ] `IndexDiachronicaParser` loads `data/parser_config.yml` on execution
- [ ] `ipa_mappings_dict()` filters by config `ipa_mapping.confidence` levels
- [ ] Tests cover default (high+medium), high-only override, and config loading errors
- [ ] `test_ipa_mappings_dict_only_high_confidence` updated or superseded to match new behaviour

## Answer

_(pending)_

## References

- [Correction pass: IPA letter mappings](49-correction-pass-ipa-letter-mappings.md)
- [`data/parser_config.yml`](../../../data/parser_config.yml)
- [`data/common/ipa_mapping.csv`](../../../data/common/ipa_mapping.csv)
- [`parsers.py`](../../../src/conlanger/tools/parsers.py) — `load_ipa_mappings`, `ipa_mappings_dict`, `apply_ipa_mappings`, `IndexDiachronicaParser`
