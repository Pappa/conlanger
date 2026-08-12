Type: grilling
Status: resolved

# Grill: optional outputs + seeded randomness (with sporadic)

## Question

Index rules like `d → {∅,ð} / V_V` encode speaker variation (including null). ASCA 0.10.2 rejects `∅` inside sets. How should the cleaned corpus and ASCA compile/render path retain alternatives and choose one for emission — and how should the **same seeded-randomness design** also cover **sporadic** rules (apply vs skip) — without making unit tests unable to exercise every branch?

## Settled (grill closed 2026-08-12; owner confirmed)

### Detection & corpus
- **Optional outputs** ≠ **sporadic** — `CONTEXT.md`.
- **Gate:** input not a whole-field set + output is a whole-field set (e.g. `d → {∅,ð}`). Not paired `{a,b} → {c,d}`.
- Uneven zip / UnevenSet shapes: unresolvable as written — other cluster. Nested sets: separate issue.
- **YAML SoT unchanged:** opaque set in **stages**; resolve at compile (do not split corpus rules). Ticket 60 parallel-column nulls still out of scope for set-internal `∅`.

### `SoundChangeRule` shape & randomness
- On instantiation: build `alternatives: list[SoundChangeRule]` (full peers; leaves have no children).
- Then pick **one** alternative **uniformly** at random as the parent’s compiled output/`value`.
- Optional ctor `seed` / caller `Random` → use **`random.Random`** (not process-global `random.seed`). If omitted: unseeded `Random()` (nondeterministic parent pick).
- `str()` renders the frozen choice (no re-sample).
- Tests validate members of `alternatives` independently.

### Inventory
- Column **`alt_idx`** immediately after `rule_idx`.
- When alternatives exist: emit **only** alternative rows (`alt_idx` 0-based in Index/set order). Do **not** inventory the parent’s random pick.
- When no alternatives: one row, **`alt_idx` empty**.
- Changelog / uniqueness: `(source, alt_idx)`.

### Sporadic & follow-ups
- **Defer** sporadic apply/skip sampling; keep RNG plumbing reusable.
- Filed: [66 implement](66-implement-optional-outputs-alt-idx.md), [67 nested sets spike](67-spike-nested-sets.md), [68 sporadic sampling](68-sporadic-sampling.md).

## Facts (do not re-litigate)

- ASCA rejects `d > {∅,ð} / V_V`; `d > ∅ / V_V` and `d > ð / V_V` are valid.
- Today: `SoundChangeRule` freezes `value` in `__init__`; ignores `sporadic`; no RNG on render path.
- Changelog today keys on unique `source` only — must move to `(source, alt_idx)`.

## Answer

Owner confirmed the settled design (2026-08-12). Implementation and deferred work:

1. [66 — Implement optional outputs + `alt_idx` + instance RNG](66-implement-optional-outputs-alt-idx.md) (`ready-for-agent`)
2. [67 — Spike: nested sets](67-spike-nested-sets.md) (`needs-triage`, blocked by 66)
3. [68 — Sporadic sampling](68-sporadic-sampling.md) (`needs-triage`, blocked by 66)

## References

- [Ticket 60](60-correction-pass-parallel-column-null.md) — set-internal `∅` out of scope
- [Ticket 19](19-correction-pass-sporadic-qualifier.md) — sporadic flag; sample/skip still aspirational
- ASCA 0.10.2 Insertion/Deletion; LonelySet notes in [asca-rule-validity.md](../research/asca-rule-validity.md)
