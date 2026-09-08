Type: task
Status: needs-grilling
Blocked by: [125](125-grill-asca-grouping-insertion.md)

# Correction pass: ASCA grouping insertion rules

Target cluster: `incomplete_matrix` — **`Cypriot-Arabic-∅`** today ([incomplete_matrix_errors.csv](../inventory/error_clusters/incomplete_matrix_errors.csv)); scope may widen per [125](125-grill-asca-grouping-insertion.md).

**Blocked by grill:** [Grill: ASCA grouping letters on insertion rules](125-grill-asca-grouping-insertion.md) — **do not start** until Q1–Q6 are answered there. Status `needs-grilling` until grill resolves.

Spawned from wayfinder session on [Cleaned rule index SoT](../map.md) (2026-09-08).

## Problem (updated 2026-09-08)

`Cypriot-Arabic-∅`: Index `∅ → F / N_{O,r} ! m_f` → compiled `∅ > F / N_{O,r} // m_f` → runtime `An incomplete matrix cannot be inserted`.

**Not a simple `∅ > F` grouping-output bug.** Follow-up probes show:

- **`Hidatsa-∅`** (`∅ → V / x_k` → `∅ > V / x_k`) **validates** — same matrix-style output (`V`), different env.
- **`∅ > f / N_{O,r} // m_f`** and **`∅ > i / N_{O,r} // m_f`** run **ok** — concrete IPA output with the same env.
- **`∅ > V / N_{O,r}`** and **`∅ > V / N_O`** **fail** — env contains ASCA grouping **`O`** (from Index `{O,r}`) + matrix/grouping output.
- **`∅ > V / N_r`** and **`∅ > V / x_k`** **ok** — env without grouping `O`.

Fix likely requires **both** output policy (matrix vs IPA on insertion) **and** env policy (Index class letters `O`, `r`, … in env sets vs ASCA grouping letters). See [125](125-grill-asca-grouping-insertion.md) probe table.

## What to build

*(Implementation shape TBD by [125](125-grill-asca-grouping-insertion.md).)*

1. Apply the grill’s chosen policy for **output** and **env** (manual overlay, parse rewrite, compile expansion, or hold-out + comment).
2. Re-run full inventory; record ok/fail and `incomplete_matrix` cluster delta in **Answer**.
3. ASCA apply probes: Cypriot full rule; Hidatsa `∅ > V / x_k` regression; IPA-output baseline on `N_{O,r}` env.

## Acceptance criteria

- [ ] Grill [125](125-grill-asca-grouping-insertion.md) resolved
- [ ] Policy implemented per grill **Answer** (output **and** env if grill requires)
- [ ] `Cypriot-Arabic-∅` validates or is explicitly held out with documented reason
- [ ] `Hidatsa-∅` (and other passing insertion+grouping rows) unchanged
- [ ] Full inventory re-run; before/after metrics in **Answer**

## References

- [125 grill](125-grill-asca-grouping-insertion.md)
- [Hidatsa-∅](../inventory/rule-inventory-success.csv)
- [incomplete_matrix_errors.csv](../inventory/error_clusters/incomplete_matrix_errors.csv)
- `config/parser/manual_mappings.yml`, `config/parser/index_diachronica_corrections.yml`
