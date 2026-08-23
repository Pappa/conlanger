Type: task
Status: resolved
Blocked by: 20

# Correction pass: labialized Index class letters (Kʷ, K(ʷ), …)

Target cluster: `unknown_grouping` / `syntax_other` — Index labialization suffix `ʷ` (U+02B7) on class letters (~18+ rules).

## Problem

Index Diachronica marks labialized class letters with a trailing `ʷ` (`Kʷ`, `Qʷ`, `Cʷ`) or optional `(ʷ)` in sets (`{P,K(ʷ),s}`). `apply_asca_group_mappings_to_string()` only expanded bare letters; `Kʷ` left literal `K` for ASCA → **Unknown grouping 'K'**. ASCA rejects `matrixʷ`; labialization is `:[+round]` on the feature matrix.

## What was built

- Extended compile-time group mapping in `rules.py`:
  1. `L(ʷ)` → `{L_labialized,L}`; flattened when already inside a set (ASCA rejects nested `{}`)
  2. `Lʷ` → labialized mapping (`Kʷ` → `C:[-front,+back,+hi,-lo,+round]`)
  3. Native ASCA groupings (`Cʷ` → `C:[+round]`) via `_ASCA_NATIVE_GROUPINGS`
  4. Boundary rules unchanged (`Kr`, `rK`, ASCII `Kw` not matched)

## Acceptance criteria

- [x] Compile transform with TDD tests on representative fixtures
- [x] Smoke before/after metrics recorded
- [x] Full test suite green

## Answer (before/after)

Baseline (after issue 22): **6237 / 9316** ok (67.0%); **120 / 714** sections all OK.

Full inventory re-run with labialized class-letter compile transform:

- **6254 / 9316** ok (**+17** rules)
- `unknown_grouping` **85 → 70** (−15); top `K` token removed from failure table
- Remaining `K` failures are mostly ASCII `Kw` (correctly preserved) or unrelated syntax
