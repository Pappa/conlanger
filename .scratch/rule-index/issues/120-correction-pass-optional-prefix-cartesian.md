Type: task
Status: resolved
Blocked by: None

# Correction pass: optional-prefix cartesian (structural I/O optionals)

Spawned from [grill 113 follow-up](113-human-review-io-optional-residuals.md) and [grill 71](71-grill-paren-and-parallel-set-notation.md) (2026-09-06). Owner confirmed: compile-time cartesian for `(Class[features])suffix` shapes; `#`-in-I/O rows stay in [113](113-human-review-io-optional-residuals.md) for manual correction.

## Problem

Ticket [51](51-correction-pass-input-optionals-to-env.md) `_expand_prefix_structure_optional` emits `{inner}rest` — a **required** prefix set member. Faithful zero-or-one semantics need `{inner+rest, rest}` (same as ticket [48](48-correction-pass-parenthetical-segment-notation.md) `(G)V` → `{GV,V}`).

`(V[-long])N` was explicitly deferred via `_DEFERRED_STRUCTURAL_OPTIONAL_RE` after the unfaithful `{V[-long]}N` wrap was removed ([111](111-correction-pass-cartesian-io-optionals.md)).

## What to build

1. **`input_optionals.py`:** optional structural prefix `(X)rest` → cartesian `{Xrest, rest}` (not `{X}rest`).
2. **Recognize** class+Index-bracket inners (`V[-long]`, `C[+voice]`, …) as structural optionals; remove `V[-long]` from deferral (keep `{C,#}V` deferred — [113](113-human-review-io-optional-residuals.md)).
3. **Colon matrix on prefix inner** when Index uses postfix brackets: `V[-long]` → `V:[-long]` in the cartesian member (ASCA apply fidelity; see [CONTEXT.md](../../CONTEXT.md) **Feature matrix**).
4. **Tests:** unit cases + shape-faithful apply probe for `Arapaho-V-longN` / `Gros-Ventre-V-longN` (`{V:[-long]N,N} > ∅ / _#` on `kaN`, `kN`).

## Acceptance criteria

- [x] `(V[-long])N` → `{V:[-long]N,N}` via `expand_meta_notation`
- [x] `(V:[+long])θt` → `{V:[+long]θt,θt}` (fixes unfaithful `{V:[+long]}θt` wrap)
- [x] `({C,#}V)ʔ` still passes through unchanged (deferred)
- [x] Apply probes for Arapaho/Gros Ventre `V-longN` rows
- [x] Update [113](113-human-review-io-optional-residuals.md) — `V-longN` rows resolved; `#` rows remain

## Answer

**Shipped 2026-09-06.** `input_optionals._expand_prefix_structure_optional` cartesian-expands class/matrix optional prefixes to `{prefix+suffix,suffix}`; Index `V[-long]` → `V:[-long]` in emitted set members. Braced-literal prefix inners (`{foo}`) keep legacy `{foo}suffix` wrap.

## References

- [io-optionals research §5](../research/io-optionals-asca-and-convention.md)
- `src/conlanger/tools/compile/asca/input_optionals.py`
- Grill session 2026-09-06 (feature-matrix convention)
