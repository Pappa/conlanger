Type: task
Status: resolved
Blocked by: None

# Implement compile-field intermediate representation (field tokens)

Spec: [ticket 94 Answer](94-grill-structured-soundchangerule-ir.md). ADR: [0015](../../../docs/adr/0015-compile-field-intermediate-representation.md).

Replace string-gated alternative detection and ad-hoc splits with an ordered **field-token** intermediate representation on pydantic compile-field types at `SoundChangeRule` construction.

## Spec (grill 94)

- **Compile-field types:** `RuleInput`, `RuleOutput`, `RuleEnv` (exception reuses `RuleEnv`). Each holds Index-raw, field-token tuple, and compiled ASCA string.
- **Field token:** singleton opaque string **or** ordered brace-set members (tuple/list — not Python `set`).
- **Parse timing:** inside `compile_rule` — parse Index-raw to field tokens before alternatives and compile; write compiled ASCA back to the field object.
- **Alternatives:** detect on field-token structure (optional outputs + parallel-∅); fan-out to peer `SoundChangeRule` instances unchanged ([ticket 92 Q10](92-grill-pydantic-compile-refactor.md)).
- **Parallel tokens:** zip input/output field-token tuples at rule level ([tickets 60](60-correction-pass-parallel-column-null.md), [81](81-correction-pass-parallel-output-null.md)).
- **Optional-length `(ː)`:** optional-length node → ordered alternation before suffix `length_marks`; unblocks [104](104-correction-pass-parenthesized-optional-length-marker.md) (may land in same PR or immediately after).
- **Transforms (hybrid v1):** walk field tokens for structural paths; legacy string transforms may stringify → existing `compile/asca/` function → reparse until ported.
- **Render:** field object renders tokens → compiled string; `__str__` joins four compiled strings.
- **Tests:** field-token structure + alternative fan-out unit tests; golden `.rsca` on representative rules.

## Out of scope

- Ticket 71 optional-prefix parallel shapes (stay on string layer until v2)
- Full recursive syntax tree for all Index notation
- Index YAML shape changes
- Brassica compiler

## Acceptance criteria

- [x] `RuleInput` / `RuleOutput` / `RuleEnv` with raw + tokens + compiled
- [x] Alternative detection uses field-token gates (66, 81)
- [x] Parallel null drop (60) operates on field tokens
- [x] Optional-length node policy per grill 94 Q6 (landed with [104](104-correction-pass-parenthesized-optional-length-marker.md))
- [x] Golden `.rsca` unchanged except documented cases in **Answer**
- [x] Structure tests for token shape and fan-out
- [x] Full gate: `uv run pytest`; `uv run per_file_coverage_gate`; ruff

## References

- [Grill: structured compile intermediate representation](94-grill-structured-soundchangerule-ir.md)
- [Store compiled fields; join at render](99-compiled-fields-join-at-render.md)
- [Correction pass: parenthesized optional length `(ː)`](104-correction-pass-parenthesized-optional-length-marker.md)

## Answer

Field-token IR shipped per [ADR-0015](../../../docs/adr/0015-compile-field-intermediate-representation.md):

- `src/conlanger/tools/compile/field_tokens.py` — `FieldToken`, `OptionalLengthNode`, parse/render, optional-output shape gate
- `src/conlanger/tools/compile/compile_fields.py` — `RuleInput` / `RuleOutput` / `RuleEnv` (raw + tokens + compiled)
- `src/conlanger/tools/rules.py` — alternatives and parallel fan-out read field tokens
- `src/conlanger/tools/compile/asca/parallel.py` — parallel null drop and branch expansion on tokens
- `src/conlanger/tools/compile/asca/optional_length.py` — optional-length node expansion (consumed by [104](104-correction-pass-parenthesized-optional-length-marker.md))
- `tests/conlanger/tools/compile/test_field_tokens.py` — structure, fan-out, and optional-output gate tests

**Render changes:** None beyond [104](104-correction-pass-parenthesized-optional-length-marker.md) optional-length policy (documented there).
