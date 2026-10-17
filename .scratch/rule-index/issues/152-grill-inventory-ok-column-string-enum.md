Type: grilling
Status: resolved
Blocked by: None

# Grill: inventory `ok` column string enum (`FAILED` / `OK` / `SKIPPED`)

Spawned from wayfinder session 2026-10-17. Owner input: replace numeric **`ok`** values **`0`**, **`1`**, **`2`** in validation inventory code with strings **`FAILED`**, **`OK`**, **`SKIPPED`** (`index_inventory.py`: `OK_FALSE`, `OK_TRUE`, `OK_SKIPPED`, `_coerce_ok_column`, field-isolation `whole_ok`).

## Question

Lock the **CSV and summary contract** for human and downstream tooling: string enum only vs transitional coercion, column names unchanged, and whether **field-isolation** and **changelog** rows use the same literals.

## Answer

Grill closed 2026-10-17 (owner agreed to all frontier questions).

| # | Decision |
| --- | --- |
| 1 | Literals: **`FAILED`**, **`OK`**, **`SKIPPED`**. |
| 2 | **Write:** strings only on new inventory CSV output (`ok`, `whole_ok`). |
| 3 | **Read:** coerce legacy `0`/`1`/`2` (and bool) when loading prior CSVs for changelog / comparison. |
| 4 | Column names **`ok`** / **`whole_ok`** unchanged. |
| 5 | Field-isolation and changelog use the **same** three literals. |
| 6 | **`SKIPPED`** replaces numeric `2`; `rule_skipped` / `section_skipped` failure classes unchanged. |
| 7 | **`ValidationRow.ok`** (and related code) use string enum end-to-end; ints only at CSV read coercion. |

**Implementation:** ~~[157 task](157-task-inventory-ok-column-string-enum.md)~~ **resolved** (2026-10-17).

## Topics

- **Backward compatibility** — accept legacy `0`/`1`/`2` on read for one release?
- **Pandas / cluster scripts** — any repo or `.scratch` analytics assuming ints?
- **Failure class** rows — `section_skipped` / `rule_skipped` still pair with `SKIPPED`?
- **Tests and fixtures** — golden CSV updates.

## Deliverable

Enum names (confirm `FAILED` not `FAIL`), write policy, read policy; implementation is a small **task** once locked.

## Comments

- 2026-10-17: Grill round 1 — owner agreed to all Q1–Q7; filed [157](157-task-inventory-ok-column-string-enum.md).
