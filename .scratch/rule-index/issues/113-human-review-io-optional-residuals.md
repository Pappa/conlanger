Type: task
Status: resolved
Blocked by: None

# Human review: `#`-in-I/O optional-prefix residuals

Spawned from [grill 71](71-grill-paren-and-parallel-set-notation.md) Q6. Ticket [111](111-correction-pass-cartesian-io-optionals.md) **removed** unfaithful auto-expansion for these shapes. Originally tracked four rule ids; `(V[-long])N` is **resolved** by compile pass [120](120-correction-pass-optional-prefix-cartesian.md) (2026-09-06). This ticket now tracks **owner decision** for the two `{C,#}` optional-prefix rows only.

## Problem

| Pattern | Status | Why not auto-compile |
|---------|--------|----------------------|
| `(V[-long])N` | **Resolved** — [120](120-correction-pass-optional-prefix-cartesian.md) | Was `{V[-long]}N` (required prefix); now `{V:[-long]N,N}` |
| `({C,#}V)ʔ` | **Open** — human review | Index `#` = null consonant slot, not ASCA word boundary; `{C,#,V}ʔ` fails at apply |

## Corpus rows

| Rule id | HTML line | Index `raw` | Decision |
|---------|-----------|-------------|----------|
| `Arapaho-V-longN` | 1684 | `(V[-long])N → ∅ / _#` | **Compile** — [120](120-correction-pass-optional-prefix-cartesian.md): `{V:[-long]N,N} > ∅ / _#` |
| `Gros-Ventre-V-longN` | 1704 | `(V[-long])N → ∅ / _#` | **Compile** — [120](120-correction-pass-optional-prefix-cartesian.md): `{V:[-long]N,N} > ∅ / _#` |
| `Arapaho-C,#Vʔ` | 1676 | `({C,#}V)ʔ → ({C,#}Vː)∅ / _C` | **Pending** — owner: correction, `manual_mappings`, skip, or rule split |
| `Gros-Ventre-C,#V-longʔ` | 1698 | `({C,#}V[-long])ʔ → ({C,#}Vː[+falling tone])∅ / _C` | **Pending** — owner: correction, `manual_mappings`, skip, or rule split |

`#` in **env** (`_{C,#}`, `C_{C,#}`) is fine — out of scope.

Faithful cartesian for `({C,#}V)ʔ` is likely `{CVʔ,Vʔ,ʔ}` (treat `{C,#}` as `{C,∅}` → `{CV,V}`), not any form that emits literal `#` in I/O. See [io-optionals research §5](../research/io-optionals-asca-and-convention.md).

## What to do (human)

For the two **Pending** rows only:

1. Choose: **Index Diachronica correction**, **`manual_mappings`**, **`status: skipped`**, or faithful multi-rule split.
2. Do **not** re-enable ticket 51 auto-expand for `({C,#}V)ʔ`.
3. Record chosen encoding and apply probe in **Answer** when done.

## Acceptance criteria

- [x] `Arapaho-V-longN` / `Gros-Ventre-V-longN` — compile encoding documented ([120](120-correction-pass-optional-prefix-cartesian.md))
- [x] `Arapaho-C,#Vʔ` / `Gros-Ventre-C,#V-longʔ` — documented owner decision
- [x] Corrections / manual mappings keyed by **rule id** (if chosen for `#` rows)
- [x] Inventory reflects decision for `#` rows (ok, skipped, or documented residual)
- [x] [111](111-correction-pass-cartesian-io-optionals.md) no longer emits unfaithful wraps for these patterns

## Answer

### Resolved (2026-09-06) — `(V[-long])N` via [120](120-correction-pass-optional-prefix-cartesian.md)

| Rule id | Compiled input | Apply probe |
|---------|----------------|-------------|
| `Arapaho-V-longN` | `{V:[-long]N,N} > ∅ / _#` | `kaN`, `kiN`, `kN` at `_#` |
| `Gros-Ventre-V-longN` | `{V:[-long]N,N} > ∅ / _#` | same shape |

No `manual_mappings` or index correction. `stages` unchanged; compile pass only.

### Open — `({C,#}V)ʔ` rows

Owner decision pending. Candidate faithful input: `{CVʔ,Vʔ,ʔ}` (and analogous for `V[-long]` variant on Gros Ventre row) — confirm before encoding.

## References

- [Grill 71 Q4/Q6](71-grill-paren-and-parallel-set-notation.md)
- [Optional-prefix cartesian (120)](120-correction-pass-optional-prefix-cartesian.md)
- [io-optionals research §5](../research/io-optionals-asca-and-convention.md)
- [Correction pass: input optionals](51-correction-pass-input-optionals-to-env.md)

## Comments

> 2026-09-02: Filed from closed grill 71. Owner deferred to human review (not agent cartesian pass).

> 2026-09-06: `(V[-long])N` rows resolved by compile pass [120](120-correction-pass-optional-prefix-cartesian.md). Ticket narrowed to `#`-in-I/O optional-prefix rows; corpus table and acceptance criteria updated.
