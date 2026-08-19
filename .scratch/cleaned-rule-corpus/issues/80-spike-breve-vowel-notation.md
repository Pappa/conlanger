Type: spike
Status: needs-triage
Blocked by:

# Spike: Index breve vowel notation (`̆`) → ASCA representation

## Question

For **`unknown_character`** failures on combining breve **`̆`** (and precomposed breve vowels like `ɨ̆`, `j̆`, `ə̆`, `ă`, `æ̆`), what does Index Diachronica intend phonologically, and is there a **class-first** ASCA target — or should these rules be `manual_mappings` / `status: skipped` hold-outs?

Spawned from sizing after [63 near-miss unknown_character](63-correction-pass-near-miss-unknown-character.md) (2026-08-19).

## Context

**13** inventory rows (`unknown_character`, error_token `̆`) across **8** sections. Subclusters:

| Subcluster | rows | Sections (examples) |
|---|---:|---|
| Tai `iə > j̆`, `ɨ̆` | 9 | 38.1.1.3–38.1.1.5 (Central/North/Southwest Tai, Po-Ai) |
| Scots / Athabaskan breve vowels | 3 | 17.7.2.1.10 Scots; 29.1.1.1.37 Tanacross |
| Slavic `i > j̆` | 1 | 46.14 Pre-Slavic Vowel Changes |

**ASCA 0.10.2 probes (2026-08-19):** all breve segment forms reject (`j̆`, `ɨ̆`, `ə̆`, `ă`, `æ̆`). `V:[+short]` → unknown feature `short`. No compile regex analogue to `ː` → `:[+long]`.

Issue 63's `ı→j` mapping exposed Tai rules that previously failed on dotless `ı`; they now fail on `̆` instead (same ok/fail status, different error token).

Near-miss: **5 / 13** rows in ≤3-fail sections; **1** mono-class near-miss section.

## What to research

1. Sample Index HTML / linguistic context for Tai `̆` (extra-short? centralized vowel?) and Athabaskan/Scots `æ̆`/`ə̆`.
2. ASCA 0.10.2 feature matrix survey — any accepted feature combo for extra-short / non-syllabic vowels?
3. Brassica / Americanist conventions if relevant (cite primary sources).
4. Recommend per subcluster: **parse IPA map** | **compile transform** | **manual_mappings** | **defer/skip** — with confidence.
5. Rank by section-complete impact if cleared.

Resolve with `/research`. Deliver findings markdown + optional CSV (same shape as [unknown-character-ipa-mappings.csv](../research/unknown-character-ipa-mappings.csv)).

## Out of scope

- Implementing mappings (follow-on correction pass or manual_mappings batch)
- Bundling with [79 matrix-suffix `ː`](79-correction-pass-matrix-suffix-length-marker.md) — different layer and difficulty

## Acceptance criteria

- [ ] Subcluster table with counts and linguistic gloss
- [ ] ASCA acceptance probes recorded (legal / illegal forms)
- [ ] Per-subcluster recommendation with confidence
- [ ] Findings under `.scratch/cleaned-rule-corpus/research/`
- [ ] Follow-on correction-pass ticket filed **or** explicit defer/skip recommendation

## References

- [Correction pass: near-miss unknown_character](63-correction-pass-near-miss-unknown-character.md)
- [Spike: unknown_character → IPA mappings](42-spike-unknown-character-ipa-mappings.md) — combining marks excluded from letter CSV
- [Correction pass template](13-correction-pass-template.md)
- [Inventory summary](../inventory/asca-rule-inventory-summary.md)
