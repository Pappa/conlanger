Type: task
Status: resolved
Blocked by: 29

# Correction pass: unknown_feature (feature matrix synonyms at ingest)

Target cluster: `unknown_feature` — **251** rules, **39** distinct matrix feature names ([inventory summary](../inventory/rule-inventory-summary.md)).

## What to build

Implement ingest-time **feature matrix** normalisation inside `[...]` per [Normalise segment feature matrices for appliers](07-normalise-segment-features.md) and spike findings [research/index-feature-matrices-to-asca-targets.md](../research/index-feature-matrices-to-asca-targets.md).

### Phase 1 (this ticket — ship first)

1. Add **`data/asca/feature_mappings.csv`** using the extended schema (`index_feature`, `mapping_kind`, `asca_target`, optional `host`, `confidence`, `notes`).
2. Seed **rename** rows: `voiced`→`voice`, `stressed`→`stress`, `sibilant`→`strident`, `rounded`→`round`.
3. Seed **`rename_invert`**: `short`→`long` (`[+short]` → `[-long]` per spike 29).
4. Wire lookup in `IndexDiachronicaParser` at ingest — replace Index token inside `[...]`; **`raw`** unchanged; unmapped tokens left literal.
5. Re-run full inventory; record before/after for `unknown_feature`.

Expected Phase 1 impact: ~**90/251** rules fixed (spike estimated ~81; inventory shows **88**).

### Phase 2 (follow-on — do not block Phase 1)

- **`mapping_kind=bundle`** expansion for place labels (`dental`, `alveolar`, `palatal`, `velar`, `uvular`, `glottal`).
- **`rename_invert`** / **`rename_polarity`** kinds (`short`→`long`, `glottal`→`place`).
- Tone, lenis/fortis, `sameC`, `AP`, syllable `open`/`closed` — separate cluster tickets (defer per spike).

## Policy

- Apply inside `[...]` only at HTML→YAML parse; not compile layer.
- Do **not** seed from Levenshtein suggestions without spike review ([assessment](../research/unknown-feature-suggestions-assessment.md)).
- No pre-emptive `status: skipped` for unmapped features (ADR-0010).

## Acceptance criteria

- [x] `data/asca/feature_mappings.csv` created with Phase 1 rename rows
- [x] Parse-time normaliser wired; `raw` preserved
- [x] Unit tests on representative rules (`C[+voiced]`, `C[+sibilant]`, `%[- stressed]`, `u[+short]`)
- [x] Full inventory re-baseline; ok/fail delta recorded in **Answer**
- [x] Bundle kinds rejected at CSV load (Phase 2)

## Answer

Phase 1 shipped in `IndexDiachronicaParser.apply_feature_mappings` + `data/asca/feature_mappings.csv` (5 rows: 4× `rename`, 1× `rename_invert` for `short`→`long`).

**Inventory (ASCA 0.10.2, full HTML re-parse):**

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK | 6422 (68.9%) | 6483 (69.6%) | **+61** |
| `unknown_feature` | 251 | 163 | **−88** |

`short`/`voiced`/`sibilant`/`stressed`/`rounded` no longer appear as `unknown_feature` tokens. Phase 2 (place bundles) remains open.

## References

- [Spike: Index feature matrices → ASCA targets](29-spike-index-feature-matrices-to-asca-targets.md) (resolved)
- [Correction pass template](13-correction-pass-template.md)
- [`data/asca/group_mappings.csv`](../../../data/asca/group_mappings.csv) — co-located CSV convention
