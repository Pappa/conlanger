Type: spike
Status: resolved

# Spike: unknown_character → IPA mapping candidates

## Question

For **`unknown_character`** failures in [rule-inventory-error.csv](../inventory/rule-inventory-error.csv), which non-punctuation error tokens are **letter-like** Index graphèmes that should map to ASCA-accepted IPA at parse time (via `ipa_mappings.csv`), and with what confidence?

## Notes

- Baseline: **613** `unknown_character` rows ([inventory summary](../inventory/rule-inventory-summary.md)); **51** distinct letter-like `error_token` values after filtering punctuation and combining marks alone.
- Existing ingest path: `data/common/ipa_mappings.csv` + `apply_ipa_mappings()` in `IndexDiachronicaParser` (Š→ʃ seeded).
- **Out of scope for this spike:** length marks (`ː`, `ˑ` — tickets 15/25); subscript correspondence notation (`ₓ`, `ₙ`, …); pure punctuation (`(`, `"`, …); prose env fragments where the character is not a phonological segment.
- Validate proposed targets against **ASCA 0.10.2** `validate_asca` smoke (single-segment rules).
- Resolve with `/research`; deliver CSV columns: `index_feature`, `ipa_target`, `confidence`, `notes`.

## Acceptance criteria

- [x] Unique letter-like `error_token` values extracted from inventory error CSV with counts
- [x] Punctuation / combining-only / length / subscript tokens documented as excluded
- [x] Proposed mappings with `high` | `medium` | `low` | `defer` confidence and cited rationale
- [x] Output CSV at `research/unknown-character-ipa-mappings.csv`
- [x] Findings markdown linked from this ticket; no bulk seeding of `ipa_mappings.csv` (spike only)

## Answer

**613** `unknown_character` rows → **78** distinct `error_token` values. After filtering punctuation/combining-only (**27** tokens) and non-segment notation (length **2**, subscript **5**), **42** letter-like tokens remain in scope (**~470** row hits).

**Deliverables**

- Findings: [research/unknown-character-ipa-mappings.md](../research/unknown-character-ipa-mappings.md)
- Proposed mappings CSV: [research/unknown-character-ipa-mappings.csv](../research/unknown-character-ipa-mappings.csv) — **44** rows (42 letter tokens + 4 `defer` prose hits for ASCA-valid segments)

**High-confidence seed candidates (16 tokens):** `ḱ`→`kʲ`, `ǵ`→`ɡʲ`, `š`→`ʃ`, `Ṣ`→`ʂ`, `Ṭ`→`ʈ`, `Ṽ`→`ṽ`, nasal vowels `ã/ẽ/õ/ũ`→decomposed tilde, `è`→`ɛ`, `ā/ē`→long vowels, `ȵ`→`ɲ`.

**Defer:** `Ω` (author placeholder); `ð`/`ŋ`/`ɛ`/`ʝ` (ASCA already accepts; inventory hits are prose).

**Follow-on:** paste high/medium rows into `data/common/ipa_mappings.csv` as a correction pass (not done in this spike).
