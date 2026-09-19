Type: task
Status: resolved
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

- [x] Implementation matches spike **Recommendation** (record deviation in **Answer** if any)
- [x] Class-first or explicit skip/manual per [ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)
- [x] Full inventory re-run; metrics in **Answer**

## Answer

**Baseline (before):** **9003 / 9839** ok (~91.5%); **`invalid_ipa` 47** rules (click tokens `ǃ`/`ǀ`/`ǁ`/`ǂ`; plus **1** non-click Akan affricate row in the same cluster export).

**After (2026-09-19):** **9050 / 9839** ok (~92.0%); **`invalid_ipa` 1** (residual `Akan-p,ʋ̃-c-k͜p` — `k͡` tie-bar, out of scope). **+47** ok rules; **§20.x** Khoisan click rows cleared.

**Implementation (spike [138](138-spike-asca-khoisan-click-representation.md) policy):**

1. **`normalize_asca_index_click_segments()`** in `src/conlanger/tools/compile/asca/clicks.py` — wired on **input/output only** in `compile_asca_rule_field_strings()` (after post-subscript transforms; skips env/exception so Index `!` exception delimiter is preserved).
2. Transforms: `!!` → `! !`; default velar onset on bare clicks; Index `ǂɡ`/`!ɡ` → `ɡǂ`/`ɡ!`; cluster `ˀ` → `:[+cg]`.
3. **`index_diachronica_corrections.yml`** — seven manual rows: §17 `Early-Modern-English-ʊ` env split; optional `(n)` on click I/O expanded to sets for six §20.x rules.
4. Re-parsed index (`create_index`) so corrections land in SoT YAML before inventory.

**Deviations:** none from spike recommendation.

## References

- [invalid_ipa_errors.csv](../inventory/error_clusters/invalid_ipa_errors.csv)
- [138 spike](138-spike-asca-khoisan-click-representation.md)
- [Correction pass template](13-correction-pass-template.md)
