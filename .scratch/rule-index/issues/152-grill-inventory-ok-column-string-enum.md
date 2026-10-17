Type: grilling
Status: needs-grilling
Blocked by: None

# Grill: inventory `ok` column string enum (`FAILED` / `OK` / `SKIPPED`)

Spawned from wayfinder session 2026-10-17. Owner input: replace numeric **`ok`** values **`0`**, **`1`**, **`2`** in validation inventory code with strings **`FAILED`**, **`OK`**, **`SKIPPED`** (`index_inventory.py`: `OK_FALSE`, `OK_TRUE`, `OK_SKIPPED`, `_coerce_ok_column`, field-isolation `whole_ok`).

## Question

Lock the **CSV and summary contract** for human and downstream tooling: string enum only vs transitional coercion, column names unchanged, and whether **field-isolation** and **changelog** rows use the same literals.

## Topics

- **Backward compatibility** — accept legacy `0`/`1`/`2` on read for one release?
- **Pandas / cluster scripts** — any repo or `.scratch` analytics assuming ints?
- **Failure class** rows — `section_skipped` / `rule_skipped` still pair with `SKIPPED`?
- **Tests and fixtures** — golden CSV updates.

## Deliverable

Enum names (confirm `FAILED` not `FAIL`), write policy, read policy; implementation is a small **task** once locked.
