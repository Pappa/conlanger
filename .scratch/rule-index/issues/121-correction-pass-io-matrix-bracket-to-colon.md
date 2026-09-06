Type: task
Status: resolved
Blocked by: [120](120-correction-pass-optional-prefix-cartesian.md)

# Correction pass: I/O host+bracket matrices → ASCA colon form

Spawned from grill 113 follow-up (2026-09-06). Owner confirmed: **stages** keep Index postfix brackets (`V[+long]`); ASCA compile rewrites to colon form (`V:[+long]`).

## Problem

ASCA 0.10.2 accepts Index postfix brackets at **validate** time but **not** at apply time with the same semantics as colon matrices:

| Form | Linguistic meaning | ASCA input match | ASCA output substitute |
|------|-------------------|------------------|------------------------|
| `V:[-long]` | short vowel | ✓ | ✓ |
| `V[-long]` | (same) | ✗ / wrong | runtime `incomplete matrix` |

The corpus has hundreds of stage lines with class+bracket matrices (`V[-long]` ×140, `V[+nas]` ×130, …). Many inventory `ok` rules compile to `V:[+long] > V[-long]` and fail only at apply.

Ticket [120](120-correction-pass-optional-prefix-cartesian.md) colon-normalizes prefix inners inside the optional-prefix cartesian pass only. This ticket is the **general** I/O compile pass.

## What to build

1. **Compile pass** on input/output compile fields (post chain-expansion, alongside existing per-field transforms): rewrite host+bracket `X[features]` → `X:[features]` for class letters and IPA segments.
2. **Do not** rewrite standalone matrices (`[-long]`, `[+voice]`) unless probes require it.
3. **Env/exception:** out of scope for v1 (separate bucket; see [119](119-grill-distinctive-features-env-exception.md)).
4. **Shape-faithful apply probes:** `V:[+long] > V:[-long]`; input `V:[-long] > x` on short vowels.
5. **Inventory re-baseline** with ok/fail delta in **Answer**.

## Policy

- Index/applier-neutral YAML keeps bracket form ([CONTEXT.md](../../CONTEXT.md) **Feature matrix**).
- ASCA compiled strings use colon form.
- No spike — equivalence disproved by local ASCA 0.10.2 probes (grill 2026-09-06).

## Acceptance criteria

- [x] Pass runs on I/O compile fields after [120](120-correction-pass-optional-prefix-cartesian.md) optional-prefix work lands
- [x] `V[-long]` → `V:[-long]` on I/O; `raw` / **stages** unchanged
- [x] Apply probes for input matching and output substitution
- [x] Inventory metrics in **Answer**; `incomplete_matrix` cluster reduced where bracket-output was root cause

## Answer

**Shipped 2026-09-06.** `normalize_asca_host_bracket_matrices` rewrites host+bracket matrices (`V[-long]`, `C[+voice]`, `a[+nas]`, …) to colon form on **compiled input/output only** (after `expand_meta_notation`; env/exception unchanged). Skips Oceanic `aCV[+ high]`-style templates (`(?<![aeiou]C)[A-Z][` guard + no-uppercase IPA hosts). Shared `host_bracket_matrix_to_colon` also used by optional-prefix cartesian ([120](120-correction-pass-optional-prefix-cartesian.md)).

- **Inventory:** OK **8825 → 8837 (+12)**; fail **706 → 694 (−12)**; sections all-OK **441 → 442 / 714**. `incomplete_matrix` **13 → 3 (−10)** — Indo-Aryan `C[+voice]` output, Creek `P[+voice]`, Chilcotin `V[+rtr]`, Adángbe/Kansa `V[+nas]`, Basque `P[+voice]`, Lycian `F[+voice]` output recovered; residual 3 are unrelated insertion/runtime shapes.
- **Apply probes:** `Vː > V[-long]` substitutes long→short; `V[-long] > x` matches short vowels (ASCA 0.10.2).

## References

- [index-feature-matrices research](../research/index-feature-matrices-to-asca-targets.md)
- [asca-rule-validity.md](../research/asca-rule-validity.md) §2 (segment+matrix colon syntax)
- `src/conlanger/tools/compile/asca/pipeline.py`
