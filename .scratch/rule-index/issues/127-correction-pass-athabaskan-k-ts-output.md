Type: task
Status: ready-for-agent
Blocked by: None

# Correction pass: Athabaskan K→TS multi-segment output

Target cluster: `incomplete_matrix` — **1** rule ([Proto-Southern-Athabaskan-K](../inventory/error_clusters/incomplete_matrix_errors.csv)).

Spawned from wayfinder session on [Cleaned rule index SoT](../map.md) (2026-09-08). Distinct from [124 merge adjacent matrices](124-correction-pass-merge-adjacent-matrices.md) (Sebirwa `][` merge) and [125–126 grouping insertion](125-grill-asca-grouping-insertion.md) (Cypriot `∅ > F`).

## Problem

Index `K → TS` compiles to:

```text
C:[-front,+back,+hi,-lo] > P:[-voice]P
```

Per-letter group expansion (`T` → `P:[-voice]`, `S` → `P`) glues two ASCA **plosive grouping** tokens. ASCA 0.10.2 rejects this at apply time (`An incomplete matrix cannot be inserted`). Spacing does not help (`P:[-voice] P` also fails).

**Legal output shapes** (local probes): IPA multi-segment or affricate, e.g. `t s`, `t:[-voice]s`, `ts` — not adjacent `P` groupings.

## What to build

1. Fix **rule id** `Proto-Southern-Athabaskan-K` (`index_diachronica_original.html:10157`, section 29.1.1.1.19) so compiled output uses **concrete IPA segments**, not letter-by-letter class expansion of `TS`.
2. **Preferred:** `index_diachronica_corrections.yml` overlay keyed by rule id — output stage `TS` → IPA per Hoijer (1938) intent (likely /ts/ or voiceless stop + /s/; confirm against citation before locking).
3. **Alternative:** section-local `compiler_config.yml` mapping for `TS` → `ts` / `{t,s}` **before** `T`/`S` group-letter split, if cluster grows.
4. **Do not** attempt to make `P:[-voice]P` valid in ASCA.
5. ASCA apply probes + full inventory re-run; record metrics in **Answer**.

## Policy

- Applier-neutral YAML **`stages`** / `raw` unchanged unless grill/ADR requires otherwise; fix via overlay or compile mapping per [ADR-0010](../../docs/adr/0010-historical-fidelity-vs-validity.md).
- Document chosen IPA shape and source rationale on the ticket **Answer**.

## Acceptance criteria

- [ ] `Proto-Southern-Athabaskan-K` validates (`ok=1`)
- [ ] Compiled string uses IPA (or other ASCA-legal multi-segment output), not `P:[-voice]P`
- [ ] Apply probe on velar input → expected fricative/cluster output
- [ ] Full inventory re-run; before/after metrics in **Answer**

## References

- [incomplete_matrix_errors.csv](../inventory/error_clusters/incomplete_matrix_errors.csv)
- `config/parser/index_diachronica_corrections.yml`
- `config/compile/asca/compiler_config.yml` (section mappings — if used)
- HTML SoT: `K → TS` at `index_diachronica_original.html:10157`
