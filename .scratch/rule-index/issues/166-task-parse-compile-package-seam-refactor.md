Type: task
Status: done
Blocked by: 150

# Task: refactor parse vs compile package seams (grill 150)

## Goal

Align `src/conlanger/` imports with the four top-level areas: **ingest** (parse), **compile** (compile), **utils** (shared), **tools** (inventory / operator helpers). Remove **ingest → compile** imports.

## Checklist (from [150 Answer](150-grill-parse-compile-module-seams.md#answer))

- [x] Move `resolve_rule_env_exception_for_compile`, `merge_medial_boundary_exception`, and compile rule-level resolver into `compile/` (extend `resolve_index_rule.py` or `compile/project_index_context.py`).
- [x] Add `ingest/utils/index_context_project.py` with applier-neutral `project_index_context()`; use in `section_policy.py` (replace `resolve_index_context_to_string` import from `index_models`).
- [x] Strip `index_models.py` to Pydantic + parse lifecycle only; re-export from `ingest/__init__.py` only if needed for public API.
- [x] Move `strip_editorial_in_before_syllable_position` to `ingest/utils/syllable_position.py`; update `transforms.py` and compile syllable module to import from ingest or utils per 150 table.
- [x] Move `compile/tools/bracket_scanner.py` → `conlanger/utils/bracket_scanner.py`; fix imports in compile and `ingest/utils/flatten_nested_sets.py`.
- [x] Move `CompilerConfig` + `PositionTemplates` to `compile/models/config.py` (or `compile/config.py`); keep `ParserConfig` + parse `normalize_*` in `ingest/models/mappings.py` (rename file optional).
- [x] Update `config_loaders.py`, scripts, and tests; run full quality gate.
- [x] One-line note in `docs/system/index-diachronica-parser.md` / compile doc: allowed import directions.

## Out of scope

- Behaviour changes to env projection (162/163/164/165 own that).
- Splitting `tools/` beyond import fixes tied to this seam work.
