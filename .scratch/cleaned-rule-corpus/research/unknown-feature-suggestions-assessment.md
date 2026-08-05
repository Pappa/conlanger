# Assessment: ASCA Levenshtein suggestions for `unknown_feature` tokens

Spike for a future **Correction pass: unknown_feature** (ticket 07 policy).  
Baseline inventory: `uv run regenerate_corpus` (2026-08-05) — **251** rules, **39** distinct `error_token` → `suggested` pairs.

ASCA suggestions come from the parser’s “Did you mean …?” hint ([`parse_unknown_token_error`](../../../src/conlanger/tools/corpus_inventory.py)); they are **string-distance guesses**, not semantic mappings. Use them to triage only — not as `feature_mappings.csv` rows without review.

## Summary

| Verdict | Pairs | Rules | Notes |
| --- | ---: | ---: | --- |
| **Accept** — safe 1:1 synonym | 4 | 62 | Index name differs only in spelling from an ASCA shorthand |
| **Reject** — wrong node / place / manner | 28 | 177 | Levenshtein hit an unrelated ASCA feature |
| **Defer** — needs decomposition or non-feature fix | 7 | 12 | Compound labels, co-reference, or section-local abbreviations |

**Bottom line:** only **~25%** of failing rules (62/251) have a Levenshtein suggestion that matches ticket-07 “safe 1:1 ASCA equivalent” intent. The top five tokens by count (`voiced`, `sibilant`, `dental`, `open`, `palatal`) account for **123/251** failures; only `voiced→voice` among those five is acceptable.

## Accept (author in `feature_mappings.csv`)

| error_token | suggested | count | Index intent | ASCA target |
| --- | --- | ---: | --- | --- |
| `voiced` | `voice` | 56 | `[±voiced]` on consonants | `voice` (`[+voice]` / `[-voice]`) |
| `rounded` | `round` | 1 | `[+rounded]` | `round` |
| `stressed` | `stress` | 3 | `%[± stressed]` env | `stress` |
| `aspirated` | `spread` | 1 | `[+ aspirated]` on obstruents | `spread` (spread glottis) — verify rule-local semantics |

`voiced` is the highest-volume win: e.g. `C[+voiced]`, `N[-voiced]`, `O[+voiced]` → replace feature name with `voice` inside matrices ([ticket 07](../issues/07-normalise-segment-features.md); ASCA [Feature shorthands](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands)).

## Reject (do not auto-map from suggestion)

### Place / manner confusion (top cluster)

| error_token | suggested | count | Why reject | Likely manual mapping |
| --- | --- | ---: | --- | --- |
| `sibilant` | `sonorant` | 22 | Sibilant ≈ strident obstruent; sonorant is the opposite branch of the tree | `strident` or `stridnt` |
| `dental` | `ldental` | 18 | `ldental` = **labiodental** place shorthand, not coronal dental | `anterior` + coronal, or segment class |
| `palatal` | `latrl` | 13 | Palatal = coronal place; lateral = manner | `distr` / `back` on coronal, or `[+cons,+hi,-lo,+front]` |
| `palatalized` | `latrl` | 1 | Secondary articulation, not lateral | custom or env-only rewrite |
| `velar` | `delay` | 5 | Velar = dorsal place; `delay` = delayed release | `[+back,-hi]` (dorsal) |
| `alveolar` | `delay` | 5 | Alveolar = coronal anterior | `anterior` |
| `uvular` | `lar` | 4 | Uvular = dorsal/back; `lar` = laryngeal **node** name | dorsal `[+back,-hi,-lo]` |
| `guttural` | `lateral` | 5 | Guttural ≈ uvular/pharyngeal; not lateral | dorsal or pharyngeal features |
| `glottal` | `lateral` | 4 | Glottal place/laryngeal | `[-place]` or laryngeal segment match |
| `labiovelar` | `labiodental` | 1 | Distinct places | labial + dorsal composite |

### Vowel height / length / tone

