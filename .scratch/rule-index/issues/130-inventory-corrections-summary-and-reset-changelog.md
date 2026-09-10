Type: task
Status: ready-for-agent
Blocked by:

# Inventory: corrections summary section and reset-changelog empty file

Grill 2026-09-10 (`/grill-with-docs` on [map](../map.md)). Extends [ticket 34](34-inventory-success-error-splits-and-ok-changelog.md) changelog behaviour and [ticket 12](12-full-index-validation-inventory.md) summary markdown.

## Problem

1. **`--reset-changelog` with no flips** — `validate_rules` deletes the existing changelog, then `append_ok_flip_changelog` returns early when `flips` is empty, so no file is written. After a schema reset with unchanged `ok` values, operators lose the changelog file entirely instead of getting a header-only CSV.

2. **Corrections pass rate invisible** — `config/parser/index_diachronica_corrections.yml` holds **Index Diachronica corrections** ([ADR-0012](../../../docs/adr/0012-index-diachronica-corrections-overlay.md)). The validation inventory reports global OK/Fail/Skipped but not how many corrected rules actually validate — a key signal for correction workflow quality.

## What to build

### 1. `--reset-changelog` writes header-only CSV when there are no flips

In `validate_rules` / `index_inventory.py`:

- When `--reset-changelog` is passed:
  - Delete existing `rule-inventory-changelog.csv` if present (unchanged).
  - If `flips` is **non-empty**: write header + flip rows (unchanged).
  - If `flips` is **empty**: write `rule-inventory-changelog.csv` with `CHANGELOG_CSV_COLUMNS` header only, zero data rows.
- When `--reset-changelog` is **not** passed and `flips` is empty: leave the changelog file untouched (no append) — unchanged.

Prefer a small helper (e.g. `write_ok_flip_changelog`) over duplicating CSV logic in the script.

### 2. `## Corrections` section in `rule-inventory-summary.md`

Emit from `summarize_inventory` (or a dedicated formatter called by it). Placement: **after `## Rules`**, **before `## Failure classes`**.

**Population scope (grill Q1-B):** denominator **N** = corrections whose `rule.id` appears in the parsed index / inventory (matched overlays only). YAML entries with no matching corpus rule (`unmatched_corrections()` orphans) are **excluded** from N and from all buckets — they stay parse-time warnings only.

**Per-rule rollup (grill Q2-A):** one bucket per matched `rule_id`, aggregating all `alt_idx` inventory rows for that rule:

| Bucket | Condition |
| --- | --- |
| **OK** | every inventory row for the rule has `ok=1` |
| **Fail** | any inventory row for the rule has `ok=0` |
| **Skipped** | every inventory row has `ok=2` (and none `ok=0`) |

A rule with mixed `ok=1` and `ok=2` rows counts as **OK** (not skipped).

**Skipped semantics (grill Q3-A):** same `ok=2` encoding as the main **Rules** section (`skip_sections` / `skip_rules` hold-outs).

**Example** (illustrative counts):

```markdown
## Corrections
OK: **24/27**
Fail: **2/27**
Skipped: **1/27**

### Failed corrections

- `Proto-Circassian-ɡʲʷ-xʲʷ-ɣʲʷ?` — `expected_underscore`
- `Proto-Erromango-v_2` — `syntax_other`
```

**Formatting rules (grill Q4-B, Q6):**

- Use `OK` / `Fail` / `Skipped` labels (title case) with `**count/N**`; no percentage lines (unlike **Rules**).
- Omit any bucket line whose count is **zero**.
- Omit the entire `## Corrections` section when there are **no matched** correction rule ids to report.
- Omit `### Failed corrections` heading and list when **Fail = 0**.
- Failed bullets: `` `rule_id` — `failure_class` ``. When a rule has multiple failing `alt_idx` rows, use the modal `failure_class` among failing rows (or first failing row if tied).

**Data source:** cross-reference inventory validation rows with correction ids loaded from `config/parser/index_diachronica_corrections.yml` (same path as `ParserConfig.corrections` / `_load_corrections`). `validate_rules` should pass matched correction ids (or a pre-built stats object) into `summarize_inventory`.

## Acceptance criteria

- [ ] `--reset-changelog` with zero flips writes `rule-inventory-changelog.csv` containing only the header row
- [ ] `--reset-changelog` with flips still overwrites and writes header + flip rows
- [ ] Without `--reset-changelog`, zero flips does not modify an existing changelog file
- [ ] Summary includes `## Corrections` between **Rules** and **Failure classes** when matched corrections exist
- [ ] Per-rule rollup matches grill Q2-A / Q3-A; orphans excluded from N
- [ ] Zero-count bucket lines omitted; `### Failed corrections` omitted when Fail = 0
- [ ] Failed bullets show `rule_id` and `failure_class`
- [ ] Tests cover reset-empty-changelog, corrections stats rollup (including multi-`alt_idx` and skipped hold-outs), and summary section formatting

## References

- `src/conlanger/tools/index_inventory.py` — `summarize_inventory`, `append_ok_flip_changelog`, `CHANGELOG_CSV_COLUMNS`
- `src/conlanger/scripts/validate_rules.py` — `--reset-changelog`
- `src/conlanger/scripts/config_loaders.py` — `_load_corrections`
- `config/parser/index_diachronica_corrections.yml`
- [ADR-0012 Index Diachronica corrections overlay](../../../docs/adr/0012-index-diachronica-corrections-overlay.md)
- [validate.md](../../../docs/system/validate.md) — update changelog + summary table rows when implemented
