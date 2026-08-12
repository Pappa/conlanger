Type: spike
Status: needs-triage
Blocked by:

# Spike: `syntax_other` in ≤3-fail sections (backlog)

**Backlog** — do not start until after [62](62-correction-pass-tone-features.md) → [63](63-correction-pass-near-miss-unknown-character.md) and a re-review of section-completeness.

## Question

Among sections with **1–3** validation fails, `syntax_other` is the largest lever (**179** rules / **137** sections; **71** mono-class near-misses would go complete if the class cleared). What **subclusters** exist, and which are class-first correction passes vs manual_mappings / skip?

## What to research

1. Re-run inventory; filter sections with `fail_count ≤ 3` and `failure_class == syntax_other`.
2. Bucket by error message / shape (not by Levenshtein alone).
3. Rank buckets by **sections completed** if cleared (not raw rule count).
4. Recommend 1–3 correction-pass instance tickets (or manual_mapping batches).

## Acceptance criteria

- [ ] Findings under `.scratch/cleaned-rule-corpus/research/`
- [ ] Ranked subcluster table with section-complete impact
- [ ] Follow-on correction-pass tickets filed **or** explicit defer/skip recommendation

## References

- [Correction pass template](13-correction-pass-template.md)
- [Inventory summary](../inventory/asca-rule-inventory-summary.md)
