Type: task
Status: ready-for-agent
Blocked by: 62

# Correction pass: near-miss `unknown_character` tokens

Target cluster: `unknown_character` in sections with **≤3** fails — high-leverage tokens from the 2026-08-12 near-miss audit: **`ı`**, **`ṽ`**, **`ₓ`**, **`û`** (then residual `ː` / accent marks if still cheap).

Priority: **second** after [tone features](62-correction-pass-tone-features.md); **re-review** inventory/section-complete metrics before filing further character passes.

## Context

Section-completeness goal: maximize sections with 0 fails. Among ≤3-fail sections, `unknown_character` hits **87** sections (**41** mono-class → complete if cleared). Top tokens in that band: `ı` 13, `ṽ` 11, `ₓ` 10, `û` 9.

`ₓ` may overlap collective/series coverage ([series backlog](../series-mappings-coverage-backlog.md) / [65](65-series-mappings-coverage-pass.md)) — prefer series/collective expand over IPA letter hacks when the token is a collective subscript.

## What to build

1. After ticket 62 lands, re-pull near-miss ≤3 token table (don't trust stale counts).
2. Class-first mappings for the top recoverable tokens (parse `ipa_mapping.csv` / compile diacritic passes as warranted).
3. Full inventory; record section-complete delta.

## Acceptance criteria

- [ ] Target tokens named and sized from post-62 inventory
- [ ] Class-first transforms only (edit ladder / ADR-0010)
- [ ] Full inventory re-run; ok + sections-all-OK before/after
- [ ] Fixtures updated where outcomes changed

## References

- [Spike: unknown_character → IPA mapping candidates](42-spike-unknown-character-ipa-mappings.md)
- [Correction pass: IPA letter mappings](49-correction-pass-ipa-letter-mappings.md)
- [Correction pass template](13-correction-pass-template.md)
