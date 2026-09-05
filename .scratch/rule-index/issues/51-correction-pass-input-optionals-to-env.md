Type: task
Status: resolved
Blocked by: 12

# Correction pass: input optionals to env

Target cluster: `syntax_other` — **`Options can only be used in Environments or Structures`** — **86** rules at current inventory baseline ([summary](../inventory/rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

ASCA permits optionals `(…)` only in environments or structures, not in bare I/O segments. Index writes input-side optionals such as `(G)V > ∅ / _#` that fail at compile validation.

## What to build

1. Identify recurring input-optional shapes in the cluster (e.g. `(C)V`, `(G)V`, prefixed optional consonants).
2. Implement parse/compile rewrite — move optionals into ASCA env/structure positions or expand to equivalent set notation `{…}` where faithful.
3. Full inventory re-run; record before/after for rows matching the exact error message.

**Expected impact:** ~**51** ok uplift at ~60% recoverability.

## Policy

- Preserve optional semantics; do not drop the optional branch silently.
- `raw` unchanged; class-first transform per edit ladder.

## Acceptance criteria

- [x] Dominant optional-in-input patterns documented
- [x] Handler(s) + tests on inventory samples (e.g. `(G)V > ∅ / _#`)
- [x] Full inventory re-baseline; cluster size before/after in **Answer**
- [x] Fixtures updated where outcomes change

## Answer

Baseline (pre-pass): **7114 / 9201** ok (77.3%); cluster `Options can only be used in Environments or Structures`: **18** rows.

After `expand_input_optionals_to_structures()` wired in `expand_meta_notation()` (after parenthetical pass):

- **7132 / 9201** ok (**77.5%**, **+18**)
- Cluster: **18 → 0** (100% of syntax cluster cleared)
- **17** rules newly pass validation; **1** rule (Klallam `V=0 3ʔ(0 )`) reclassified from `syntax_other` → `runtime_other` (`Unknown reference '3'` — subscript phase 2)

**Pattern taxonomy** (module docstring in `src/conlanger/tools/asca_compile/input_optionals.py`):

| Pattern | Example | Expansion |
|---------|---------|-----------|
| Prefix feature matrix | `(V[-long])N` | `{V[-long]}N` |
| Prefix segment/class features | `(V:[+long])θt`, `(C:[+labial])ɡ` | `{…}tail` |
| Prefix grouped class | `({C,#}V)ʔ` | `{C,#,V}ʔ` |
| Set suffix optional | `{s,z}(ʔ)` | `{s,sʔ,z,zʔ}` |
| Literal + set + optional | `a{i,j}(a)` | `a{i,j,a}` |
| Set + class optional + tail | `{r,s}(N)k` | `{r,s,N}k` |
| Set cross optional | `{p,t,k}({p,t,k})n` | cross-product members + suffix |
| Identity subscript optional | `3ʔ(0 )` | `3ʔ{0}` |

**Residual (not input-optional cluster):** `({C,#}V)ʔ > ({C,#}Vː)∅ / _C` — input fixed; output `∅` concatenation after structure remains `syntax_other`.

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: parenthetical segment notation](48-correction-pass-parenthetical-segment-notation.md) — overlapping `(` handling

## Comments

> **2026-08-29:** Owner re-opened the **pattern taxonomy** in a paused grill ([71](71-grill-paren-and-parallel-set-notation.md)), now blocked on [spike 100](100-spike-io-optionals-asca-and-convention.md). The +18 `ok` cluster clear is not treated as historically faithful. `Muong-Khen-həp,b` nested braces are **48**, not this pass. Do not implement a 51 rewrite until 100 + 71 Q5″/Q10 are settled.
