Type: task
Status: resolved
Blocked by: 12

# Correction pass: group-mapping boundaries + unglued class letters

Target cluster: `unknown_grouping` — **mapped** Index class letters from `data/asca/group_mappings.csv` that remain literal in compiled rules because `apply_asca_group_mappings_to_string` boundary regexes miss the token context. Baseline artifact: [unknown_grouping_errors.csv](../inventory/unknown_grouping_errors.csv) (**89** rows total; **68** in scope for CSV/native letters; **21** out of scope — **M**, **X**, **I**, **Y** — ignore).

Spawned from grouping-errors investigation (2026-08-27). Supersedes ticket [43](43-correction-pass-unknown-grouping-t.md) **Phase 2** policy: lowercase-glued uppercase class letters (**`rK`**, **`sTP`**, **`nQ`**, **`hR`**) **must expand** — a mapped uppercase letter in a rule segment is always the class, not part of a literal digraph with the neighbouring lowercase IPA segment.

## Problem

CSV rows and expansion targets are correct ([spike 09](../issues/09-spike-asca-class-letter-feature-matrices.md), [research](../research/asca-class-letter-mappings.md)). Failures are **boundary recognition** in [`group_mappings.py`](../../../src/conlanger/tools/compile/asca/group_mappings.py).

In-scope error tokens at baseline: **R** (26), **U** (11), **T** (8), **E** (6), **B** (5), **K** (5), **H** (4), **D** (2), **Q** (1).

### Root causes (two fixes, one ticket)

**A — Widen before/after char sets (~41 rows estimated)**

| Gap | Examples | Fix |
| --- | --- | --- |
| **Before:** digit / `)` | `V3R`, `(C,0)U`, `#_(j)B` | Add `0-9`; allow `)` as valid **before** |
| **Before:** ellipsis, `ʔ`, `ç` | `…U:[+stress]`, `ʔR`, `çT`/`çK` | Add `…`, `ʔ`, `ç` |
| **Before:** `]` | `]Bʱ`, `XC_j` after matrix | Add `]` |
| **After:** `(` | `_%U(%,0)#` | Add `(` |
| **After:** `β`, `ʱ`, `ŋ`, `…` | `Eβu`, `Bʱ`, `Dʱ`, `UŋA`, `R…R` | Add modifier chars |

**B — Unglued second pass (~14 rows estimated)**

After the normal pass, expand any **remaining** mapped uppercase letter when the **after** boundary passes, **without** a **before** check. Covers lowercase IPA prefix (**`rK`**, **`sTP`**, **`nQ`**, **`hR`**, **`jE`**, **`iHn`**, **`iU`**, **`wI`**) and ticket 43 glued-cluster residuals.

**Policy (2026-08-27):** `Kr` and `rK` both expand **K** → `C:[-front,+back,+hi,-lo]`; flip regression test `rK > k` from unchanged to expanded.

**Still blocked:** subscript digits (`C₁`, `S₁`) — subscript not in **after** boundary.

## What to build

1. Extend `_CLASS_BEFORE` / `_CLASS_AFTER` (and labialized variant) per table above; keep named constants + module comment ([docs/system/sound-change-applier.md](../../../docs/system/sound-change-applier.md) § Class-letter expansion boundaries).
2. Add **unglued** pass after optional-labial / suffix-labial / bare passes (ticket 43 option 2, now mandatory).
3. Unit tests in `tests/conlanger/tools/test_group_mappings.py` — fixtures from [unknown_grouping_errors.csv](../inventory/unknown_grouping_errors.csv) in-scope rows (minimum: digit-ref **R**, ellipsis **U**, `_%U(`, `çT`, `rK`, `sTP`, `nQ`, `hR`, `Eβu`, `Bʱ`, `{D,Dʱ}` first member).
4. Full inventory re-run (`uv run create_index`); refresh `unknown_grouping_errors.csv`; record before/after in **Answer**.

## Out of scope

- **M**, **X**, **I**, **Y** — not in `group_mappings.csv`; separate tickets / clusters.
- New CSV rows.
- `apply_section_local_abbreviations` (stub).

## Policy

- Compile-layer only; `raw` and index YAML unchanged (ADR-0010).
- No changes to `group_mappings.csv` — regex + unglued pass only.

## Acceptance criteria

- [x] Before/after char sets extended with documented rationale per char class
- [x] Unglued second pass implemented; `rK` expands **K** (test updated)
- [x] `C₁`, `S₁` regressions unchanged
- [x] Ticket 23 labialization regressions unchanged (`Kʷ`, `K(ʷ)`, …)
- [x] Full inventory re-run; in-scope `unknown_grouping` count in **Answer** (target **~55–58 / 68** in-scope rows cleared, ~**85%**)
- [x] `unknown_grouping_errors.csv` regenerated or diff noted

## Answer

Compile-layer only (`group_mappings.py`). Before-set gained digits, `)`, `]`, `…`, `ʔ`, `ç`; after-set gained `(`, `…`, and extra modifiers `β` `ʱ` `ŋ` (outside IPA-ext `U+0250–U+02AF`). Unglued pass expands remaining mapped letters whose previous char is **not** a Before delimiter (so `rK` / `sTP` expand without re-expanding mapping results such as `S` → `P`). `rK > k` regression now expects `rC:[-front,+back,+hi,-lo] > k`. Subscripts and labialization tests unchanged.

**Inventory (ASCA 0.10.2, `uv run create_index` 2026-08-27):**

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK | 8004 (82.7%) | 8051 (83.2%) | **+47** |
| Fail | 1143 (11.8%) | 1096 (11.3%) | **−47** |
| Sections all OK | 348 / 691 (50.4%) | 351 / 691 (50.8%) | **+3** |
| `unknown_grouping` (all) | 89 | 30 | **−59** |
| In-scope CSV/native letters | 68 | 9 | **−59 (87%)** |

In-scope tokens cleared: **R** 26→0, **T** 8→0, **H** 4→0, **Q** 1→0, **U** 11→1, **E** 6→2, **B** 5→3, **K** 5→2, **D** 2→1. Out of scope **M/X/I/Y** unchanged (21).

12 of the 59 token-clears still fail under other classes (47 ok-flips). Residual 9 in-scope rows (ticket 96): Old-Norse/Luwian class letter before `ː` (not in After at mapping time); rGyalrongic `Kç` (`ç` in Before only); Finnish output `Uː`.

`unknown_grouping_errors.csv` regenerated (30 rows).

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: unknown_grouping](14-correction-pass-unknown-grouping.md)
- [Correction pass: residual `T`](43-correction-pass-unknown-grouping-t.md) — Phase 1 shipped; Phase 2 policy superseded here
- [Correction pass: labialized class letters](23-correction-pass-labialized-class-letters.md)
- [unknown_grouping_errors.csv](../inventory/unknown_grouping_errors.csv)
- [asca-class-letter-mappings research](../research/asca-class-letter-mappings.md)
