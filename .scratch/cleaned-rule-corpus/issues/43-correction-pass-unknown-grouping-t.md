Type: task
Status: resolved
Blocked by: 12

# Correction pass: unknown_grouping — residual `T` token

Target cluster: `unknown_grouping` where `error_token` is **`T`** — **49** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)); **49 / 133** (37%) of remaining `unknown_grouping` failures.

Spawned from [correction pass template](13-correction-pass-template.md) investigation (2026-08-08).

## Problem

`data/asca/group_mappings.csv` already maps Index **`T`** (voiceless plosive) → `P:[-voice]`, and [ticket 14](14-correction-pass-unknown-grouping.md) wired compile-time expansion in `apply_asca_group_mappings_to_string()`. Despite this, **49** rules still fail with `Unknown grouping 'T'`.

## Investigation (2026-08-08)

### Symptom

Compiled strings still contain literal `T` where Index meant the voiceless-plosive class letter, e.g.:

| Compiled fragment (still literal) | ASCA error |
| --- | --- |
| `{Tʃ,Tʃʷ}` | Unknown grouping `T` |
| `> Tʃ` | Unknown grouping `T` |
| `sTP çTP` | Unknown grouping `T` |
| `çT` | Unknown grouping `T` |

Repro (current `group_mappings.py`):

```python
apply_asca_group_mappings_to_string("{Tʃ,Tʃʷ} > P:[-voice]P", mappings)
# → '{Tʃ,Tʃʷ} > C:[+labial]:[-voice]C:[+labial]'   # T unchanged; P expanded

apply_asca_group_mappings_to_string("Tʃ > P:[-voice]P", mappings)
# → 'Tʃ > C:[+labial]:[-voice]C:[+labial]'         # T unchanged

apply_asca_group_mappings_to_string("çT > ʃt", mappings)
# → 'çT > ʃt'                                       # T unchanged

apply_asca_group_mappings_to_string("sTP", mappings)
# → 'sTC:[+labial]'                                 # only P expands; T unchanged
```

Contrast: `TS > TH` **does** expand `T` (and `S`, `H`, `P`) because `T` is followed by uppercase `S`, which is already allowed by `_GROUPING_FOLLOW`.

### Root cause — two boundary gaps in `group_mappings.py`

Class-letter expansion uses paired lookaround regexes:

```8:12:src/conlanger/tools/asca_compile/group_mappings.py
_GROUPING_PREC = r"(?:^|(?<=[\{\[\s/,>_A-Z#$%|!\(-]))"
_GROUPING_FOLLOW = r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z])"
_GROUPING_FOLLOW_LABIALIZED = (
    r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z]|[a-z\u0250-\u02AF])"
)
```

**Gap A — IPA tail (44 / 49 rules).** `_GROUPING_FOLLOW` allows uppercase ASCII or punctuation after a class letter, but **not** IPA letters in the Latin Extended-B block (`U+0250–U+02AF`). Index writes affricates as class **`T`** + IPA **`ʃ`** (`Tʃ`, `Tʃʷ`). The `ʃ` (U+0283) blocks the match, so `T` is never expanded.

Affected sections: mostly **§29 Athabaskan** (42 rules), plus §17.10 PIE→PII (1), §38.1.1 Dioi (1).

**Gap B — glued clusters (5 / 49 rules).** `_GROUPING_PREC` only treats a class letter as starting after delimiters or **uppercase** ASCII. In rGyalrongic rules, `T` is glued inside clusters like `sTP`, `çTP`, `lTP`, or after IPA `ç` in `çT`, so the letter is never eligible for expansion.

Affected sections: **§36.3.2** rGyalrongic (5 rules).

### What is *not* the problem

- Missing CSV row — `T,P:[-voice]` is present and correct.
- Wrong mapping target — spike [09](09-spike-asca-class-letter-feature-matrices.md) validated `P:[-voice]`.
- Labialization pass ([23](23-correction-pass-labialized-class-letters.md)) — `Tʷ` is out of scope; failures are bare `T` before IPA or inside clusters.

## Suggested fix

### Phase 1 — IPA tail follow (ship first; ~44 rules)

