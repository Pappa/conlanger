Type: task
Status: ready-for-agent
Blocked by: None

# Task: inventory `ok` / `whole_ok` string enum (`FAILED` / `OK` / `SKIPPED`)

Spawned from [Grill: inventory `ok` column string enum](152-grill-inventory-ok-column-string-enum.md) (resolved 2026-10-17).

## Question

Implement the inventory outcome contract locked in grill 152: replace numeric **`0` / `1` / `2`** with **`FAILED` / `OK` / `SKIPPED`** in validation inventory code and emitted CSVs.

## Answer (from 152)

| Topic | Policy |
| --- | --- |
| Literals | **`FAILED`**, **`OK`**, **`SKIPPED`** (not `FAIL`). |
| Write | New regen writes **strings only** in `ok` and `whole_ok` columns. |
| Read | Coerce legacy `0`/`1`/`2` (int/float/bool) when **reading** existing CSVs for changelog / diff; map to string enum internally. |
| Column names | Unchanged: `ok`, `whole_ok`. |
| Field-isolation + changelog | Same three literals in `whole_ok` and changelog `ok` columns. |
| Skipped semantics | `SKIPPED` replaces `2`; `rule_skipped` / `section_skipped` failure classes and descriptions unchanged. |
| In-memory model | `ValidationRow.ok` (and helpers) use string enum / `StrEnum` — no int `0`/`1`/`2` in Python comparisons. |

## Acceptance

- [ ] `index_inventory.py`: rename/replace `OK_FALSE`/`OK_TRUE`/`OK_SKIPPED` with string constants; update `_coerce_ok_value`, filters, summary counts, field-isolation blame.
- [ ] Regenerated `diagnostics/inventory/*.csv` use string `ok` / `whole_ok`; run `uv run validate_rules` after change.
- [ ] Changelog flip detection works against prior numeric **or** string CSVs (read coercion).
- [ ] Tests in `tests/conlanger/tools/test_index_inventory.py`, `test_validate_rules.py` updated.
- [ ] `docs/system/validate.md` documents string enum (not `ok=True`/`False` prose for CSV cells).
- [ ] Audit `.scratch/rule-index/research/scan_*.py` (and any other inventory consumers) for `ok` assumptions; fix or note in ticket Answer.

## Related

- [152 grill](152-grill-inventory-ok-column-string-enum.md)
- [34 inventory CSV splits](34-inventory-success-error-splits-and-ok-changelog.md)
- [36 field-isolation blame](36-per-field-asca-blame-in-inventory.md)
