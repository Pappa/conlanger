Type: task
Status: ready-for-human
Blocked by: [125](125-grill-asca-grouping-insertion.md)

# Correction pass: ASCA grouping insertion rules

Target cluster: `incomplete_matrix` — insertion rows where compiled output is an ASCA **grouping letter** or otherwise triggers `InsertionMatrix` at apply time.

**Blocked by grill:** [Grill: ASCA grouping letters on insertion rules](125-grill-asca-grouping-insertion.md) — **do not start** until Q1–Q5 are answered there.

Spawned from wayfinder session on [Cleaned rule index SoT](../map.md) (2026-09-08).

## Problem (known before grill)

`Cypriot-Arabic-∅`: Index `∅ → F / N_{O,r} ! m_f` → compiled `∅ > F / N_{O,r} // m_f` → runtime `An incomplete matrix cannot be inserted`.

Substitution analogues (`P > F`, Index `S → F`) validate because ASCA patches features on a matched segment; insertion has no host segment for a bare grouping/matrix output.

## What to build

*(Implementation shape TBD by [125](125-grill-asca-grouping-insertion.md).)*

1. Apply the grill’s chosen policy (manual overlay, parse rewrite, compile expansion, or hold-out + comment).
2. Re-run full inventory; record ok/fail and `incomplete_matrix` cluster delta in **Answer**.
3. ASCA apply probes for each fixed rule shape.

## Acceptance criteria

- [ ] Grill [125](125-grill-asca-grouping-insertion.md) resolved
- [ ] Policy implemented per grill **Answer**
- [ ] `Cypriot-Arabic-∅` validates or is explicitly held out with documented reason
- [ ] Full inventory re-run; before/after metrics in **Answer**

## References

- [125 grill](125-grill-asca-grouping-insertion.md)
- [incomplete_matrix_errors.csv](../inventory/error_clusters/incomplete_matrix_errors.csv)
- `config/parser/manual_mappings.yml`, `config/parser/index_diachronica_corrections.yml`
