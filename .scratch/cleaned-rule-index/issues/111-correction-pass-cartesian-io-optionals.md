Type: task
Status: resolved
Blocked by: None

# Correction pass: cartesian I/O optionals (grill 71 successor)

Target cluster: `nested_brackets` — bucket D optional-prefix / parallel-column shapes deferred by [70](70-correction-pass-flatten-nested-io-sets.md) and [grill 71](71-grill-paren-and-parallel-set-notation.md). Findings: [io-optionals-asca-and-convention.md](../research/io-optionals-asca-and-convention.md).

## Problem

Ticket [48](48-correction-pass-parenthetical-segment-notation.md) cartesian-expands Index I/O optionals but **nests** `{…}` inside `{…}` when a parallel column follows — ASCA `NestedBrackets`. Ticket [51](51-correction-pass-input-optionals-to-env.md) cleared `OptLocError` with several **unfaithful** wraps; grill 71 owner-confirmed re-scope (2026-09-02).

| Index shape | Family | 48 today | Target |
|-------------|--------|----------|--------|
| `(h)ə{p,b}` | A — optional segment prefix + `{…}` | `{hə{p,b},ə{p,b}}` | `{həp,həb,əp,əb}` |
| `e(C){V[…]}` | A | nested | flat cartesian (one set) |
| `(j){u,ʌ}` | A (output-side Scots) | `{j{u,ʌ},{u,ʌ}}` | `{ju,jʌ,u,ʌ}` |
| `(G)V` | A | `{GV,V}` via 48 | unchanged |
| `k(ʰ){r,j}` | B — modifier + `{…}` | `{k{r,j},kʰ{r,j}}` | `{k,kʰ}{r,j}` adjacent sets |
| `ɡ(ʷ)` | B (lone modifier) | `{ɡ,ɡʷ}` | unchanged |

**Do not** emit native Index `(C)a` on I/O or `<>` wrappers on I/O (grill Q5″/Q10). Env `(C)_` and syllable structures ([98](98-correction-pass-syllable-position-u-hash.md)) stay separate.

## What to build

1. **String-layer compile pass** after [48](48-correction-pass-parenthetical-segment-notation.md), before or integrated with re-scoped [51](51-correction-pass-input-optionals-to-env.md) — ticket [105](105-implement-compile-field-intermediate-representation.md) explicitly defers these shapes to strings until IR v2.
2. **Family A:** prefix cartesian × parallel column → **one flat `{…}`** (no nested braces).
3. **Family B:** modifier cartesian then **adjacent sets** when an independent `{…}` column follows (`{k,kʰ}{r,j}`).
4. **51 re-scope — keep:**
   - `{s,z}(ʔ)` → `{s,sʔ,z,zʔ}`
   - `{r,s}(N)k` → `{rk,rNk,sk,sNk}` (zero-or-one insert per set member; not `{rN,sN}k` or `{r,s,N}k`)
   - `(G)V` → 48 only
5. **51 re-scope — replace:**
   - `a{i,j}(a)` → `a{i,j,ia,ja}` (prefer **partial structure** with literal prefix when faithful; flat `{ai,aj,aia,aja}` equivalent)
6. **51 re-scope — remove auto-expand** (defer to [113](113-human-review-io-optional-residuals.md)): `(V[-long])N`, `({C,#}V)ʔ`
7. **Shape-faithful apply probes** in tests (not inventory `ok` alone) — grill Q7.

### Corpus probes (minimum)

| Rule id | Probe |
|---------|-------|
| `Muong-Khen-həp,b` | `{həp,həb,əp,əb} > t / _l` applies `həpl` → `tl` |
| `Scots-—-øː_3` | `{ju,jʌ,u,ʌ}` output validates; no `NestedBrackets` |
| `Naxi-r,sNk` | `{rk,rNk,sk,sNk} > k / _V` with class `N` expanded |
| Amdo `k(ʰ){r,j}` | `{k,kʰ}{r,j} > tɕ` applies `kr` → `tɕ` |

## Policy

- ADR-0010 / historical fidelity: cartesian encodings must match Index **zero-or-one segment** semantics (grill Q2).
- `raw` unchanged.
- Inventory `ok` on identity or weak probes is insufficient (spike 100 §7).

## Acceptance criteria

- [x] New pass (or 48 extension) emits flat Family A sets and adjacent Family B sets
- [x] 51 re-scoped per §What to build; `(V[-long])N` and `({C,#}V)ʔ` no longer auto-expanded
- [x] Unit tests with shape-faithful apply probes on corpus rows above
- [x] Full inventory re-baseline; `nested_brackets` bucket D rows recovered; metrics in **Answer**
- [x] No `<>` emission on I/O in this pass

## References

- [Grill 71 Answer](71-grill-paren-and-parallel-set-notation.md)
- [Parse fix Indo-Aryan](112-parse-fix-indo-aryan-optional-stages.md) — separate ticket
- [Human-review residuals](113-human-review-io-optional-residuals.md)
- `src/conlanger/tools/compile/asca/parenthetical.py`, `input_optionals.py`, `planned.py`

## Comments

> 2026-09-02: Filed from closed grill 71. Owner confirmed spike 100 Q5″/Q6/Q10 and Round 2–3 decisions.

## Answer

**Shipped 2026-09-02.** New compile pass `flatten_cartesian_io_optionals` runs after ticket 48 parenthetical expansion and before re-scoped ticket 51 input optionals (`planned.expand_meta_notation`).

### Implementation

- **Family A:** `{hə{p,b},ə{p,b}}` → `{həp,həb,əp,əb}`; same for `(j){u,ʌ}`, `e(C){V[…]}`.
- **Family B:** `{k{r,j},kʰ{r,j}}` → `{k,kʰ}{r,j}` adjacent sets.
- **51 re-scope:** `a{i,j}(a)` → `a{i,j,ia,ja}`; deferred `(V[-long])N` and `({C,#}V)ʔ` (→ [113](113-human-review-io-optional-residuals.md)).
- **Tests:** shape-faithful apply probes for Muong-Khen, Scots, Naxi, Amdo corpus rows.

### Inventory

Pre-pass summary: **8380 / 9840 ok (85.2%)**; `nested_brackets` **28**.

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK / total | 8380 / 9840 (85.2%) | **8385 / 9840 (85.2%)** | **+5 ok** |
| Fail | 848 | **843** | **−5** |
| `nested_brackets` | 28 | **20** | **−8** |

**ok flips (+7):** `:2398` Muong-Khen, `:3124` Hiw, `:3737` Vera'a, `:5900` Scots, `:6327` Old Norse, `:12290` Amdo, `:14327` Scots Vowel Shifts.

**Expected ok→fail (−2):** `:1684` Arapaho, `:1704` Gros Ventre — `(V[-long])N` no longer auto-expanded (deferred to [113](113-human-review-io-optional-residuals.md)).
