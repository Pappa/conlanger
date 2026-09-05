Type: spike
Status: resolved
Blocked by:

# Spike: IPA-shape correction-pass prioritisation (post-110 baseline)

Spawned from [grill-with-docs session 2026-09-05](../map.md): after passes 107–110 and heavy-section `skip_sections` (Salish 35.1.x, 29.2, 46.13), the next correction-pass queue should target **`expected_ipa` → `invalid_ipa` → `expected_range_dots`**. **Do not file the next batch of ticket-13 instances until this spike resolves.**

Precedent: [Spike: near-miss correction-pass prioritisation](106-spike-near-miss-correction-prioritization.md) (2026-09-01) — same success metric, amended ranking policy (global mono-class rank; ≤3-fail hunt band).

## Question

Given the **current** inventory, which **`expected_ipa`**, **`invalid_ipa`**, and **`expected_range_dots`** subclusters yield the highest **sections-all-OK** payoff (rule-ok delta tiebreaker) — and which should become the next 2–4 correction-pass instances (vs `manual_mappings` / `status: skipped` / defer)?

## Baseline (inventory summary at ticket spawn)

| Metric | Value |
|--------|------:|
| Rules OK / fail / skipped | **8321** / **734** / **772** |
| Sections all-OK | **417 / 714** (58.4%) |
| Sections skipped (`skip_sections`) | **35** |
| Near-miss sections (1–3 fails, active) | **211** |
| Near-miss failing rules | **322** |

Failure-class head (active fails only):

| count | `failure_class` |
|------:|-----------------|
| 125 | `unknown_character` |
| 105 | `expected_underscore` |
| 77 | `expected_ipa` |
| 58 | `invalid_ipa` |
| 43 | `syntax_other` |
| 41 | `expected_range_dots` |

Global mono-class section-complete levers (preliminary sizing):

| `failure_class` | mono-class sections | rules in mono-class |
|-----------------|--------------------:|--------------------:|
| `expected_ipa` | **24** | 28 |
| `invalid_ipa` | **17** | 45 |
| `expected_range_dots` | **6** | 25 |

Preliminary `expected_ipa` shape hints (`error_token` on cluster CSV): `(` (12), `ʷ` (11), `/` (8), `>` (6), `//` (6), `∅` (6), `ʼ` (5) — mostly **prose/gloss/parenthetical residue in compile fields**, not bare missing `ipa_mappings` rows.

Preliminary `invalid_ipa` shape hints: Khoisan `ǃ`/`ǀ`/`ⁿ` (majority of rows in §20.1.x) — overlaps spike-64 defer policy; prenasal `ⁿ` prefix also in §7.13 / §10.3.5.

Preliminary `expected_range_dots`: Yup'ik-style `V.V` geminate/dot ranges (§24.x) and Italic affricate splits (`t.ʃ`).

## What to research

1. Re-run `uv run create_index && uv run validate_rules`; confirm baseline matches or note drift.
2. Bucket **`expected_ipa`**, **`invalid_ipa`**, and **`expected_range_dots`** by shape / error message / field blame — extend [`scan_near_miss_all_classes.py`](../research/scan_near_miss_all_classes.py) or add a class-focused scan; pull from [`expected_ipa_errors.csv`](../inventory/expected_ipa_errors.csv), [`invalid_ipa_errors.csv`](../inventory/invalid_ipa_errors.csv), [`expected_range_dots_errors.csv`](../inventory/expected_range_dots_errors.csv), [`field-isolation-error.csv`](../inventory/field-isolation-error.csv) where useful.
3. Rank buckets by **sections completed if cleared** (primary, **global** mono-class rank — not only ≤3-fail band), rule-ok delta (secondary). Tag each bucket near-miss vs heavy-section.
4. Cross-check against **resolved** env passes (107–108), spike-64 Khoisan defer, and **2026-09-05** heavy-section skips — mark stale or blocked levers.
5. For `expected_ipa`: separate **class-first parse/compile transforms** (strip prose `//`, unwrap `(X)` optionals, editorial `/` gloss) from **`ipa_mappings` / `manual_mappings`** hold-outs.
6. For `invalid_ipa`: separate **ⁿ prenasal prefix** (compile normalisation?) from **Khoisan click `!` notation** (manual/skip per spike 64).
7. For `expected_range_dots`: confirm Yup'ik `..` vs European dot-affricate shapes; one pass or two?
8. Recommend **2–4** numbered correction-pass instance tickets **or** explicit defer/skip/manual batches.

## Acceptance criteria

- [x] Findings under `.scratch/rule-index/research/` (markdown + CSV + scan script if new)
- [x] Ranked subcluster table with section-complete impact on **current** inventory
- [x] Follow-on correction-pass tickets filed **or** explicit defer/skip/manual recommendation
- [x] Map Notes / implementation plan updated with the chosen next queue

## Answer

**2026-09-05** — Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md). Scan: [scan_ipa_correction_classes.py](../research/scan_ipa_correction_classes.py) → [ipa-correction-classes.csv](../research/ipa-correction-classes.csv), [ipa-correction-buckets.csv](../research/ipa-correction-buckets.csv).

Baseline confirmed: **8321 / 734 / 772** rules; **417 / 714** sections all-OK — no drift from spawn. Near-miss failing rules **326** (+4 vs spawn 322).

**Top mono-class levers:** `expected_ipa` editorial slash (**8** sections) → [115](../issues/115-correction-pass-editorial-slash-prose-residue.md); `expected_ipa` paren modifiers (**8**) → [116](../issues/116-correction-pass-paren-optional-modifiers.md); `invalid_ipa` prenasal `ⁿ` (**6**) → [117](../issues/117-correction-pass-prenasal-prefix.md); `expected_range_dots` dot-affricate (**3**) → [118](../issues/118-correction-pass-dot-affricate-notation.md).

**Defer:** Khoisan §20.x clicks (47 rules, spike-64 policy); `prose_double_slash_env` env-paren `//` (2 mono-class, distinct from resolved 108); Yup'ik `V.V` geminate (0 `expected_range_dots` rows — failures are `//` + `ⁿ` instead).

**Map updated** with 115→118 queue.

## References

- [Correction pass template](13-correction-pass-template.md)
- [Inventory summary](../inventory/rule-inventory-summary.md)
- [Spike 106 findings](../research/near-miss-correction-prioritization.md) (superseded queue; ranking policy amended in map)
- [Spike 64 findings](../research/syntax-other-near-miss-sections.md) (Khoisan / range-dots defer notes)
