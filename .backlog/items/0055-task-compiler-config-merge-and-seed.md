Type: task
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Layer CompilerConfig from class defaults, YAML, and CLI; optional compile seed in config.
Blocked by:

## Problem Statement

`load_compiler_config` treats missing YAML keys as **`false`** for `sample_sporadic` / `sample_dialect`, which disagrees with [`CompilerConfig`](../../src/conlanger/compile/models/config.py) field defaults. Compile RNG is hard-coded as `INVENTORY_COMPILE_RNG_SEED` in code instead of operator config. Downstream work ([0054](0054-task-compile-rules-sample-mode-v4-schema.md)) needs a single, documented precedence chain for scalar compile settings and for an optional seed.

## Description

Introduce a dedicated merge path when building a `CompilerConfig` for compile operations:

**Precedence (low → high):**

1. **Pydantic defaults** on `CompilerConfig` (and nested defaults where applicable).
2. **YAML** — still load `group_mappings` from `config/compile/asca/group_mappings.yml` and series maps from the chosen compiler package YAML (default [`compiler_config.yml`](../../config/compile/asca/compiler_config.yml)); scalar keys in that file override defaults only when present.
3. **CLI** — on `compile_rules` (and any shared helper), accept overrides for **scalar** fields only: booleans, numbers, strings that map to top-level `CompilerConfig` fields (not nested dicts like `series_mappings`).

**`seed`**

- Add optional `seed: int | None` to `CompilerConfig` (default **`None`** = unseeded `random.Random()` for compile).
- Allow `seed` in the same compiler YAML file; document in config comments.
- Set **`seed: 0`** in committed [`config/compile/asca/compiler_config.yml`](../../config/compile/asca/compiler_config.yml) so validate/diagnostics compile stays reproducible today.
- Remove **`INVENTORY_COMPILE_RNG_SEED`** and all uses; thread `compiler_config.seed` into `DiachronicSeries` / `resolve_inventory_targets` / [`compiled_rules_yaml.py`](../../src/conlanger/tools/compiled_rules_yaml.py) `_skipped_rule_line` via one helper (e.g. `rng_for_compile_config(config) -> random.Random`).
- Optional CLI flag (e.g. `--seed`) overrides YAML when passed; omitting CLI and omitting YAML `seed` ⇒ **no** fixed seed.

**Loader refactor**

- Replace `raw.get("sample_sporadic", False)`-style defaults in [`config_loaders.py`](../../src/conlanger/scripts/config_loaders.py) with merge-into-model behaviour (`CompilerConfig.model_validate({...})` or equivalent) so absent YAML keys keep class defaults.
- Keep `sample_sporadic: false` / `sample_dialect: false` in committed asca `compiler_config.yml` so validate behaviour unchanged after the loader fix.

**Out of scope for this ticket**

- `config/pipeline/compiler_config.yml` (follow-up with 0054 / pipeline compile mode).
- `enumerate_compile_targets` / sample vs fan-out output.
- v4 `asca_rules.yml` schema.

## Acceptance Criteria

- [x] Building config with an **empty** YAML dict (only sidecar mappings loaded) yields `sample_sporadic=True`, `sample_dialect=True`, and `seed=None` unless tests inject overrides.
- [x] Committed `compiler_config.yml` with `sample_sporadic: false`, `sample_dialect: false`, and `seed: 0` loads to those values.
- [x] `compile_rules` CLI scalar override wins over YAML (test at least one boolean and `seed`).
- [x] `INVENTORY_COMPILE_RNG_SEED` is removed; grep clean in `src/` and `tests/`.
- [x] Two compile runs with the same index and `seed: 0` in config produce identical stochastic choices; with `seed` omitted (and no CLI seed), two runs **may** differ (smoke test optional).
- [x] [`validate.md`](../../docs/system/validate.md) mentions compile seed lives in `compiler_config.yml` (not the removed constant).
- [x] `uv run check` passes.

## Comments