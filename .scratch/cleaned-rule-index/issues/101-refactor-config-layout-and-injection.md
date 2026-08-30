Type: task
Status: ready-for-agent

# Refactor config layout, YAML migration, and dependency injection

Owner proposal (2026-08-30): relocate mapping tables and runtime config under `./config/`, convert CSV mapping tables to YAML, and stop package code (everything under `src/conlanger` except `src/conlanger/scripts`) from loading config files at runtime. Parser and compiler accept only in-memory config objects; when omitted, use **empty** config instances. Only `src/conlanger/scripts` reads `./config/` and wires real YAML into config classes. `create_index.py` becomes the single bootstrap point composing one `ParserConfig` and one `CompilerConfig`.

**Blocked by** [102 remove production config test assertions](102-remove-production-config-test-assertions.md) — land test cleanup first for like-for-like regen comparison.

Spawned from [Cleaned rule index SoT](../map.md) (`data/` tree note) and owner `/grill-with-docs` session.

## Problem

Today mapping tables and YAML settings live under `data/` (mixed with corpus artifacts), and library code silently falls back to disk:

- `src/conlanger/utils/file_io.py` — `load_parser_config()`, `load_compiler_config()`, `load_*_mappings()`, `load_default_ingest_tables()` with hard-coded `data/` defaults.
- `DiachronicSeries` (`rules.py`) calls `load_compiler_config()` when `compiler_config=None`.
- `compile_asca_rule_fields` / pipeline (`pipeline.py`) same fallback.
- `asca_group_mappings_dict()` (`group_mappings.py`) loads `data/asca/group_mappings.csv`.
- Tests (`tests/helpers.py` `default_index_parser()`, many `test_parser.py` / `test_compiler_config.py` cases) load real package config files and assert on production contents (e.g. PIE laryngeals, section-mapping seeds).

This couples the library to repo paths, makes unit tests depend on production config drift, and splits config across CSV + YAML without a clear boundary between **corpus data** (`data/diachronica/…`) and **operator config** (`config/…`).

## Target layout

| Current path | New path | Format |
| --- | --- | --- |
| `data/asca/group_mappings.csv` | `config/compile/asca/group_mappings.yml` | YAML (dict keyed by `grouping`) |
| `data/asca/feature_mappings.csv` | `config/parser/feature_mappings.yml` | YAML (dict keyed by `index_feature`) |
| `data/compiler_config.yml` | `config/compile/asca/compiler_config.yml` | YAML (schema unchanged) |
| `data/common/manual_mappings.csv` | `config/parser/manual_mappings.yml` | YAML (**list** of records — order matters) |
| `data/common/ipa_mappings.csv` | `config/parser/ipa_mappings.yml` | YAML (dict keyed by `index_feature`) |
| `data/parser_config.yml` | `config/parser/parser_config.yml` | YAML (schema unchanged) |
| `data/diachronica/index_diachronica_corrections.yml` | `config/parser/index_diachronica_corrections.yml` | YAML (schema unchanged) |

**Stays in `data/`**: `index_diachronica_original.html`, regenerated `index_diachronica_parsed.yml`, `data/asca/asca_aliases.alias`, test fixtures, inventory outputs.

**Future note (out of scope):** owner intends to split the parse/compile pipeline in two once cleaned YAML is SoT; this ticket only relocates config and enforces injection.

## Design requirements (owner)

1. **No file I/O in library code** — remove config-path loading and default-path fallbacks from `src/conlanger` except `src/conlanger/scripts`. Parser/compiler/pipeline/`DiachronicSeries` accept config objects only; `None` → empty instances.
2. **Composition root in `create_index.py`** — one `ParserConfig` and one `CompilerConfig`, each built from loaded sub-configs (see Answer).
3. **Scripts-only loaders** — thin YAML loaders in `src/conlanger/scripts/config_loaders.py`:
   - `load_parser_config(path: Path | None = None) -> ParserConfig`
   - `load_compiler_config(path: Path | None = None) -> CompilerConfig`
   - Each reads YAML → plain dict/list → splats into Pydantic config constructors where practical. `create_index.py` orchestrates both loads + composition.
4. **Tests** — no unit tests that read `./config/` and assert production contents. Loader tests in `tests/conlanger/scripts/test_config_loaders.py` use `tmp_path` fixture YAML. Config-class behaviour tests use inline construction in package tests.
5. **`sample_asca_guess_fixtures.py`** — same bootstrap as `create_index.py`.
6. **CSV → YAML** — mechanical migration; preserve `manual_mappings` `use_regex` field. YAML shape is implicit — validation on Pydantic config classes.
7. **Hard gate** — full `uv run create_index` (with validation) must match pre-refactor inventory baseline.

## Config class shape (resolved)

### `ParserConfig` (Pydantic `BaseModel`)

Fat config; `IndexDiachronicaParser` takes **only** `ParserConfig`.

| Field | Type | Notes |
| --- | --- | --- |
| `manual_mappings` | `list[ManualMapping]` | from `manual_mappings.yml` (list, ordered) |
| `ipa_mappings` | `tuple[IpaMapping, ...]` | from `ipa_mappings.yml` |
| `ipa_mappings_confidence` | `frozenset[str] \| None` | from `parser_config.yml`; see IPA rules below |
| `feature_mappings` | `dict[str, FeatureMapping]` | from `feature_mappings.yml` |
| `corrections` | `dict[str, str]` | from `index_diachronica_corrections.yml` |
| `series_expansions` | `dict[str, tuple[str, ...]]` | unchanged |
| `section_mappings_sections` | `dict[str, dict[str, str]]` | from `section_mappings` in parser_config |
| `skip_section_ids` / `skip_rule_ids` / `skip_rule_comments` | unchanged | |

