Type: task
Status: resolved
Blocked by:

# Docs: parse → compile → validate (three stages)

Grill 2026-08-21 Q7 / [ADR-0013](../../../docs/adr/0013-parse-compile-validate.md). Living pipeline docs list **three** stages. Inventory and `uv run create_index` sit under **validate**, not a fourth “applier-neutral index validation” stage. Hold-out language matches Q5 / [ADR-0010 amendment](../../../docs/adr/0010-historical-fidelity-class-first-status.md): `status: skipped` only from `skip_sections` / `skip_rules`.

## What to build

- `docs/SYSTEM.md` **Pipeline stages (new)**: three rows — parse, compile, validate. Fix the current `parse → validate → compile` wording.
- Stage docs: keep parse and compile pages; fold [applier-neutral-index-validation.md](../../../docs/applier-neutral-index-validation.md) into the validate section (redirect or merge). Inventory, correction loop, CSVs live there.
- Cross-links in parser/compile docs, `CONTEXT.md` documentation list if needed, `.scratch/cleaned-rule-index/spec.md` stage count (do not rewrite the whole spec).
- Skip field names: `status: skipped` only; no `skip: true` / `skipped: true`. Compile-time chain expansion only (no living parse-time chain-split).
- History of `input`/`output` → **stages** stays in [ADR-0011](../../../docs/adr/0011-index-rule-stages.md) / [ticket 59](59-index-rule-stages-schema.md).

## Out of scope

- Code changes ([tickets 89](89-unify-status-skipped.md) / [90](90-missing-arrow-single-stage.md) / [93](93-pydantic-compile-refactor.md))
- Implementing pydantic

## Acceptance criteria

- [x] No living doc treats inventory as an applier-neutral stage
- [x] SYSTEM.md and stage docs agree on parse → compile → validate
- [x] Skip policy in those docs matches config-only `status: skipped`
