Type: task
Status: ready-for-agent
Blocked by: 142

# Implement index rule normalisation passes

## Question

Replace ad hoc regex / `manual_mappings.yml` overlap with an ordered **index rule normalisation** pipeline on the working line (after manual mappings, before section mappings) per [140](140-adr-parse-pipeline-order-and-raw-semantics.md).

## Answer

- Each pass is a pure function `str -> str` (or `IndexRule` pre-split only where agreed).
- Document each pass in [index-diachronica-parser.md](../../../docs/system/index-diachronica-parser.md).
- Track parity vs prior parse output; retire `manual_mappings` rows when extraction + normalisation match (checklist from [122](122-grill-proximity-conditions-yaml.md) proximity rows).
- Initial pass list is **inventory-driven** (file follow-on tickets per cluster if needed); do not port all manual rows in one PR.

## Acceptance

- [ ] Normalisation module + registration order in parser
- [ ] Tests per pass; no coverage regression on quality gates
- [ ] Diagnostics note in `diagnostics/parse/` when a pass changes working line (optional CSV)

## Related

- [139](139-grill-parse-indexrule-model-and-surface-normalization.md)
