Type: spike
Status: needs-triage
Blocked by: 66

# Spike: nested sets in Index optional-output / set notation

Spawned from [grill 61](61-grill-optional-outputs.md). Nested sets are **out of scope** for [optional-outputs implementation](66-implement-optional-outputs-alt-idx.md).

## Question

What nested-set shapes appear in Index Diachronica / the cleaned corpus (e.g. sets inside sets, or set members that are themselves parallel/set-valued), and which of those should become a class-first compile path, `manual_mappings`, skip, or a later grill?

## What to research

1. Inventory / YAML scan for nested `{…}` (brace depth > 1) in **stages** and related fields.
2. Bucket by shape; note overlap with optional outputs (unpaired output set) vs paired sets vs other failure classes.
3. Check ASCA 0.10.2 (and Brassica notes if relevant) for any faithful encoding.
4. Recommend: correction-pass ticket(s), grill, or explicit defer/skip.

## Acceptance criteria

- [ ] Findings under `.scratch/cleaned-rule-corpus/research/`
- [ ] Counted buckets with example `source` lines
- [ ] Follow-on ticket(s) filed **or** explicit defer/skip recommendation

## References

- [Grill 61](61-grill-optional-outputs.md) — detection excludes nested sets from the flat optional-outputs path
- [Implement optional outputs](66-implement-optional-outputs-alt-idx.md)
- [asca-rule-validity.md](../research/asca-rule-validity.md)
