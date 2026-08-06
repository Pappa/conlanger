Type: task
Status: ready-for-agent
Blocked by:

# Inventory success/error CSV splits and ok-change changelog

## Question

How should `uv run regenerate_corpus` extend the validation inventory so regressions in **compile validation** are easy to spot — without changing what counts as a valid rule?

## Decision (charted)

Extend [Full-corpus validation inventory](12-full-corpus-validation-inventory.md) artifacts under `.scratch/cleaned-rule-corpus/inventory/`:

1. **Filtered views** (same columns as `asca-rule-inventory.csv`, rewritten each regen):
   - `asca-rule-inventory-success.csv` — rows with `ok=True`
   - `asca-rule-inventory-error.csv` — rows with `ok=False`
2. **Changelog of `ok` flips only** (append-only across runs):
   - Columns: `section_index`, `rule_idx`, `source`, `ok`, `timestamp`
   - `timestamp` is identical for every row written in a given regeneration run
   - Emit a row only when a rule’s `ok` value **changed** vs the previous inventory (`True→False` or `False→True`)
   - Match rules primarily by `source` (HTML `file:line`) so chain-split / `rule_idx` renumbering does not false-alarm; keep `section_index`/`rule_idx` for human context
   - Filename: e.g. `asca-rule-inventory-changelog.csv` (confirm at implement)

Out of scope for this ticket: field-isolation validation; tagging “transform-exempt” bare I/O rules; changing `validate_asca` itself.

## Acceptance criteria

- [ ] Regen writes success + error filtered CSVs alongside the full inventory
- [ ] Regen appends changelog rows only for `ok` flips, with a shared run `timestamp`
- [ ] First run (no prior inventory) does not invent flip rows (or documents empty-changelog behaviour)
- [ ] Summary markdown mentions the new artifacts
- [ ] Tests cover flip detection by `source` and no-op when `ok` unchanged

## References

- `src/conlanger/scripts/regenerate_corpus.py`
- `src/conlanger/tools/corpus_inventory.py`
- Map grilling 2026-08-06 (Q1–Q3)
