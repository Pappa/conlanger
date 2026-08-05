# Index feature matrices → ASCA targets

Spike for [29-spike-index-feature-matrices-to-asca-targets](../issues/29-spike-index-feature-matrices-to-asca-targets.md).  
Baseline: **251** rules, **39** distinct `unknown_feature` tokens ([inventory summary](../inventory/asca-rule-inventory-summary.md)); Levenshtein triage in [unknown-feature-suggestions-assessment.md](./unknown-feature-suggestions-assessment.md) (not authoritative).

Primary sources: **ASCA 0.10.2** ([Feature shorthands](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands), [Segment features / feature tree](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#segment-features), [Matching a subnode](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode), [Suprasegmental features](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#suprasegmental-features)), [`diacritics.json`](https://raw.githubusercontent.com/Girv98/asca-rust/36c3c623fb9f501a358ae087764e77b92d0037bf/src/diacritics.json).

Policy: [07-normalise-segment-features](../issues/07-normalise-segment-features.md) — ingest normalisation inside `[...]` only; `raw` unchanged; unmapped → validation fail (ADR-0010).

**Path note:** ticket 07 names `src/conlanger/data/asca/feature_mappings.csv`; the repo convention (with `group_mappings.csv`) is **`data/asca/feature_mappings.csv`**.

---

## Executive summary

| Outcome | Rules (approx.) | Tokens (count ≥ 3) |
|---------|----------------:|--------------------|
| **Kind 1 — Rename** (1:1 ASCA shorthand, same polarity) | ~62 | `voiced`, `stressed` |
| **Kind 2 — Different shorthand** (same node, different label) | ~22 | `sibilant` |
| **Kind 3 — Feature bundle** (place/manner → multi-feature matrix) | ~80 | `dental`, `palatal`, `velar`, `alveolar`, `uvular`, `guttural`, `glottal` |
| **Kind 4 — Defer** (suprasegmental, lenis/fortis, co-ref, section-local, syllable prosody) | ~87 | `lowtone`, `hightone`, `short`, `fortis`, `lenis`, `sameC`, `AP`, `open`, `mid`, `closed`, `glottalized`, `weak`, `fallingtone` |

Ticket 07 assumed **1:1 synonym** rows only. This spike shows **~35%** of high-volume failures are safe renames (`voiced`, `stressed`, `sibilant→strident`), **~32%** need **bundle expansion** (Index place labels as single matrix features), and **~35%** cannot be solved with `feature_mappings.csv` alone — they need env rewrites, `[tone: …]` syntax, correspondence/alpha notation, or validation-cluster hand edits.

**`asca_target` may be a multi-feature matrix fragment.** Use `mapping_kind=bundle` and a comma-separated feature list (preserving `+`/`-` from the Index token on each expanded feature, or documenting exceptions). Ingest must **replace one Index token with multiple ASCA features** inside the same `[...]` block; a bare string swap is insufficient for place labels.

---

## ASCA constraints (relevant)

From [Segment features](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#segment-features) and [Matching a subnode](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode):

| Index-style label | ASCA decomposition | Source |
|-------------------|-------------------|--------|
| Sibilant manner | `[+strident]` (`strident`, `stridnt`, …) | Feature tree MANNER / strident row |
| Voicing | `[±voice]` (`voice`, `voi`, …) | LARYNG / voice; [`diacritics.json` "voiced"](https://raw.githubusercontent.com/Girv98/asca-rust/36c3c623fb9f501a358ae087764e77b92d0037bf/src/diacritics.json) → `Voice: true` |
| Dental / alveolar / palatal place | CORONAL subnode: `[+anterior]`, `[±distrib]` (`distrib`, `dist`, …) | anterior = “dentals, alveolars”; distrib = “palatals, post-palatals” vs alveolars |
| Velar / uvular place | DORSAL: `[±front]`, `[±back]`, `[±hi]`, `[±lo]` | Crate TODO matrices in [class-letter spike](./asca-class-letter-mappings.md) (`K`, `Q`) |
| Glottal segment | `[-place]` → “h, ɦ, ʔ, etc.” | Matching a subnode |
| Glottalized laryngeal | `[+cg]` (constricted glottis) | [`diacritics.json` "glottalized"](https://raw.githubusercontent.com/Girv98/asca-rust/36c3c623fb9f501a358ae087764e77b92d0037bf/src/diacritics.json); [ejective research](./asca-ejective-notation.md) |
| Short vs long | `[-long]` / `[+long]` | [Length](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#length-1) |
| Stress | `[±stress]` (`stress`, `str`, …) | [Stress](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#stress-1) |
| Tone | **`[tone: N]`** — not a ± binary feature | [Tone](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#tone-1); `[tone: 214]`, `[tone: 35]`, etc. |

There is **no** ASCA feature for: lenis, fortis, open/closed syllable, mid vowel height as a single feature, co-reference (`sameC`), or section series labels (`AP`).

---

## Classification: tokens with count ≥ 3

| Token | count | Kind | Recommended ASCA target | Conf. | Primary source |
|-------|------:|------|-------------------------|-------|----------------|
| `voiced` | 56 | **1 Rename** | `voice` | high | [Feature shorthands — voice](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands); e.g. `C[+voiced]` → `C[+voice]` |
| `sibilant` | 22 | **2 Different shorthand** | `strident` | high | Feature tree strident row; [`diacritics.json` strident payloads](https://raw.githubusercontent.com/Girv98/asca-rust/36c3c623fb9f501a358ae087764e77b92d0037bf/src/diacritics.json) |
| `dental` | 18 | **3 Bundle** | `C:[+cor,+anterior,+dist]` | high | CORONAL + anterior + distributed; cf. `denti-alveolar` payload in diacritics.json |
| `open` | 14 | **4 Defer** | — | — | **Two Index senses:** vowel `[+open-mid]` (height) vs syllable `%[+open]` / `%[+stress][+open]` (prosody). No single ASCA feature; height needs `±hi`/`±lo` bundles or hyphen-token split; syllable open → env/`%` cluster |
| `palatal` | 13 | **3 Bundle** | `C:[+cor,+dist]` | medium | CORONAL + distributed = “palatals, post-palatals” ([Matching a subnode](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode)); overlaps alveolo-palatals — cluster review when rule contrasts `dental`/`alveolar` |
| `lowtone` | 12 | **4 Defer** | — | — | Index `[+low tone]` / `V[+low tone]`; ASCA requires `[tone: N]` ([Tone](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#tone-1)). Language-specific number choice → correction pass / cluster |
| `short` | 9 | **4 Defer** | `long` with **polarity invert** | medium | Index `[+short]` = ASCA `[-long]` ([Length](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#length-1)). Needs `mapping_kind=rename_invert`, not ticket-07 1:1 |
| `fortis` | 9 | **4 Defer** | — | — | Anatolian consonant strength; no lenis/fortis in ASCA tree. `[+tense]` on consonants is documented but **not** equivalent ([Segment features — tense](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#segment-features)) |
| `sameC` | 9 | **4 Defer** | — | — | Co-reference (“same C as …”), e.g. `P[+same C:[+labial]…]` — alpha/reference syntax, not a feature ([Alpha notation](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#alpha-notation)) |
| `glottalized` | 9 | **4 Defer** | `[+cg]` (+ often `[-voice]` on sonorants) | medium | [`diacritics.json` "glottalized"](https://raw.githubusercontent.com/Girv98/asca-rust/36c3c623fb9f501a358ae087764e77b92d0037bf/src/diacritics.json): `ConstrGlottis: true`, `Voice: false` on sonorants; Chumash rules mix `[- glottalized]` with `VO:[+cg]` — cluster per rule |
| `hightone` | 8 | **4 Defer** | — | — | Index `V[+high tone]`; ASCA `[tone: N]` only. Athabaskan/Iroquoian sections need contour/register mapping table |
| `mid` | 7 | **4 Defer** | `V:[-hi,-lo]` (approx.) | low | Vowel height `[+ mid]` — no atomic ASCA height feature; `-hi,-lo` over-generates (central vowels). Prefer env/cluster |
| `lenis` | 6 | **4 Defer** | — | — | Same as `fortis` — unrepresentable without rule rewrite or custom compile pass |
| `velar` | 5 | **3 Bundle** | `C:[-fr,+bk,+hi,-lo]` | high | DORSAL velar matrix ([class-letter K row](./asca-class-letter-mappings.md)); also appears as `C[+labial/+velar]` compound — slash compounds need separate normaliser |
| `guttural` | 5 | **3 Bundle** | `{C:[-fr,+bk,+hi,-lo],C:[-fr,+bk,-hi,-lo],[-place]}` | low | Index “guttural” (Chinese) ≈ velar∪uvular∪glottal; union of dorsal back + `[-place]` ([Matching a subnode](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode)) — **medium fidelity** |
| `alveolar` | 5 | **3 Bundle** | `C:[+cor,+anterior,-dist]` | high | CORONAL anterior, non-distributed ([Segment features](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#segment-features)) |
| `closed` | 4 | **4 Defer** | — | — | Syllable `%[+closed]` (coda / syllable type), not `[+cons]` — prosodic predicate, not segment feature |
| `uvular` | 4 | **3 Bundle** | `C:[-fr,+bk,-hi,-lo]` | high | DORSAL uvular ([class-letter Q uvular branch](./asca-class-letter-mappings.md)) |
| `weak` | 4 | **4 Defer** | — | — | Algonquian schwa `[+weak]` — section-local reduced vowel; no ASCA `weak` |
| `glottal` | 4 | **3 Bundle** | **Polarity map to `place`:** `[+glottal]`→`[-place]`, `[-glottal]`→`[+place]` | medium | Iroquoian `C[-glottal]` = non-glottals ([Matching a subnode — `-place`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode)); needs `mapping_kind=rename_polarity` |
| `fallingtone` | 3 | **4 Defer** | — | — | Contour `[+falling tone]` → `[tone: 51]` or similar per language ([Tone](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#tone-1)) |
| `stressed` | 3 | **1 Rename** | `stress` | high | [Feature shorthands — stress](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands); `%[- stressed]` → `%[-stress]` |
| `AP` | 3 | **4 Defer** | — | — | Bantu section series (aspirated/obstruent slot), e.g. `V[+high +AP:[-voice][+son,-syll]]` — class/env rewrite, not feature synonym |

---

## Inventory context (how tokens appear)

| Token | Example rule fragment | Notes |
|-------|----------------------|-------|
| `voiced` | `C[+voiced]`, `N[-voiced]`, `O[+voiced]` | Pure rename win |
| `sibilant` | `C[+sibilant]`, `#C[+sibilant]_{d,n,r}` | Env conditioning on sibilant consonants |
| `dental` | `C[+dental]`, `C[-dental]` | Coronal place in env |
| `palatal` | `O[+lateral] > O[+palatal]`, `_C[+palatal]` | Output + env |
| `open` | `_CV[+open-mid]`, `%[+open]`, `%:[+stress][+open]` | Split by hyphen/prosody before mapping |
| `short` | `u[+short]_V[+short]`, `%[+open -initial -final]` | Often paired with `%[+open]` (Yupik) |
| `lenis`/`fortis` | `P:[-voice][+lenis]`, `T[+fortis] T[+lenis]` | Anatolian geminate strength |
| `glottalized` | `[- glottalized]VˀR`, `VO:[+cg]` mixed in same section | Align with `[+cg]` pass ([ticket 20](../issues/20-correction-pass-ejective-marks.md)) |
| `hightone`/`lowtone` | `Vˀ > V[+high tone]`, `V[+low tone] > V[-tone]` | Athabaskan register; space in `high tone` may need whitespace normalisation first |
| `sameC` | `P[+same C:[+labial]OO:[+delrel]]` | Identity, not feature |
| `AP` | `V[+high +AP:[-voice][+son,-syll]]` | Multi-matrix section symbol |
| `glottal` | `C[-glottal]`, `V > V:[+long] / _C[-glottal]` | Feature name for “glottal consonant” |

---

## Tail: tokens with count &lt; 3

| Token | count | Kind | Notes |
|-------|------:|------|-------|
| `lowfallingtone` | 2 | 4 Defer | Contour tone → `[tone: …]` |
| `highrisingtone` | 2 | 4 Defer | Contour tone → `[tone: …]` |
| `fricative` | 2 | 3 Bundle | `O:[+cont]` or `[+cont,-son]` — manner, not place |
| `close` | 1 | 4 Defer | `[+close-mid]` compound — split token |
| `lowpitch` / `highpitch` | 1 each | 4 Defer | Altaic pitch accent → tone/stress cluster |
| `rounded` | 1 | 1 Rename | `round` |
| `aspirated` | 1 | 1 Rename | `spread` (verify rule = spread glottis, not `[+sg]` on plosives only) |
| `affricate` | 1 | 3 Bundle | `O:[+delrel]` or `[-cont,+delrel]` |
| `tonic` | 1 | 4 Defer | Syllable `[+tonic]` — stress |
| `glide` | 1 | 4 Defer | Use grouping `G` or `[+approx,-cons]` |
| `RP` | 1 | 4 Defer | Section-local (with `AP`) |
| `palatalized` | 1 | 4 Defer | Secondary articulation — dorsal `+hi,+fr` or segment diacritic cluster |
| `creakyvoice` | 1 | 2/3 | `[+cg]` (creaky = constricted glottis per laryngeal table) |
| `labiovelar` | 1 | 4 Defer | Multi-place — `{C:[+lab],C:[-fr,+bk,+hi,-lo]}` or hand rule |
| `intertonic` | 1 | 4 Defer | Prosodic position — env rewrite |

---

## Proposed `feature_mappings.csv` schema

Ticket 07’s two-column `index_feature, asca_feature` is **insufficient**. Proposed columns:

| Column | Required | Description |
|--------|----------|-------------|
| `index_feature` | yes | Token inside `[...]` (case-sensitive; match inventory) |
| `mapping_kind` | yes | `rename` \| `rename_invert` \| `rename_polarity` \| `bundle` \| `defer` |
| `asca_target` | if not defer | **Rename:** single shorthand (`voice`). **Bundle:** comma-separated features without brackets (`+cor,+anterior,+dist`). **Rename_invert:** target feature name (`long`). **Rename_polarity:** target feature (`place`) with ± flipped |
| `host` | no | Optional grouping prefix when bundle must not match vowels (`C`, `V`, `O`, `%`) — applied as `host:matrix` at compile |
| `confidence` | yes | `high` \| `medium` \| `low` — gates auto-ingest vs cluster-only |
| `notes` | no | Human rationale + source link |

### Can `asca_target` be a multi-feature matrix?

**Yes.** For `mapping_kind=bundle`, `asca_target` is the **inner** matrix body (e.g. `+cor,+anterior,-dist`). The normaliser:

1. Finds `[±index_feature]` (or bare `index_feature` after `:` host).
2. Removes the Index token.
3. Inserts expanded ASCA features, **propagating the Index token’s `+`/`-`** to each feature unless `notes` document an exception.
4. Optionally prefixes `host:` (e.g. `C:[+cor,+anterior,+dist]`).

**Not in CSV scope:** whole-matrix rewrites, `[tone: N]` syntax transforms, slash compounds (`C[+labial/+velar]`), or rules where Index uses **space-separated** pseudo-features (`[+high tone]` → tokenise to `hightone` first).

### Runtime location

Co-locate with [`data/asca/group_mappings.csv`](../../../data/asca/group_mappings.csv) → **`data/asca/feature_mappings.csv`**. Apply at ingest inside `[...]` per ticket 07; bundles may require a **second pass** after 1:1 renames.

---

## High-confidence seed rows

Paste-ready block — **implement these first** in a correction pass; omit `defer` rows from CSV (track in cluster tickets).

```csv
index_feature,mapping_kind,asca_target,host,confidence,notes
voiced,rename,voice,,high,Index [±voiced] → ASCA voice (LARYNG node)
stressed,rename,stress,,high,Index [±stressed] → ASCA stress suprasegmental
sibilant,rename,strident,,high,Sibilant manner → strident (MANNER); not sonorant
dental,bundle,"+cor,+anterior,+dist",C,high,Coronal dental; cf. diacritics.json denti-alveolar
alveolar,bundle,"+cor,+anterior,-dist",C,high,Coronal alveolar
palatal,bundle,"+cor,+dist",C,medium,Coronal palatal/post-palatal; review alveolo-palatal sections
velar,bundle,"-fr,+bk,+hi,-lo",C,high,Dorsal velar; matches group_mappings K
uvular,bundle,"-fr,+bk,-hi,-lo",C,high,Dorsal uvular; matches group_mappings Q uvular branch
glottal,rename_polarity,place,C,medium,[+glottal]→[-place] [-glottal]→[+place]; Iroquoian envs
rounded,rename,round,,high,Single-count tail; included for completeness
```

**Do not seed yet:** `open`, `mid`, `closed`, `short`, `lenis`, `fortis`, `glottalized`, all `*tone*` tokens, `sameC`, `AP`, `weak`, `guttural` (low confidence union), `fricative`, `affricate`.

Expected impact of seed block alone: **~59 rules** from renames (`voiced`+`stressed`) + **~22** from `sibilant` ≈ **81/251 (32%)** before bundle plumbing exists.

---

## Implementation notes (out of spike scope)

1. **Whitespace:** Index `[+high tone]`, `[+ open-mid]`, `[- glottalized]` — normalise spaces inside brackets before feature lookup (deferred ticket 07 whitespace).
2. **Hyphen compounds:** `[+open-mid]`, `[+close-mid]` — tokeniser should split on `-` or map as compound keys (`open-mid`), not `open`.
3. **Tone pass:** separate correction pass: `[+high tone]` → `[tone:5]`, `[+low tone]` → `[tone:1]` (language tables in validation clusters).
4. **`sameC` / `AP`:** correspondence-series / alpha-reference tickets, not feature CSV.
5. **`glottalized`:** align with compile `[+cg]` normalisation ([20-correction-pass-ejective-marks](../issues/20-correction-pass-ejective-marks.md)); sonorant rules may need `[-voice,+cg]`.

---

## Source index

| Claim | Primary source |
|-------|----------------|
| Feature tree (strident, coronal, dorsal, …) | [doc.md § Segment features](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#segment-features) |
| Place subnode matching | [doc.md § Matching a subnode](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode) |
| Accepted matrix names / shorthands | [doc.md § Feature shorthands](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands) |
| Stress, length, tone syntax | [doc.md § Suprasegmental features](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#suprasegmental-features) |
| Named category → feature payloads | [`diacritics.json` (0.10.2)](https://raw.githubusercontent.com/Girv98/asca-rust/36c3c623fb9f501a358ae087764e77b92d0037bf/src/diacritics.json) |
| Velar/uvular bundle precedent | [asca-class-letter-mappings.md](./asca-class-letter-mappings.md) |
| Levenshtein triage (non-authoritative) | [unknown-feature-suggestions-assessment.md](./unknown-feature-suggestions-assessment.md) |
| Failure counts | [asca-rule-inventory-summary.md](../inventory/asca-rule-inventory-summary.md) |
