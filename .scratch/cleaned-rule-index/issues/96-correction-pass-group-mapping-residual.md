Type: task
Status: resolved
Blocked by: 95

# Correction pass: group-mapping residuals (post-boundaries)

Target cluster: `unknown_grouping` — **mapped** class letters still literal after [ticket 95](95-correction-pass-group-mapping-boundaries-unglued.md) boundary + unglued pass. Expected **~10** in-scope rows (~15% of the 68 CSV-native rows in [grouping_errors.csv](../inventory/grouping_errors.csv)); exact set depends on 95 outcome.

Spawned from grouping-errors investigation (2026-08-27). Follow-on only — do not start until 95 is **resolved** and `grouping_errors.csv` is refreshed.

## Problem

After 95, remaining in-scope failures are likely **not** solvable by another global boundary tweak alone:

| Likely pattern | Example | Notes |
| --- | --- | --- |
| Multi-occurrence | Token expanded in one field, literal in another (`Ci > … // R…R_#`) | Per-field pass may leave env literal |
| Partial cluster expansion | `{D,Dʱ}` — first **D** expands, **D** in `Dʱ` may still fail | Needs **after** `ʱ` (95 may fix) |
| Space-delimited glue | `Kç` after whitespace | Review **before** whitespace policy |
| Expansion OK, other ASCA error | Rule no longer `unknown_grouping` for target token but still `ok: false` | Inventory attribution, not group_mappings |
| Leftover glued edge | Residual **T**/**K** in §36.3.2 if 95 misses a prefix class | Cluster-specific test |

**Out of scope (still):** **M**, **X**, **I**, **Y** — not in `group_mappings.csv`.

## What to build

1. Re-extract in-scope rows from post-95 inventory into `grouping_errors.csv` (or equivalent filter).
2. Bucket each residual row by root cause (multi-field, punctuation edge, false positive in error_token, needs targeted regex, unfixable).
3. Implement **minimal** fixes — targeted tests per bucket; avoid a third global regex widening without spike evidence.
4. Full inventory re-run; record before/after in **Answer**.
5. If a bucket needs section-local abbrev or meta-notation (not group_mappings), file a new ticket instead of expanding scope here.

## Policy

- Prefer one vertical slice per bucket (test + fix + inventory row).
- No new `group_mappings.csv` rows without spike justification.
- Compile-layer only; ADR-0010.

## Acceptance criteria

- [x] Post-95 residual rows enumerated and bucketed in ticket body or linked research note
- [x] Each bucket either fixed with tests or explicitly deferred with new ticket / `wontfix` rationale
- [x] Full inventory re-run; `unknown_grouping` in-scope count in **Answer**
- [x] No regressions on 95 fixture set

## Residual buckets (post-95, 9 in-scope rows)

| Bucket | Rows | Root cause | Resolution |
| --- | ---: | --- | --- |
| Class letter before `ː` | 7 | Group mappings run pre-length-mark; `Eː`, `Dː`, `Bː`, `Uː` need `ː` in **After** | `group_mappings.py`: add `ː` to after punct set |
| `Kç` glued tail | 2 | `ç` was **Before** only (ticket 95); `K` before `ç` missed **After** | `group_mappings.py`: add `ç` to extra-modifier after set |
| Finnish `Uː` output | 1 | `U`→`%` then `%ː` not normalized (overlap ticket 79) | `length_marks.py`: `%ː` → `%:[+long]`; rule still fails `syntax_other` (ASCA syllable tone/stress) — out of `unknown_grouping` |

Out of scope unchanged: **M**, **X**, **I**, **Y** (21 rows).

## Answer

Compile-layer only (`group_mappings.py`, `length_marks.py`). **After** boundary gained length mark `ː` (pre-`:[+long]` tokens) and `ç` (symmetric with ticket 95 **Before**). Length pass gained `%ː` → `%:[+long]` for syllable-marker output after `U`→`%` expansion.

**Inventory (`uv run create_index`, 2026-08-27):**

| Metric | Post-95 | After 96 | Δ |
|--------|--------:|---------:|--:|
| OK | 8051 (83.2%) | 8059 (83.3%) | **+8** |
| Fail | 1096 (11.3%) | 1088 (11.2%) | **−8** |
| `unknown_grouping` (all) | 30 | 21 | **−9** |
| In-scope CSV/native letters | 9 | **0** | **−9 (100%)** |

Cleared rule_ids: `Luwian-D-R`, `Old-Norse-EːBː-Eːaː`, `Old-Norse-Eːu,oː-Eːaː`, `Old-Norse-BːB-aːo,a,æ,e-æ,eːæ,eː-æ,eːi-iːEː`, `Old-Norse-eːBː,iː`, `Old-Norse-eːBː,iː_2`, `bTshan-La-k-sk-kr-ɡ-Pɡ-sɡ-Nɡ-sɡr-çK-rK-Kç`, `lCog-Rtse-Nkj-sɡr-Kç-kr-skr-ɡr`. `Standard-Finnish-iU-OU` no longer `unknown_grouping` (`U`); residual `syntax_other` (ASCA syllable parameter) — not group_mappings.

`grouping_errors.csv` regenerated (21 rows, all M/X/I/Y).

## References

- [95 boundaries + unglued pass](95-correction-pass-group-mapping-boundaries-unglued.md)
- [grouping_errors.csv](../inventory/grouping_errors.csv)
- [Correction pass template](13-correction-pass-template.md)