**`resolved_ipa_mappings() -> dict[str, str]`** (replaces package `ipa_mappings_dict()`):

- `ipa_mappings_confidence is None` → include **every** row with a non-empty `ipa_target`, regardless of row `confidence`.
- `ipa_mappings_confidence` is a frozenset → include row only if `row.confidence` is in the set; rows with `confidence=None` (absent in YAML) are **excluded** (invalid / non-matching), same spirit as today where `"" not in {"high","medium"}`.

Production `parser_config.yml` keeps explicit `confidence: [high, medium]` so scripts-loaded behavior matches current regen when filter is active.

### `CompilerConfig` (Pydantic `BaseModel`)

| Field | Type | Notes |
| --- | --- | --- |
| `group_mappings` | `dict[str, str]` | from `group_mappings.yml` (`grouping` → `mapping`) |
| `series_mappings_global` | `dict[str, str]` | unchanged |
| `series_mappings_sections` | `dict[str, dict[str, str]]` | unchanged |

`DiachronicSeries(section, compiler_config=…)` — drop separate `group_mappings=` arg; pipeline reads `compiler_config.group_mappings`.

## Implementation sketch

### Package (`src/conlanger`)

- Migrate `ParserConfig` / `CompilerConfig` to Pydantic; add composed fields and `resolved_ipa_mappings()`.
- `IndexDiachronicaParser(parser_config: ParserConfig)` only.
- Remove disk fallbacks from `rules.py`, `pipeline.py`, `group_mappings.py`.
- Delete `load_default_ingest_tables`, path constants, CSV mapping loaders from `file_io.py` (keep inventory CSV helpers).
- Delete `ipa_mappings_dict`, `feature_mappings_dict`, `asca_group_mappings_dict()` file loaders from package.

### Scripts

- `config_loaders.py` — `load_parser_config()`, `load_compiler_config()` as separate entry points.
- `create_index.py` — load all fragments from `config/`, compose single `ParserConfig` + `CompilerConfig`, pass through pipeline.

### Docs (in scope)

Update living docs: `map.md`, `docs/*.md`, `CONTEXT.md` path references, ADR-0012/0004 paths. Do **not** rewrite closed historical tickets.

## Acceptance criteria

- [ ] All seven config artifacts under `config/` as YAML; legacy mapping CSVs and top-level `data/parser_config.yml` / `data/compiler_config.yml` removed.
- [ ] No config file loading under `src/conlanger` outside `scripts/`.
- [ ] `IndexDiachronicaParser` / compile pipeline run with empty configs without disk I/O.
- [ ] Full `uv run create_index` inventory-equivalent to pre-refactor baseline.
- [ ] Loader tests in `tests/conlanger/scripts/test_config_loaders.py`; no production config assertions in package tests.
- [ ] Full quality gate passes.

## Related

- [102 remove production config test assertions](102-remove-production-config-test-assertions.md) — **must land first**
- [Implement compiler_config.yml series mappings](75-implement-compiler-config-series-mappings.md)
- [Implement parser_config section_mappings](97-implement-parser-config-section-mappings.md)
- [ADR-0012 Index Diachronica corrections overlay](../../../docs/adr/0012-index-diachronica-corrections-overlay.md)

## Answer

Grill resolved 2026-08-30.

### Round 1

| # | Decision |
| --- | --- |
| Q1 | **A** — `feature_mappings.yml` under `config/parser/`. |
| Q2 | **A** — fat `ParserConfig`; parser takes only `ParserConfig`. |
| Q3 | **A** — fat `CompilerConfig` with `group_mappings`; drop separate `group_mappings=` on `DiachronicSeries`. |
| Q4 | Optional `ipa_mappings_confidence`; `None` = apply all rows (behavior change vs historical default when unset). |
| Q5 | **C** — dict-keyed mapping YAML except manual_mappings (list). |
| Q6 | **A** — `scripts/config_loaders.py`. |
| Q7 | Thin loaders + Pydantic validation; loader tests under `tests/conlanger/scripts/`. |
| Q8 | **A** — corrections in `config/parser/`, embedded in `ParserConfig`. |
| Q9 | Full `uv run create_index` hard gate. |

### Round 2

| # | Decision |
| --- | --- |
| Q10 | `ipa_mappings_confidence` omitted/`None` → apply all IPA rows. When provided (frozenset), filter by row `confidence`; row `confidence=None` → excluded (invalid). Empty list `[]` → explicit empty filter (no rows). **Today:** `row.confidence in confidences` with CSV `confidence` column required — empty string excluded when filter active; same spirit as `None` under filter. |
| Q11 | **A** — `tuple[IpaMapping, ...]` + `resolved_ipa_mappings()` on config. |
| Q12 | **A** — `manual_mappings.yml` is list-of-records (order preserved). |
| Q13 | **B** — Pydantic `BaseModel` for config classes. |
| Q14 | Update `map.md`, `docs/`, `CONTEXT.md`, ADRs; not closed historical tickets. |
| Q15 | **B** — separate `load_parser_config()` and `load_compiler_config()` in `config_loaders.py`; scripts orchestrate. |
| Q16 | **A** — delete package `ipa_mappings_dict()`; use `ParserConfig.resolved_ipa_mappings()`. |

### Follow-on (owner)

Pre-refactor test cleanup filed as [102](102-remove-production-config-test-assertions.md); 101 blocked until 102 resolves.

## Comments

### 2026-08-30 — grill-with-docs complete

Round 1–2 answers recorded; status `ready-for-agent`, blocked by 102.
