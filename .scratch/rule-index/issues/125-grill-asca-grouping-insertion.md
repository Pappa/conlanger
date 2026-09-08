Type: grilling
Status: needs-grilling
Blocked by: None

# Grill: ASCA grouping letters on insertion rules

Spawned from wayfinder session on [Cleaned rule index SoT](../map.md) (2026-09-08). **Do not implement** [126](126-correction-pass-asca-grouping-insertion.md) until this grill resolves.

## Question

When Index rules are **insertions** (`∅ → …`) and compile to ASCA `∅ > F` (or other grouping letter / bare matrix output), how should the cleaned index represent and compile them?

**Blocked inventory example:** `Cypriot-Arabic-∅` — `∅ → F / N_{O,r} ! m_f` compiles to `∅ > F / N_{O,r} // m_f` → runtime `An incomplete matrix cannot be inserted`. Concrete IPA `∅ > f` with the same env **runs ok**.

Facts established in map session (2026-09-08; do not re-litigate without new probes):

- ASCA groupings (`P`, `F`, `C`, …) parse to **feature matrices**, not segment picks ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)).
- **1:1 substitution** `P > F` is legal: output matrix **patches** the matched segment’s features (place preserved; manner changes)—see Bantu [5-Vowel-Merger-Bantu-S](inventory/rule-inventory-success.csv).
- **Insertion** `∅ > F` fails: ASCA has no host segment to patch (`InsertionMatrix` in asca-rust 0.10.2).
- Index class letter **F** is not in `group_mappings.yml`; compiled `F` is ASCA’s fricative grouping, not Index fricative class semantics.

## Grill must decide

1. **SoT shape** for insertion outputs that Index writes as class letters (`∅ → F`, `∅ → S`, …): manual map to IPA? parse-time rewrite? compile expansion table?
2. **Historical fidelity** when the Index author meant “some fricative (POA not fixed)” vs a concrete segment—does `comment` on the rule suffice, or is a `manual_mappings.yml` row required per rule?
3. **Scope:** all `∅ > {grouping}` failures, or only `incomplete_matrix` cluster rows? Any overlap with env/exception matrices on insertion rules?
4. **Compile vs parse vs overlay:** which pipeline stage owns the fix (per [ADR-0010](../../docs/adr/0010-historical-fidelity-vs-validity.md) edit ladder)?
5. **Acceptance probes:** which ASCA shapes are in-scope (`∅ > f`, `∅ > [+cont]`, `∅ > *`, set expansions)?

## Follow-on

After grill resolves, implement [Correction pass: ASCA grouping insertion rules](126-correction-pass-asca-grouping-insertion.md).

## Acceptance criteria

- [ ] Q1–Q5 recorded under **Answer** with chosen policy
- [ ] Follow-on ticket [126](126-correction-pass-asca-grouping-insertion.md) unblocked (update its body if scope changed)

## References

- [Cypriot-Arabic-∅](../inventory/error_clusters/incomplete_matrix_errors.csv)
- [5-Vowel-Merger-Bantu-S](../inventory/rule-inventory-success.csv) — contrast: substitution not insertion
- [What counts as a valid ASCA rule string?](01-valid-asca-rule-string.md)
- [Correction pass template](13-correction-pass-template.md)
