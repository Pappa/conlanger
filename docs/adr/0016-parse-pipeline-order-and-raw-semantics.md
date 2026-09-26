# Parse working-line order and HTML-only `raw`

Per-rule parse applies overlays and normalisation to a **working copy** of the extracted Index line. The stored **`raw`** field is always the HTML extract (Unicode subscripts, whitespace collapsed) and is **never** rewritten by corrections, manual mappings, section mappings, or later transforms.

**Working-line order** (after Phase A HTML text extraction):

1. **Index Diachronica correction** overlay by **rule id** (`config/parser/index_diachronica_corrections.yml`) on the working copy only.
2. **Index rule normalisation** — ordered, policy-documented surface transforms on the working line ([ticket 143](../../.scratch/rule-index/issues/143-implement-index-rule-normalisation-passes.md); placeholder no-op until passes land).
3. **Manual mapping** (`manual_mappings.yml`) — applied in order of definition; substring or regex rewrite on the working copy.
4. **Section mapping** (`parser_config.yml` `section_mappings`, ancestry merge).
5. Quoted-prose short-circuit, then first-`;` comment peel, symbol normalisation, structural split, and class-first field transforms (detail in [index-diachronica-parser](../system/index-diachronica-parser.md)).

Grill and audit: [ticket 139](../../.scratch/rule-index/issues/139-grill-parse-indexrule-model-and-surface-normalization.md).

## Considered Options

- **Corrections replace `raw` (previous, [ADR-0012](0012-index-diachronica-corrections-overlay.md))** — conflates maintainer overlay with HTML audit trail; inventory diffs could not see HTML vs corrected claim side by side in one field.
- **HTML-only `raw` + corrections on working line (chosen)** — `raw` matches published Index text; corrections still drive parsed `stages` / `env` / `exception`; `source` still points at the HTML `<p>`.

## Consequences

- [ADR-0012](0012-index-diachronica-corrections-overlay.md) is amended: correction content applies to the **working line**, not to **`raw`**.
- Parser doc Phase A½ table and `IndexDiachronicaParser.parse_rule_element` must match this order:
  - index rule normalisation
  - manual mappings
  - section mappings
- Regenerated index YAML may show HTML `raw` where corrections previously overwrote `raw`; parsed fields stay correction-shaped when overlays exist.
