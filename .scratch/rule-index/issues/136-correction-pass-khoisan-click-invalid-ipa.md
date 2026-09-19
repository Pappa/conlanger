Type: task
Status: ready-for-agent
Blocked by:

# Correction pass: Khoisan click notation (`invalid_ipa`)

Target cluster: `invalid_ipa` — **47** failing rules at current inventory; IPA tokens **`ǃ`** (25), **`ǀ`** (11), **`ǁ`** (6), **`ǂ`** (5) — concentrated in **§20.x** Khoisan. Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-09-19).

**Policy** ([138](../issues/138-spike-asca-khoisan-click-representation.md) resolved): compile-time click normaliser first, then manual residuals — [research/asca-khoisan-click-representation.md](../research/asca-khoisan-click-representation.md).

## Problem

Index uses Unicode click letters in rules; ASCA rejects them at validation (`Could not get value of IPA 'ǃ'`).

Example:

```
ʊ > ɤ ! C:[+labial]_ and _l
```

(Inventory may show mixed env prose + click segments — classify per rule after spike.)

## What to build

1. Read [138](138-spike-asca-khoisan-click-representation.md) findings ([research/asca-khoisan-click-representation.md](../research/asca-khoisan-click-representation.md) when written).

2. Implement the spike’s primary lever:
   - **Parse-time** mappings (`ipa_mappings.yml` / `manual_mappings.yml`) when recommended, or
   - **Compile-time** normalisation when Index → ASCA requires programmatic feature/group expansion, or
   - **Manual / overlay** for rule-specific rows, or
   - **`skip_sections` / `skip_rules`** when spike concludes no faithful ASCA projection.

3. Full inventory re-run; `invalid_ipa` cluster delta (click tokens and §20.x section counts) in **Answer**.

## Out of scope

- Non-click `invalid_ipa` rows after click clearance — file follow-on.
- Changing the ASCA fork IPA inventory without upstream agreement (spike may recommend fork change separately; not default scope).

## Acceptance criteria

- [ ] Implementation matches spike **Recommendation** (record deviation in **Answer** if any)
- [ ] Class-first or explicit skip/manual per [ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)
- [ ] Full inventory re-run; metrics in **Answer**

## References

- [invalid_ipa_errors.csv](../inventory/error_clusters/invalid_ipa_errors.csv)
- [138 spike](138-spike-asca-khoisan-click-representation.md)
- [Correction pass template](13-correction-pass-template.md)
