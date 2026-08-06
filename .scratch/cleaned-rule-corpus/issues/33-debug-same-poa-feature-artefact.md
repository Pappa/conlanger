Type: task
Status: ready-for-agent

# Debug / fix: Index `same POA` (inventory `samePOA`)

## Problem

ASCA compile validation fails a cluster of rules with `unknown_feature` / token **`samePOA`** (Index prose **`same POA`** inside feature matrices). Spike 29 / ticket 32 deferred this under the label **`sameC`**, but a full-text search of Index HTML and the current inventory finds **no `sameC`** — only **`same POA`**. The `sameC` label looks like a research/tokenisation artefact; this ticket targets the real Index string.

Examples (HTML SoT):

| Line | Raw (abbrev.) |
|-----:|---------------|
| 4726 | `F[+voice] → S[+same POA] / l̥_` |
| 6361 | `O → ∅ / {F[- same POA],r,l}_O` |
| 10473 | `NC → N[+same POA]C / #_ (in verbs)` |
| 13647 | `N → [+ same POA] / _C` |

Inventory rows: filter `error_token == samePOA` in [asca-rule-inventory.csv](../inventory/asca-rule-inventory.csv).

## What to do

1. **Diagnose** — Confirm ASCA’s parse of `[+same POA]` / `[+ same POA]` (space stripping → `samePOA`). Confirm there is no ASCA feature for “same place of articulation” agreement.
2. **Classify intent** — Is Index `same POA` place-agreement co-reference (needs alpha/reference / other machinery), an unrepresentable Index gloss, or something that should move to **`comment`**?
3. **Fix** — Class-first if possible (parse-time strip-to-comment, compile strategy, or documented skip). Do **not** add a fake `feature_mappings.csv` rename. Preserve **`raw`**. Follow ADR-0010 (no pre-emptive skip until class-first options are exhausted).
4. **Clean up docs** — Correct spike/ticket wording that says `sameC` where the corpus actually has `same POA` / `samePOA`.

## Out of scope

- Positional / identity subscript compile transforms (deferred; see map).
- Brassica.
- Seeding `samePOA` → some ASCA feature synonym without a primary-source basis.

## Acceptance criteria

- [ ] Root cause written under **Answer** (ASCA tokenisation + Index intent)
- [ ] Concrete fix or explicit hold-out policy shipped (or owner-approved skip) for the `samePOA` cluster
- [ ] Inventory re-check: `samePOA` count before/after
- [ ] `sameC` mislabel corrected in research/issue notes that still claim HTML `sameC`

## References

- [index-feature-matrices-to-asca-targets.md](../research/index-feature-matrices-to-asca-targets.md) (deferred `sameC` row — likely misnamed)
- [unknown-feature-suggestions-assessment.md](../research/unknown-feature-suggestions-assessment.md)
- [32-correction-pass-unknown-feature.md](32-correction-pass-unknown-feature.md) Phase 2 deferrals
- ADR-0010 historical fidelity / class-first
