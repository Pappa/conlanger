Type: task
Status: ready-for-agent
Blocked by: 92

# Refactor compile classes to pydantic (per-field transforms)

Spec: [ticket 92 Answer](92-grill-pydantic-compile-refactor.md). ADR: [0014](../../../docs/adr/0014-per-field-asca-compile.md).

Re-implement `src/conlanger/tools/rules.py` as **pydantic** `BaseModel`s (**latest** pydantic 2.x — `uv add pydantic` when claiming; owner approved). Keep the name **`DiachronicSeries`**. Transforms run on **input / output / env / exception separately at instantiation**; join is render-time.

## Spec (grill 92)

- **Models:** `RulePartBase`, `RuleTitle`, `RuleCitation`, `RuleComment`, `SoundChangeRule`, `DiachronicSeries` — all `BaseModel`. Title/citation/comment: format only, no compile validators.
- **Pure functions** stay in `compile/asca/`; pydantic `field_validator` / `model_validator` call them (Q3: may change later).
- **Per-field** pipeline on the four compile fields (`field_validator`). Spike-38 **order** still applies per field.
- **Cross-field:** `model_validator(mode='after')` for subscript refs (shared `declared`, **output last**).
- **Alternatives** stay on `SoundChangeRule`: detect on **raw** I/O (`_build_alternatives` gates as pure functions), compile each peer, parent RNG-picks one emitted line. Inventory still reads `.alternatives`. Do not hoist to `DiachronicSeries`. Do not add a corpus YAML field.
- **Join** only at `__str__` / render. Remove join-then-rewrite `compile_asca_rule_string`.
- **Chains** on `DiachronicSeries` (`stages` → adjacent pairs). `SoundChangeRule` does not read `stages`. Length-1 → `output=""` ([ticket 90](90-missing-arrow-single-stage.md)).
- **Injection:** `PrivateAttr` for `group_mappings`, `compiler_config`, `section_index`, instance `Random`.
- **Skip:** `status: skipped` → comment `#\t` + `raw`; skip compile validators ([ticket 89](89-unify-status-skipped.md)).
- **ASCA-only** (no Brassica compiler).
- **Tests:** prefer byte-identical `.rsca`. If any `DiachronicSeries` / `SoundChangeRule` **unit-test input/output strings** change, list each in this ticket’s **Answer** with description and justification.

## Out of scope

- Brassica compiler
- Changing corpus YAML (`stages` stays parse SoT)
- Renaming `DiachronicSeries`
- Re-ordering transforms contrary to [spike 38](../research/asca-compile-transform-order.md)
- Structured column/set IR on `SoundChangeRule` — [ticket 94](94-grill-structured-soundchangerule-ir.md) (grill after this lands)

## Acceptance criteria

- [x] `uv add pydantic` (latest 2.x at claim time) — pydantic 2.13.4
- [x] Six `rules.py` types are pydantic `BaseModel`s; compile is not a post-join string pipeline
- [x] Alternatives remain on `SoundChangeRule`; chains on `DiachronicSeries`
- [x] Callers (`validate_asca`, inventory, tests, docs) updated; name stays `DiachronicSeries`
- [x] Full gate: `uv run pytest`; `uv run ruff check --fix`; `uv run ruff format && uv run ruff format --check src`
- [x] Any unit-test I/O string changes documented in **Answer** with justification

## Answer

No `DiachronicSeries` / `SoundChangeRule` unit-test input/output strings changed — all 1084 tests pass byte-identically on `.rsca` render paths.

Implementation notes:
- `compile/asca/pipeline.py`: `compile_asca_field_pre_subscript`, `compile_asca_field_post_subscript`, `compile_asca_rule_fields`, `join_asca_rule_fields`; removed `compile_asca_rule_string`.
- Cross-field subscripts via `expand_subscript_references_across_fields` in `subscript_references.py` (shared `declared`, output last).
- Spike-38 order preserved: pre-subscript per-field transforms → cross-field subscripts → post-subscript per-field transforms → join at render.
