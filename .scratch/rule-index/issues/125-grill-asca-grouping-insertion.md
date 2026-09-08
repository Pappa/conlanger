Type: grilling
Status: needs-grilling
Blocked by: None

# Grill: ASCA grouping letters on insertion rules

Spawned from wayfinder session on [Cleaned rule index SoT](../map.md) (2026-09-08). **Do not implement** [126](126-correction-pass-asca-grouping-insertion.md) until this grill resolves.

## Question

When Index rules are **insertions** (`∅ → …`) and compile to ASCA with **grouping letters or bare matrices** on output and/or env, how should the cleaned index represent and compile them?

**Blocked inventory example:** `Cypriot-Arabic-∅` — `∅ → F / N_{O,r} ! m_f` → `∅ > F / N_{O,r} // m_f` → runtime `An incomplete matrix cannot be inserted`.

**Contrast (same output class, different env):** `Hidatsa-∅` — `∅ → V / x_k` → `∅ > V / x_k` → **validates** (`ok=1`). So **`F` vs `V` is not the discriminator**; env shape matters.

Facts established (2026-09-08 map session + follow-up probes; do not re-litigate without new evidence):

- ASCA groupings (`P`, `F`, `C`, `V`, `O`, …) parse to **feature matrices**, not segment picks ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)).
- **1:1 substitution** `P > F` is legal: output matrix **patches** the matched segment’s features—see Bantu [5-Vowel-Merger-Bantu-S](../inventory/rule-inventory-success.csv).
- **`InsertionMatrix` is not “all `∅ > {grouping}`”.** Local probes (ASCA 0.10.2):

| Rule | `asca run` |
| --- | --- |
| `∅ > V / x_k` (Hidatsa) | **ok** |
| `∅ > F / x_k` | **ok** |
| `∅ > f / N_{O,r} // m_f` | **ok** |
| `∅ > i / N_{O,r} // m_f` | **ok** |
| `∅ > V / N_{O,r}` | **fail** |
| `∅ > V / N_{O,r} // m_f` (Cypriot) | **fail** |
| `∅ > V / N_O` | **fail** |
| `∅ > V / N_r` | **ok** |

- **Env with ASCA grouping `O`** (Index `{O,r}` in `N_{O,r}`) + **matrix/grouping output** triggers the failure. Env without `O` (`x_k`, `N_r`) + matrix output is fine. **Concrete IPA output** (`f`, `i`) + `N_{O,r}` env is fine.
- Index **`O`** in `{O,r}` is almost certainly an Index **class letter**; ASCA reads bare **`O`** as the built-in **obstruent** grouping regardless.
- Index class letter **F** is not in `group_mappings.yml`; compiled `F` is ASCA’s fricative grouping.

## Grill must decide

1. **SoT shape** for insertion **outputs** written as class letters (`∅ → F`, …): manual map to IPA? parse-time rewrite? compile expansion table?
2. **SoT shape for env class letters** in sets like `N_{O,r}`, `{O,r}_`, `N_O` — expand Index `O`/`r` before ASCA sees them? escape/grouping-safe form? prose rewrite?
3. **Historical fidelity** when Index meant “some fricative (POA not fixed)” vs a concrete segment—`comment` vs `manual_mappings.yml` per rule?
4. **Scope:** Cypriot row only, all env+matrix insertion interactions, or broader `incomplete_matrix` cluster?
5. **Compile vs parse vs overlay:** which pipeline stage owns output vs env fixes ([ADR-0010](../../docs/adr/0010-historical-fidelity-vs-validity.md))?
6. **Acceptance probes:** matrix output with `N_{O,r}` env; IPA output baseline; Hidatsa `∅ > V / x_k` regression; related held-out rows (e.g. skipped `Cypriot-Arabic-j` with `{O,r}` env).

## Follow-on

After grill resolves, implement [Correction pass: ASCA grouping insertion rules](126-correction-pass-asca-grouping-insertion.md).

## Acceptance criteria

- [ ] Q1–Q6 recorded under **Answer** with chosen policy
- [ ] Follow-on ticket [126](126-correction-pass-asca-grouping-insertion.md) updated if scope changed

## References

- [Cypriot-Arabic-∅](../inventory/error_clusters/incomplete_matrix_errors.csv) — fail
- [Hidatsa-∅](../inventory/rule-inventory-success.csv) — pass (contrast)
- [5-Vowel-Merger-Bantu-S](../inventory/rule-inventory-success.csv) — substitution not insertion
- [What counts as a valid ASCA rule string?](01-valid-asca-rule-string.md)
- [Correction pass template](13-correction-pass-template.md)
