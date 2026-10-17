Type: task
Status: resolved
Blocked by: None

## Resolution (2026-10-17)

- Parse `normalize_symbols` now only rewrites Index stress (`”` → postfix `[+stress]`); `%` / stem `$` stay in SoT.
- ASCA compile runs `project_index_syllable_stem_symbols` at the start of `compile_asca_field_pre_subscript` (before group mappings; `%ː` held for `normalize_asca_length_marks`).
- Regen: `uv run create_index` — env/stages with syllable `%` no longer pre-normalized to ASCA `$` in YAML (e.g. `_$%oː` not `_$$oː`). Compiled ASCA unchanged for those rules. Re-run `compile_rules` / `validate_rules` when refreshing inventory.

# Task: atomic migration of syllable/stem symbols to ASCA compile

Spawned from [Grill: ASCA-shaped syntax in the applier-neutral rule index](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) (2026-10-17).

## Question

Move Index **`%`** (syllable boundary) and stem **`$`** handling out of parse-time `normalize_symbols()` into ASCA **compile**, in **one** change set with full impact review (acceptance per ticket 148).

## Acceptance

- SoT keeps Index `%` and `$`; no syllable `%` → ASCA `$` at parse.
- ASCA compile applies syllable/stem projection before or as part of existing symbol steps.
- All unit tests, fixtures, and docs that assumed ASCA `$` in parsed YAML updated.
- Regen impact summarized (inventory/changelog); breaking regen expected.

## Out of scope

- Stress mark rewrite (separate: postfix `[+stress]` at parse).
- `position.in` compile projection ([156](156-task-indexcontext-position-in-relation.md)); broader parse-time ASCA env cleanup → [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md).
