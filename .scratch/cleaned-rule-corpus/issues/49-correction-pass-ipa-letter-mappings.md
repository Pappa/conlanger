Type: task
Blocked by: 12, 42

# Correction pass: IPA letter mappings (spike 42)

Target cluster: `unknown_character` — letter-like Index graphèmes with **high** or **medium** confidence mappings from spike 42 — **81** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Spike [42](42-spike-unknown-character-ipa-mappings.md) identified **42** letter-like tokens (~470 row hits at spike time; **81** rows match high+medium tokens in the current error CSV). Ingest path exists (`data/common/ipa_mapping.csv` + `apply_ipa_mappings()` in `IndexDiachronicaParser`) but only `Š→ʃ` is seeded.

Top residual letter-like tokens include `ı`, `ṽ`, `ь`, `î`, and PIE/Leiden `ḱ`/`ǵ`, Americanist `š`/`Ṣ`/`Ṭ`, nasal vowels with tilde.

## What to build

1. Paste **high** and **medium** confidence rows from [research/unknown-character-ipa-mappings.csv](../research/unknown-character-ipa-mappings.csv) into `data/common/ipa_mapping.csv`.
2. Verify each seeded target against ASCA 0.10.2 (`validate_asca` smoke on single-segment rules).
3. Unit tests on representative inventory lines per token family.
4. Full inventory re-run; record before/after for `unknown_character` and per-token residual counts.

**Expected impact:** ~**60** ok uplift at ~75% recoverability.

### Out of scope

- `low` / `defer` spike rows (e.g. `Ω`)
- Length marks (`ː`, `ˑ` — tickets 15/25)
- Subscript notation (`ₓ`, `ₙ`, … — tickets 40/41)
- Punctuation-only tokens (`(`, smart quotes — separate tickets)
- Combining marks alone (`́`, `̣`, …)

## Policy

- Parse-time mapping only; `raw` unchanged.
- Do not seed without spike confidence review ([findings](../research/unknown-character-ipa-mappings.md)).

## Acceptance criteria

- [ ] `ipa_mapping.csv` seeded with all high+medium spike rows
- [ ] ASCA smoke tests pass for each new mapping
- [ ] Full inventory re-baseline; per-token before/after in **Answer**
- [ ] Fixtures updated where outcomes change

## Answer

_(pending)_

## References

- [Spike: unknown_character → IPA mappings](42-spike-unknown-character-ipa-mappings.md)
- [Research findings](../research/unknown-character-ipa-mappings.md)
- [Correction pass template](13-correction-pass-template.md)
