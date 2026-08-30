Type: task
Status: resolved

# Remove production config content assertions from unit tests

Pre-requisite for [101 refactor config layout and injection](101-refactor-config-layout-and-injection.md). Today many unit tests load package-default CSV/YAML under `data/` and assert specific seed rows or values (PIE laryngeals, `group_mappings` abbrev keys, `feature_mappings` bundle rows, IPA confidence tiers). Those tests will fight the config relocation in ticket 101 and make like-for-like inventory comparison harder.

This ticket **only** changes tests (and test helpers if needed). No production code moves, no config path changes.

## Problem

Examples of production-content coupling:

| File | Pattern |
| --- | --- |
| `tests/conlanger/utils/test_compiler_config.py` | `load_compiler_config()` → assert `h₁`/`h₂`/`h₃` targets |
| `tests/conlanger/tools/ingest/test_parser.py` | `load_group_mappings()`, `load_feature_mappings()`, `load_ipa_mappings()`, `load_parser_config()` without `tmp_path` → assert seed rows |
| `tests/conlanger/tools/ingest/test_parser.py` | `feature_mappings_dict()`, `ipa_mappings_dict(config=load_parser_config())` in transform tests |
| `tests/conlanger/tools/test_group_mappings.py` | `test_asca_group_mappings_dict_loads_package_csv` |
| `tests/conlanger/tools/compile/asca/test_tone_matrices.py` | `feature_mappings_dict()` for tone rows |
| `tests/helpers.py` | `default_index_parser()` caches `load_default_ingest_tables()` (production tables) |

Behavioral tests (parser/compile integration) may still need mapping data — but it must come from **inline fixtures** or `tmp_path` YAML/CSV owned by the test, not from asserting the live `data/` tree.

## What to do

### Delete outright

Remove tests whose **only** purpose is verifying production seed data exists with expected values, e.g.:

- `test_load_compiler_config_default_includes_pie_laryngeals`
- `test_load_group_mappings_default_csv` (abbrev key assertions)
- `test_load_feature_mappings_from_default_csv`
- `test_load_ipa_mappings_from_default_csv`
- `test_load_parser_config_default_includes_high_and_medium`
- `test_ipa_mappings_dict_uses_config_confidence_levels` (production IPA file + production confidence)
- `test_asca_group_mappings_dict_loads_package_csv`

Keep **tmp_path** loader tests (malformed rows, overlay ignored, high-only config override, etc.) — those already own their YAML.

### Refactor to inline fixtures

For tests that exercise **transform logic** but currently pull production dicts:

- `test_normalize_feature_matrices_in_field_*` — build minimal `dict[str, FeatureMapping]` inline (only rows each case needs).
- `test_tone_matrices.py` — inline tone `FeatureMapping` rows.
- `test_kenyah_vowel_height_rules_validate` — inline feature + group mappings (or `{}` group if unused).
- `test_normalize_ipa_in_field`, `test_parse_rule_element_normalizes_ipa_characters`, confidence-level parse tests — pass explicit `ipa_mappings` dict + `ParserConfig` to parser constructor; do not call `load_parser_config()` / `ipa_mappings_dict()` against `data/`.
- `test_group_mappings.py` / compile tests using `asca_group_mappings_dict()` — pass explicit `group_mappings={...}` dict with only keys the test needs.

### `default_index_parser` helper

Refactor `tests/helpers.py` so `default_index_parser()` does **not** cache `load_default_ingest_tables()`. Options (pick one, document in PR):

- **A)** Empty defaults: `ParserConfig()` + empty mapping lists/dicts (tests that need mappings pass overrides).
- **B)** Small shared fixture module `tests/fixtures/minimal_mappings.py` with stable inline rows reused across tests (not read from `data/`).

Prefer **B** if many integration tests need the same handful of IPA/feature rows; prefer **A** if overrides are per-test anyway.

### Do not

- Move config files or change `src/conlanger` loading behavior (that is ticket 101).
- Remove tmp_path loader coverage.
- Change inventory baseline or run `create_index` as a gate (test-only ticket).

## Acceptance criteria

- [x] No test calls `load_*_mappings()`, `load_parser_config()`, `load_compiler_config()`, `feature_mappings_dict()`, `ipa_mappings_dict()`, or `asca_group_mappings_dict()` **without** an explicit `tmp_path` path or inline constructor args — except tmp_path loader tests may use those functions with a fixture path.
- [x] No test asserts specific values from the production `data/parser_config.yml`, `data/compiler_config.yml`, or `data/**/*.csv` mapping files.
- [x] `uv run pytest` passes; ruff clean on touched test files.
- [x] Ticket 101 unblocked (remove `Blocked by: 102` on 101 when this resolves).

## Answer

Introduced `tests/fixtures/minimal_mappings.py` with inline parser/compile mapping fixtures. `default_index_parser()` now wires those instead of `load_default_ingest_tables()`. Removed seven production-seed assertion tests; refactored transform and integration tests to use minimal fixtures or `tmp_path` loader paths. Unblocked ticket 101.

## Related

- [101 refactor config layout and injection](101-refactor-config-layout-and-injection.md) — blocked on this ticket