Extend `_GROUPING_FOLLOW` to accept IPA extensions **without** ASCII lowercase (preserves `Kr` / `Kw` / `rK` regression tests from ticket 23):

```python
_GROUPING_FOLLOW = r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z]|[\u0250-\u02AF])"
```

**Expected transforms:**

| Before | After |
| --- | --- |
| `Tʃ` | `P:[-voice]ʃ` |
| `{Tʃ,Tʃʷ}` | `{P:[-voice]ʃ,P:[-voice]ʃʷ}` |
| `C:[+front,+hi,-lo] > Tʃ` | `C:[+front,+hi,-lo] > P:[-voice]ʃ` |

**Regression checks (must stay unchanged):** `Kr > k`, `Kw > k`, `rK > k` (ticket 23 fixtures).

### Phase 2 — glued cluster letters (follow-on; ~5 rules)

Extending only `_GROUPING_PREC` with `[\u0250-\u02AF]` fixes affricate tails but **not** `çT` (U+00E7) or `sTP` (ASCII `s` prefix). Options to spike before shipping:

1. **Widen prec with IPA modifier ranges** — add Latin-1 IPA-adjacent letters used in Index (`ç`, etc.) while still excluding ASCII `a-z` so `rK` stays safe.
2. **Unglued scan** — second pass: expand mapped uppercase letters when followed by a valid `_GROUPING_FOLLOW` even if prec is lowercase IPA, but **not** when followed by ASCII lowercase (keeps `Kr`).
3. **Section-local abbreviations** — map `sTP` / `çTP` as multi-char tokens in `group_mappings.csv` (map.md notes this pattern for Athabaskan `TŠ`; cluster-driven).

Recommend **Phase 1 immediately**; file Phase 2 as a sub-task if inventory still shows `T` in §36.3.2 after Phase 1.

## What to build

1. Phase 1 code change in `src/conlanger/tools/asca_compile/group_mappings.py` (+ unit tests on Athabaskan fixtures above).
2. Full inventory re-run (`uv run regenerate_corpus`); record before/after for `unknown_grouping` / `T` token.
3. Phase 2 only if residual `T` cluster remains.

## Policy

- Compile-layer boundary fix only; `raw` and corpus YAML unchanged (ADR-0010).
- No new CSV rows for Phase 1 — existing `T` mapping is correct; the expander regex is wrong.
- Do not expand ASCII-lowercase-glued class letters without Phase 2 spike (risk to `Kr`-style segment literals).

## Acceptance criteria

- [x] Phase 1 `_GROUPING_FOLLOW` extended; tests cover `Tʃ`, `{Tʃ,Tʃʷ}`, and ticket 23 regressions
- [x] Full inventory re-baseline; `unknown_grouping` `T` count **49 → ≤5** (Phase 2 residual)
- [x] Before/after metrics recorded in **Answer**
- [x] Phase 2 approach documented or implemented for rGyalrongic `sTP` / `çT` if still failing

## Answer

Phase 1 shipped in `group_mappings.py`: `_GROUPING_FOLLOW` now accepts IPA extensions (`U+0250–U+02AF`) after class letters, so `Tʃ`/`Tʃʷ` expand to `P:[-voice]ʃ`/`P:[-voice]ʃʷ`. Tests in `test_phonological_ruleset.py`.

**Inventory (ASCA 0.10.2, full HTML re-parse):**

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK | 6658 (72.4%) | 6696 (72.8%) | **+38** |
| `unknown_grouping` (all) | 133 | 89 | **−44** |
| `unknown_grouping` `T` token | 49 | 5 | **−44** |

Residual **5** `T` failures are all §36.3.2 rGyalrongic glued clusters (`sTP`, `çTP`, `lTP`, `çT`) — Phase 2 per investigation above; no new ticket filed yet.

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: unknown_grouping (class letters)](14-correction-pass-unknown-grouping.md)
- [Correction pass: labialized class letters](23-correction-pass-labialized-class-letters.md) — boundary regression fixtures
- [`group_mappings.py`](../../../src/conlanger/tools/asca_compile/group_mappings.py)
- [`data/asca/group_mappings.csv`](../../../data/asca/group_mappings.csv)
