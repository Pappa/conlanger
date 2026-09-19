Type: task
Status: resolved
Blocked by:

# Inventory success/error CSV splits and ok-change changelog

## Question

How should `uv run create_index` extend the validation inventory so regressions in **compile validation** are easy to spot — without changing what counts as a valid rule?

## Decision (charted)

Extend [Full-index validation inventory](12-full-index-validation-inventory.md) artifacts under `.scratch/rule-index/inventory/`:

1. **Filtered views** (same columns as `rule-inventory.csv`, rewritten each regen):
   - `rule-inventory-success.csv` — rows with `ok=True`
   - `rule-inventory-error.csv` — rows with `ok=False`
2. **Changelog of `ok` flips only** (append-only across runs):
   - Columns: `section_index`, `rule_idx`, `source`, `ok`, `timestamp`
   - `timestamp` is identical for every row written in a given regeneration run
   - Emit a row only when a rule’s `ok` value **changed** vs the previous inventory (`True→False` or `False→True`)
   - Match rules primarily by `source` (HTML `file:line`) so chain-split / `rule_idx` renumbering does not false-alarm; keep `section_index`/`rule_idx` for human context
   - Filename: e.g. `rule-inventory-changelog.csv` (confirm at implement)

Out of scope for this ticket: field-isolation validation; tagging “transform-exempt” bare I/O rules; changing `validate_asca` itself.

## Acceptance criteria

- [x] Regen writes success + error filtered CSVs alongside the full inventory
- [x] Regen appends changelog rows only for `ok` flips, with a shared run `timestamp`
- [x] First run (no prior inventory) does not invent flip rows (or documents empty-changelog behaviour)
- [x] Summary markdown mentions the new artifacts
- [x] Tests cover flip detection by `source` and no-op when `ok` unchanged

## References

- `src/conlanger/scripts/create_index.py`
- `src/conlanger/tools/index_inventory.py`
- Map grilling 2026-08-06 (Q1–Q3)

## Answer

`uv run create_index` now loads the prior `rule-inventory.csv` (if any), then writes:

- `rule-inventory.csv` (full, rewritten)
- `rule-inventory-success.csv` / `rule-inventory-error.csv` (filtered views, rewritten)
- `rule-inventory-changelog.csv` (append-only `ok` flips matched by `source`; shared UTC `timestamp` per run; no rows when there is no prior inventory or `ok` is unchanged)

Helpers live in `index_inventory.py` (`filter_inventory_by_ok`, `ok_flip_changelog_rows`, …). Summary Notes link the new files. Validity criteria unchanged.
