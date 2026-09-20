Type: task
Status: ready-for-human
Blocked by: 140, 141

# Implement `IndexRule` / `IndexContext` and structured YAML emit

## Question

Introduce pydantic **`IndexRule`** (parse-time counterpart to **`SoundChangeRule`**) and emit structured **`env` / `exception`** per [141 ADR spec](141-adr-structured-env-exception-indexcontext.md), with **minimal** compile changes delegated to [144 compile resolver](144-implement-indexcontext-compile-resolution.md).

## Answer (from 139)

- Refactor `parse_rule_element` to build `IndexRule` instead of threading `dict[str, Any]`.
- Implement **index rule normalisation** step at pipeline position in [140](140-adr-parse-pipeline-order-and-raw-semantics.md).
- **`raw`** = HTML extract only; corrections on working line only.
- Parse extracts `context`, `position`, `dialect` onto `IndexContext`; neighbour / placement **projection to strings happens at compile**, not in YAML-only strings (option A).

## Acceptance

- [x] `IndexContext`, `IndexRule` in `src/conlanger/tools/ingest/` (or shared models module)
- [x] YAML round-trip tests for example shapes from 141
- [x] `uv run create_index` regen: intentional schema migration (inventory run documents delta)
- [x] Parser doc + ADRs 140/141 landed or linked

## Related

- [139 grill](139-grill-parse-indexrule-model-and-surface-normalization.md)
- [143 index rule normalisation passes](143-implement-index-rule-normalisation-passes.md)