| error_token | suggested | count | Why reject | Likely manual mapping |
| --- | --- | ---: | --- | --- |
| `open` | `ten` | 14 | `[+open-mid]` vowel height; `ten` = **tense** | `lo` / compound `[-hi,+lo]` or leave compound tokenised |
| `close` | `cons` | 1 | `[+close-mid]` | `hi` / `[-lo,+hi]` |
| `mid` | `man` | 7 | Vowel `[+ mid]` height | not a single ASCA feature — rewrite or spike |
| `closed` | `cons` | 4 | Syllable `[+closed]` (no coda vowel?) | not `cons` (consonantal) |
| `short` | `snrt` | 9 | Vowel length `[+short]` vs `long` | `long` with polarity inverted, or suprasegmental spike |
| `lenis` | `tens` | 6 | Consonant lenis/fortis contrast | no ASCA lenis feature — `[+cg]`/`[-cg]` or custom |
| `fortis` | `contin` | 9 | Fortis ≠ continuant | same as lenis |
| `hightone` | `high` | 8 | **Tone** label, not vowel height | `tone` + prose, or suprasegmental extension |
| `lowtone` | `contin` | 12 | Tone | `tone` |
| `highpitch` | `high` | 1 | Pitch accent | `tone` / `stress` spike |
| `lowpitch` | `voice` | 1 | Pitch accent | `tone` |
| `fallingtone` | `length` | 3 | Contour tone | `tone` + decomposition |
| `highrisingtone` | `strident` | 2 | Contour tone | `tone` |
| `lowfallingtone` | `continuant` | 2 | Contour tone | `tone` |
| `creakyvoice` | `voice` | 1 | `[+ creaky voice]` | `cg` / constricted glottis, not `voice` |
| `tonic` | `cons` | 1 | Syllable `[+tonic]` | stress/tone spike |

### Other feature names

| error_token | suggested | count | Why reject | Likely manual mapping |
| --- | --- | ---: | --- | --- |
| `glottalized` | `contin` | 9 | Index “glottalized” sonorant ≈ ejective/creaky | `[+cg]` ([ejective research](asca-ejective-notation.md)) |
| `fricative` | `rhotic` | 2 | Manner class | `[+cont,-son]` or obstruent minus stop |
| `affricate` | `stridnt` | 1 | Manner | `[-cont,+delrel]` or affricate = stop+fricative |
| `glide` | `click` | 1 | Glide consonant in env | approximant / `G` class |
| `weak` | `man` | 4 | Schwa `[+weak]` (Algonquian) | section-local or delete feature |
| `intertonic` | `anterior` | 1 | Prosodic position | env rewrite, not a segment feature |

## Defer (not a feature synonym row)

| error_token | suggested | count | Issue |
| --- | --- | ---: | --- |
| `sameC` | `sec` | 9 | **Co-reference** (“same C as …”) — identity/subscript ticket, not feature matrix |
| `AP` | `rt` | 3 | Section-local consonant class (Athabaskan-style) |
| `RP` | `rt` | 1 | Same |

Examples: `P[+same C:[+labial]OO:[+delrel]]`, `V[+high +AP:[-voice][+son,-syll]]` — need abbreviation or alpha-reference syntax, not `feature_mappings.csv`.

## Recommended `feature_mappings.csv` seed (high confidence only)

```csv
index_feature,asca_feature,notes
voiced,voice,Index [±voiced] on segments
rounded,round,[+rounded] vowel
stressed,stress,env %[- stressed] after normalising whitespace
```

Do **not** seed from suggestions for: `sibilant`, `dental`, `palatal`, `open`, `mid`, `velar`, tone/pitch tokens, `lenis`/`fortis`, `glottalized`, `short`, `sameC`, `AP`/`RP`.

## Follow-up tickets

1. ~~**[Spike: Index feature matrices → ASCA targets](../issues/29-spike-index-feature-matrices-to-asca-targets.md)**~~ — done; see [index-feature-matrices-to-asca-targets.md](index-feature-matrices-to-asca-targets.md).
2. **[Correction pass: unknown_feature](../issues/32-correction-pass-unknown-feature.md)** — implement ingest normalisation from `feature_mappings.csv`; Phase 1 renames (`voiced`, `stressed`, `sibilant`); Phase 2 bundles.

## References

- [Normalise segment feature matrices for appliers](../issues/07-normalise-segment-features.md)
- [ASCA rule validity research](asca-rule-validity.md)
- [ASCA Feature shorthands (0.10.2)](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands)
- [ASCA `diacritics.json` (0.10.2)](https://raw.githubusercontent.com/Girv98/asca-rust/36c3c623fb9f501a358ae087764e77b92d0037bf/src/diacritics.json) — semantic payloads for named categories
- Inventory summary: [asca-rule-inventory-summary.md](../inventory/asca-rule-inventory-summary.md) (`unknown_feature` table now includes `suggested` column)
