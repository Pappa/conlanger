Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Index breve vowel notation (`̆`) → ASCA representation.
Result: [0042-breve-vowel-notation.md](../spike/0042-breve-vowel-notation.md)
Blocked by:

## Question

For **`unknown_character`** failures on combining breve **`̆`** (and precomposed breve vowels like `ɨ̆`, `j̆`, `ə̆`, `ă`, `æ̆`), what does Index Diachronica intend phonologically, and is there a **class-first** ASCA target — or should these rules be `manual_mappings` / `status: skipped` hold-outs?

Spawned from sizing after [63 near-miss unknown_character](63-correction-pass-near-miss-unknown-character.md) (2026-08-19).

## Answer

**Resolved 2026-08-19.**

Findings: [breve-vowel-notation.md](../spike/breve-vowel-notation.md), [breve-vowel-notation.csv](../spike/breve-vowel-notation.csv).

**ASCA:** Breve glyphs (`j̆`, `ɨ̆`, `ə̆`, `ă`, `æ̆`, `ŭ`, `ŏ`) all reject. `segment:[-long]` and bare-segment stripping validate. `[+short]` rejects. `@{Breve}` is romanisation-only.

**Per-subcluster:** Tai + Scots + Tanacross → **`compile_transform`** (`normalize_asca_breve_marks()`); Slavic §46.14 → **`skip`**.

**Impact:** 13 rows / 8 sections; **+1** section all-OK if cleared (Scots 17.7.2.1.10 only). Low near-miss leverage.

**Follow-on:** [84 correction pass: breve vowel notation](84-correction-pass-breve-vowel-notation.md).

## Source list

- `.scratch/rule-index/issues/80-spike-breve-vowel-notation.md`
