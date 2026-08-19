Type: task
Status: resolved
Blocked by: 62

# Correction pass: near-miss `unknown_character` tokens

Target cluster: `unknown_character` in sections with **≤3** fails — high-leverage tokens from the 2026-08-12 near-miss audit: **`ı`**, **`ṽ`**, **`ₓ`**, **`û`** (then residual `ː` / accent marks if still cheap).

Priority: **second** after [tone features](62-correction-pass-tone-features.md); **re-review** inventory/section-complete metrics before filing further character passes.

## Context

Section-completeness goal: maximize sections with 0 fails. Among ≤3-fail sections, `unknown_character` hits **87** sections (**41** mono-class → complete if cleared). Top tokens in that band: `ı` 13, `ṽ` 11, `ₓ` 10, `û` 9.

`ₓ` may overlap collective/series coverage ([series backlog](../series-mappings-coverage-backlog.md) / [65](65-series-mappings-coverage-pass.md)) — prefer series/collective expand over IPA letter hacks when the token is a collective subscript.

## What to build

1. After ticket 62 lands, re-pull near-miss ≤3 token table (don't trust stale counts).
2. Class-first mappings for the top recoverable tokens (parse `ipa_mappings.csv` / compile diacritic passes as warranted).
3. Full inventory; record section-complete delta.

## Acceptance criteria

- [x] Target tokens named and sized from post-62 inventory
- [x] Class-first transforms only (edit ladder / ADR-0010)
- [x] Full inventory re-run; ok + sections-all-OK before/after
- [x] Fixtures updated where outcomes changed

## Answer

**Shipped 2026-08-19.**

### Post-62 near-miss token table (≤3-fail sections, `unknown_character`)

| token | pre-pass error rows | action |
|------:|--------------------:|--------|
| `ı` | 46 | `ı→j` in `ipa_mappings.csv` (confidence `low`→`medium`) |
| `ṽ` | 27 | `ṽ→ṽ`, `Ṽ→ṽ` (ASCA rejects precomposed ṽ; decomposed nasal vowel) |
| `û` | 9 | `û→u` (medium; parallel to existing `î→i`) |
| `ₓ` | 0 | already cleared via `parser_config.yml` `series_expansions` (tickets 74/75) |

ASCA 0.10.2 smoke: precomposed `ṽ`/`û`/`ı` reject; decomposed `ṽ`, plain `u`, and `j` (incl. `j̃` digraphs) accept.

### Inventory

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK / total | 8025 / 9639 (83.3%) | **8094 / 9639 (84.0%)** | **+69** |
| Sections all OK | 288 / 713 (40.4%) | **299 / 713 (41.9%)** | **+11** |
| `unknown_character` | 282 | **206** | **−76** |

**Residuals (target cluster):** `ı`/`ṽ`/`û` error-token counts → **0**. Tai `iə > ı̆` rules now fail on combining `̆` (`unknown_character` ×13), not dotless `ı`. `ː` (×23) and bare combining accents unchanged — out of scope unless cheap follow-up.

**Code:** `data/common/ipa_mappings.csv`; tests in `test_parser.py` (`test_normalize_ipa_in_field_near_miss_unknown_characters`, `test_parse_rule_element_normalizes_near_miss_unknown_characters`).

## References

- [Spike: unknown_character → IPA mapping candidates](42-spike-unknown-character-ipa-mappings.md)
- [Correction pass: IPA letter mappings](49-correction-pass-ipa-letter-mappings.md)
- [Correction pass template](13-correction-pass-template.md)
