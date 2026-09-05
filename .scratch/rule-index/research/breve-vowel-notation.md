# Index Diachronica breve vowel notation (`̆`) → ASCA representation

Primary sources: [ASCA 0.10.2 `doc/doc.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md), `data/diachronica/index_diachronica_original.html`, local `validate_asca` smoke tests (2026-08-19), [Brassica Writing Sound Changes](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md).

## Summary

Index Diachronica uses combining breve **U+0306 `̆`** (and precomposed breve vowels `ă`, `ŏ`, `ŭ`) to mark **extra-short** or **reduced** vowels — standard IPA/Americanist usage ([IPA Handbook 1999, p. 23](https://en.wikipedia.org/wiki/Extra-shortness); Athabaskan reduced grades in Krauss & Golla 1981).

**ASCA 0.10.2 does not accept breve diacritics in sound-change rules.** The `@{Breve}` named escape exists only in **romanisation** rules (`=>`), not in `>` rules. ASCA models vowel shortness via **`[-long]`** (not `[+short]`); there is no third “extra-short” length tier beyond short / long / overlong.

| Subcluster | rows | Recommendation | Confidence |
|---|---:|---|---|
| Tai `ı̆`/`j̆`, `ɨ̆` (§38.1.1.x) | 10 | **`compile_transform`** — strip breve; `ı̆`→`j`, `ɨ̆`→`ɨ` (optionally `ɨ:[-long]` where vowel) | medium |
| Scots `ə̆` (§17.7.2.1.10) | 1 | **`compile_transform`** — `ə̆` → `ə:[-long]` | high |
| Tanacross `{æ̆,ă} æ̆ ŏ` (§29.1.1.1.37) | 1 | **`compile_transform`** — breve vowels → `segment:[-long]`; nested output set is a separate issue | medium |
| Slavic `i → ı̆ [ə?]` (§46.14) | 1 | **`skip`** — chained optional rule; breve is not the only blocker | high |

**No class-first `parse_ipa_map` row** works globally: breve attaches to many bases (`j`, `ɨ`, `ə`, `æ`, `a`, `o`) and `ı→j` must run before breve stripping on Tai `ı̆`.

**Follow-on:** file correction-pass ticket for `normalize_asca_breve_marks()` compile transform (parallel seam to `normalize_asca_length_marks()`). Slavic §46.14 → `status: skipped`.

## Linguistic intent by subcluster

### Tai (Li 1977) — §38.1.1.3–38.1.1.5

Source: Li, Fang Kuei (1977), *A Handbook of Comparative Tai*; Index sections cite this throughout Tai chapters.

| HTML line | Rule (Index) | Gloss |
|---:|---|---|
| 13128 | `iə → ı̆ / _C%` | Proto-Tai diphthong *iə shortens to extra-short reduced vowel/glide in closed syllable |
| 13142 | `ɨə → ɨ̆ / _C%` | Parallel shortening of *ɨə |
| 13143 | `ɨ̆ i̯o → u ə` | Further monophthongisation chain |
| 13228–13229 | `iə → ı̆`, `ɨ̆ → a / _K` | North Tai reflexes |
| 13258–13268 | Po-Ai chains incl. `ɨ̆ə → ɨ̆`, `ɛ iɛ → eː ı̆` | Po-Ai reduced-vowel developments |
| 13324 | `iə → ı̆ / _C%` | Southwest Tai (not all languages) |

**Intent:** Breve marks an **extra-short reduced vowel** (often realized as a glide / centralized vowel) after diphthong collapse in closed syllables (`_C%`). Same sections use `V → Vː / _%` for **long** vowels — breve and macron are contrastive length notation, not interchangeable.

**Pipeline note:** After ticket 63's `ı→j` IPA map, inventory shows `j̆` / `ɨ̆` (HTML still has `ı̆`). The underlying glyph is dotless-i + combining breve.

**Index editor on breve elsewhere:** §46.18 NB (line 14468) notes author uses `ı̆` but calls it “centralized” → editor rewrites as `/ɨ/`. Supports reading breve-marked `ı̆` as a **centralized/reduced** vowel, not a distinct phoneme letter.

### Scots — §17.7.2.1.10

| HTML line | Rule | Gloss |
|---:|---|---|
| 5955 | `∅ → ə̆ / _{n,r}` | Epenthetic **extra-short schwa** before /n, r/ (cf. English police [pə̆ˈliˑs]) |

**Intent:** Classic IPA breve = extra-short duration. ASCA `[-long]` is the accepted encoding.

### Tanacross (Athabaskan) — §29.1.1.1.37

| HTML line | Rule | Gloss |
|---:|---|---|
| 10325 | `ɑ ə ʊ → {æ̆,ă} æ̆ ŏ` | Vowel **reduction / raising** to extra-short reduced grades |

Parallel Lower Tanana rule (line 10334): `e a {ɑ,ʊ} → æ ɔ ŭ` — same author source (Krauss & Golla 1981) uses breve on `ŭ` without breve on `æ`. Tanacross rule is a **graded vowel shift** with breve marking the shortest/reduced reflexes.

**Intent:** Americanist extra-short vowel notation for Athabaskan reduced vowel system. `{æ̆,ă}` is an **output allomorph set** (two breve vowels for one input `ɑ`).

### Slavic — §46.14

| HTML line | Rule | Gloss |
|---:|---|---|
| 14438 | `i → ı̆ [ə?] → {e,a} (strong)/∅ (weak)` | Yer-like **reduced vowel** with optional schwa; strong/weak stem allomorphy |

**Intent:** Multi-stage chain with optional `[ə?]` and prose allomorphy labels. Not a single-segment breve mapping problem — the rule is structurally unrepresentable in ASCA even after breve fix.

## Convention survey

### IPA / Americanist

- **IPA:** Combining breve U+0306 = **extra-short** segment ([IPA Handbook 1999](https://en.wikipedia.org/wiki/Extra-shortness)).
- **Americanist (NAPA):** No single breve standard across schools; length more often marked with raised dot (`a·`) or macron ([Wikipedia: Americanist phonetic notation](https://en.wikipedia.org/wiki/Americanist_phonetic_notation)). Index Athabaskan rules follow Krauss/Golla reduced-vowel breve usage.
- **Tai (Li 1977):** Dotless `ı` with breve for reduced reflex of *iə; Index mirrors this as `ı̆`.

### ASCA 0.10.2

From [doc.md § Length](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#length):

| Length | ASCA feature |
|---|---|
| Short | `[-long]` |
| Long | `[+long]` |
| Overlong | `[+overlong]` |

- **`[ +short]`** → `Unknown feature 'short'` (env `u[+short]` maps to `[-long]` via `feature_mappings.csv` at parse time — unrelated to breve **segment** glyphs).
- **`@{Breve}`** listed under Named Escapes but only usable in **romanisation** (`=>`) rules, not sound-change (`>`) rules.
- Precomposed breve letters (`ă`, `ŭ`, `ŏ`) → `Unknown character`.

### Brassica

[Writing Sound Changes](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md) has no breve or extra-short vowel notation. Length is handled via feature bundles / rule logic, not breve diacritics. **No Brassica analogue** — defer to ASCA compile transform; revisit when Brassica compiler lands (ADR-0001).

## ASCA acceptance probes (0.10.2, `validate_asca`)

Probed 2026-08-19 via `uv run python` + `DiachronicSeries` smoke rules.

### Breve segment glyphs

| Form | Result | Error (if any) |
|---|---|---|
| `j̆` | ✗ | Unknown character `̆` |
| `ɨ̆` | ✗ | Unknown character `̆` |
| `ə̆` | ✗ | Unknown character `̆` |
| `ă` | ✗ | Unknown character `ă` |
| `æ̆` | ✗ | Unknown character `̆` |
| `ŭ` | ✗ | Unknown character `ŭ` |
| `ŏ` | ✗ | Unknown character `ŏ` |
| `ı̆` | ✗ | Unknown character `ı` (dotless i also rejected) |

### Segment + `[-long]`

| Form | Result |
|---|---|
| `j:[-long]` | ✓ |
| `ɨ:[-long]` | ✓ |
| `ə:[-long]` | ✓ |
| `æ:[-long]` | ✓ |
| `a:[-long]` | ✓ |
| `o:[-long]` | ✓ |

### Bare segments (breve stripped)

| Form | Result |
|---|---|
| `j` | ✓ |
| `ɨ` | ✓ |
| `ə` | ✓ |
| `iə > j / _C$` | ✓ |
| `ɨə > ɨ / _C$` | ✓ |
| `ɨ i̯o > u ə` | ✓ |
| `∅ > ə:[-long] / _{n,r}` | ✓ |
| `ɑ ə ʊ > {æ:[-long],a:[-long]} æ:[-long] ɑ` | ✓ |
| `ɛ iɛ > e:[+long] j` | ✓ |

### Length / feature probes

| Form | Result | Error (if any) |
|---|---|---|
| `V:[+short]` | ✗ | Unknown feature `short` |
| `V:[-long]` | ✓ | |
| `j@{Breve}` (sound-change rule) | ✗ | `@{Breve}` not valid in `>` rules |

### Slavic chain (structural)

| Form | Result |
|---|---|
| `i > j` | ✓ |
| `i > j̆ [ə?]` | ✗ (breve + optional segment) |

## Section-complete impact ranking

Inventory baseline: `rule-inventory-error.csv` (2026-08-19). **13** breve rows across **8** sections.

| Rank | Subcluster | rows | Sections helped | Mono-class section? | Near-miss (≤2 other fails)? |
|---:|---|---:|---|:---:|:---:|
| 1 | Scots `ə̆` | 1 | 17.7.2.1.10 | **yes** (+1 all-OK section) | yes |
| 2 | Tai | 10 | 38.1.1.3, .3.1, .4, .4.2, .5 | no | 4 sections with ≤2 other fails |
| 3 | Tanacross | 1 | 29.1.1.1.37 | no (3 other fails) | no |
| 4 | Slavic | 1 | 46.14 | no (3 other fails) | no |

**Clearing all 13 breve rows:** **+1** section all-OK (Scots only). **5 / 13** rows sit in ≤3-fail sections; **1** mono-class near-miss (Scots). Low leverage vs tickets #81–#83 — run breve correction pass **in parallel**, not ahead of them.

## Recommendations

### 1. Tai — `compile_transform` (medium)

Add `normalize_asca_breve_marks()` at ASCA compile (after `ı→j` IPA normalisation, before `validate_asca`):

1. Strip U+0306 combining breve from any segment.
2. Do **not** add `[-long]` on glide outputs (`j̆` → `j`); optional `ɨ̆` → `ɨ:[-long]` if preserving extra-short semantics on vowels (both validate).

**Rationale:** Tai breve on `ı̆` marks a glide-like reduced reflex; bare `j` validates and matches Li's semivocalic notation. `ɨ̆` as input/output vowel can strip to `ɨ` (lossy) or `ɨ:[-long]` (ASCA-native extra-short).

**Risk:** Stripping breve loses contrast with plain `ɨ` in chains where both appear — review Po-Ai §38.1.1.4.2 after implementation.

### 2. Scots — `compile_transform` (high)

`ə̆` → `ə:[-long]`. Single rule, unambiguous IPA extra-short schwa.

### 3. Tanacross — `compile_transform` + nested-set fix (medium)

Map breve vowels to `segment:[-long]`:

- `æ̆` → `æ:[-long]`
- `ă` → `a:[-long]` (decompose NFC first)
- `ŏ` → `o:[-long]`

Output `{æ̆,ă}` may still need **nested-set flattening** (inventory also reports `NestedBrackets` for expanded form). Track separately from breve transform.

### 4. Slavic — `skip` (high)

`i → ı̆ [ə?] → {e,a}/∅` is a **chained optional multi-output** rule. Hold out §46.14 rule `Pre-Slavic-Vowel-Changes-i` as `status: skipped`; do not block breve pass on this row.

### Not recommended

| Approach | Why |
|---|---|
| Global `parse_ipa_map` `̆→…` | Breve is a combining mark on multiple bases; not one IPA letter |
| `V:[+short]` feature map | ASCA rejects `[+short]`; unrelated to segment breve |
| `@{Breve}` in rules | Romanisation-only syntax |
| Bundling with #79 `ː` | Different layer (length macron vs breve diacritic) |

## Out of scope

- Implementing transforms (follow-on correction pass)
- Slavic yer chain `u → ŭ [ɤ?]` (line 14443) — uses breve on `ŭ` but not in current 13-row inventory
- Brassica compile path

## References

- [Spike ticket #80](../issues/80-spike-breve-vowel-notation.md)
- [Correction pass: near-miss unknown_character #63](../issues/63-correction-pass-near-miss-unknown-character.md)
- [ASCA ejective notation research](./asca-ejective-notation.md) — compile-transform seam precedent
- [ASCA length marks](../../src/conlanger/tools/compile/asca/length_marks.py)
- Li, Fang Kuei (1977). *A Handbook of Comparative Tai*. Oceanic Linguistics Special Publications 15.
- Krauss, Michael & Victor Golla (1981). "Northern Athapaskan Languages". *Handbook of North American Indians* Vol. 6.
