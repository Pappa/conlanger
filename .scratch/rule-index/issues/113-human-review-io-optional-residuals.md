Type: task
Status: ready-for-human
Blocked by: None

# Human review: unfaithful I/O optional residuals

Spawned from [grill 71](71-grill-paren-and-parallel-set-notation.md) Q6. Ticket [111](111-correction-pass-cartesian-io-optionals.md) **removes** auto-expansion for these patterns; this ticket tracks **owner-authored** faithful encodings.

## Problem

Two Index optional-prefix shapes cannot be solved by cartesian flatten alone:

| Pattern | 51 today | Why auto-expand fails |
|---------|----------|------------------------|
| `(V[-long])N` | `{V[-long]}N` | Makes matrix prefix **required**; optional semantics lost (Gros Ventre `Gros-Ventre-V-longN` false-green `ok`) |
| `({C,#}V)ʔ` | `{C,#,V}ʔ` | `#` in I/O invalid at ASCA **apply** (`Word Boundaries cannot be in the input or output`) |

## Corpus rows (review)

| Rule id | HTML line | Index `raw` |
|---------|-----------|-------------|
| `Arapaho-V-longN` | 1684 | `(V[-long])N → ∅ / _#` | **Resolved** — [120](120-correction-pass-optional-prefix-cartesian.md) |
| `Gros-Ventre-V-longN` | 1704 | `(V[-long])N → ∅ / _#` | **Resolved** — [120](120-correction-pass-optional-prefix-cartesian.md) |
| `Arapaho-C,#Vʔ` | 1676 | `({C,#}V)ʔ → ({C,#}Vː)∅ / _C` |
| `Gros-Ventre-C,#V-longʔ` | 1698 | `({C,#}V[-long])ʔ → ({C,#}Vː[+falling tone])∅ / _C` |

`#` in **env** (`_{C,#}`, `C_{C,#}`) is fine — out of scope.

## What to do (human)

1. For each row, choose: **Index Diachronica correction**, **`manual_mappings`**, **`status: skipped`**, or faithful multi-rule split.
2. Do **not** re-enable ticket 51 auto-expand for these shapes.
3. Record chosen encoding and apply probe in **Answer** when done.

## Acceptance criteria

- [ ] All four rule ids have documented owner decision
- [ ] Corrections / manual mappings keyed by **rule id**
- [ ] Inventory reflects decision (ok, skipped, or documented residual)
- [ ] [111](111-correction-pass-cartesian-io-optionals.md) no longer emits unfaithful wraps for these patterns

## References

- [Grill 71 Q4/Q6](71-grill-paren-and-parallel-set-notation.md)
- [io-optionals research §5](../research/io-optionals-asca-and-convention.md)
- [Correction pass: input optionals](51-correction-pass-input-optionals-to-env.md)

## Comments

> 2026-09-02: Filed from closed grill 71. Owner deferred to human review (not agent cartesian pass).
