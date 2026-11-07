Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Classify `expected_underscore` inventory failures and recommend compile fixes for syllable-position gaps.
Blocked by:

## Problem Statement

Roughly one hundred rules fail ASCA validation with failure class `expected_underscore`. Some failures come from syllable-position or stress environments that never receive a valid ASCA focus underscore at compile time (`position.in`, `%` / `#U` / `U#`, compound tails such as `O_ in #U`). Others fail for unrelated reasons (prose conditions, bare `else`, invalid rule text). Without a row-by-row triage across ingest, parse, and compile representations, compile work risks fixing the wrong rules or missing distinct fix families.

## Description

Review every inventory row in `diagnostics/inventory/rule-inventory-error.csv` where `failure_class` is `expected_underscore` (same row set as `diagnostics/inventory/expected_underscore_errors.csv` when present).

For each row, record three representations, keyed by `rule_id`, `alt_idx`, and `step_idx`:

1. **Raw Index text** — HTML source line from `data/diachronica/index_diachronica.html` (use the inventory `source` column).
2. **Parsed rule** — structured rule (including `env`, `exception`, and `IndexContext` / `position.in` when present) from `data/diachronica/index_diachronica.yml`.
3. **Compiled rule** — emitted ASCA-oriented fields from `diagnostics/compile/asca_rules.yml` for the same rule key.

Compare representations against existing compile behaviour documented in [sound-change-applier.md](../../docs/system/sound-change-applier.md) (structured `IndexContext`, syllable-position pass) and code in `src/conlanger/compile/position_in_projection.py`, `src/conlanger/compile/project_index_context.py`, and `src/conlanger/compile/tools/asca/syllable_position.py`. Prior research: [0039-index-syllable-position-u-hash](../spikes/0039-index-syllable-position-u-hash.md).

Pay attention to:

- Environments that denote syllable position without a literal underscore (including classified and unclassified `position.in` targets).
- Compound environments (for example segment focus plus `in #U` / `in U#`) that should become ASCA environment sets at compile time but may omit `position.in` handling.
- Rules that already compile correctly elsewhere in the corpus (use as contrast examples in the report).

**Out of scope for this task:** implementing compile fixes, parse corrections, or inventory code changes — only analysis and fix recommendations.

**Deliverable:** findings file `.backlog/spikes/0045-expected-underscore-syllable-compile-review.md` (TLDR plus detailed tables or sections per fix family).

## Acceptance Criteria

- [ ] Every row with `failure_class` `expected_underscore` in `diagnostics/inventory/rule-inventory-error.csv` appears in the findings file (count in TLDR matches the CSV filter).
- [ ] Each listed rule includes the three representations (raw HTML, parsed YAML excerpt, compiled YAML excerpt) or documents why a representation is missing.
- [ ] Each rule has exactly one **primary** failure category: **syllable-position compile gap**, **compound env / env-set + position gap**, **unrelated (prose, syntax, other)**, or **needs follow-up spike**.
- [ ] All rules in the two syllable-related categories are grouped into **fix families**; each family states intended ASCA shape, likely code seam, and whether it extends existing `position.in` projection or syllable-position pipeline behaviour.
- [ ] Unrelated failures are listed separately so later compile tasks do not treat them as syllable-position work.
- [ ] TLDR summarizes counts per category and fix family and names recommended follow-up tasks (titles only, no implementation).
- [ ] Set **`Status: resolved`** on this item; sync the plan **Tasks** table; record the findings path in **Comments**.

## Comments
