Type: task
Status: ready-for-agent
Blocked by: None

# ADR: parse pipeline order, `raw` semantics, and index rule normalisation placement

## Question

Record the parse-time working-line order and audit `raw` policy decided in [Grill: parse-time IndexRule model and index rule normalisation](139-grill-parse-indexrule-model-and-surface-normalization.md).

## Answer (spec for ADR author)

1. **`raw`** on every corpus rule is **always** the HTML extract (subscripts normalised); **never** the corrections overlay.
2. **Working line** starts from `raw`, then **corrections** overlay by `rule_id` (`index_diachronica_corrections.yml`).
3. **Manual mappings** on working line.
4. **Index rule normalisation** (ordered transforms).
5. **Section mappings**.
6. First **`;`** comment peel, then symbol normalisation, structural split, field transforms (detail in parser doc).

Amend [index-diachronica-parser.md](../../../docs/system/index-diachronica-parser.md) Phase A½ table to match code after implementation.

## Outcomes

- [ ] New ADR (or amend ADR-0006 / ADR-0010) committed under `docs/adr/`
- [ ] Parser doc table updated
- [ ] `IndexDiachronicaParser.parse_rule_element` implements order (may land with [141](141-implement-indexrule-pydantic-and-yaml-schema.md))

## Related

- [139 grill](139-grill-parse-indexrule-model-and-surface-normalization.md)
