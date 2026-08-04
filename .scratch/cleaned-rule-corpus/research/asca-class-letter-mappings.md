# ASCA feature-matrix expansions for Index class letters

Spike for [09-spike-asca-class-letter-feature-matrices](../issues/09-spike-asca-class-letter-feature-matrices.md).  
Primary sources: **ASCA 0.10.2** ([`doc/doc.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md), [`CHANGELOG.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/CHANGELOG.md)), Index Diachronica Key to Abbreviations ([`data/diachronica/sound_change_abbreviations.txt`](../../../data/diachronica/sound_change_abbreviations.txt), [HTML §5](file:///home/pappa/Projects/Pappa/conlanger/notebooks/data/index_diachronica_original.html#Abbreviations)), current [`src/conlanger/data/group_mappings.csv`](../../../src/conlanger/data/group_mappings.csv), and [`asca-rule-validity.md`](./asca-rule-validity.md).

**Runtime constraint:** `IndexDiachronicaParser.apply_group_mappings` uses `str.maketrans` (single-character keys → replacement strings). Expansions must be valid ASCA tokens once substituted; nested Index letters inside a replacement (e.g. `{S,G}`) are **not** re-translated in the same pass (verified locally).

---

## Executive conflicts (Index vs ASCA)

| Index letter | Index meaning | ASCA same letter | Conflict |
|--------------|---------------|------------------|----------|
| **S** | Plosive | **S** = Sonorant (nasals + liquids) | Opposite class |
| **P** | Labial/bilabial | **P** = Plosive | Opposite class |
| **R** | Resonant/sonorant | **R** not a grouping; word alias = /ʀ/ | Unknown grouping if unmapped |
| **Q** | Uvular **or** click | **Q** not a grouping (TODO in crate) | Dual meaning, no built-in |
| **M** | Diphthong | No diphthong grouping | No faithful class |
| **A, B, E, H, J, K, Ḱ, T, U, W, Z** | See Key | Word-only IPA aliases (§ Inbuilt Aliases) | Must remap before ASCA parse |
| **C, O, F, L, N, V** | Consonant, Obstruent, Fricative, Liquid, Nasal, Vowel | Same grouping semantics (C since 0.10.0) | **Align — omit from CSV** |

ASCA inbuilt groupings ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings), [`src/rule/parser.rs` `get_group`](https://github.com/Girv98/asca-rust/blob/0.10.2/src/rule/parser.rs)):

| Group | Matrix (0.10.2) |
|-------|-----------------|
| **C** | `[+cons, -syll]` |
| **O** | `[+cons, -son, -syll]` |
| **S** | `[+cons, +son, -syll]` |
| **P** | `[+cons, -son, -syll, -delrel, -cont]` |
| **F** | `[+cons, -son, -syll, -approx, +cont]` |
| **L** | `[+cons, +son, -syll, +approx]` |
| **N** | `[+cons, +son, -syll, -approx, +nasal]` |
| **G** | `[-cons, +son, -syll]` |
| **V** | `[-cons, +son, +syll]` |

**C grouping change (0.10.0):** `C` = `[+cons, -syll]` (glides excluded); use `{C,G}` or `[-syll]` when Index “consonant” intent includes semivowels ([CHANGELOG 0.10.0](https://github.com/Girv98/asca-rust/blob/0.10.2/CHANGELOG.md), [Considerations in doc.md](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)).

---

## Summary table

| Index | Index meaning | Current CSV | Recommended ASCA expansion | Confidence | Source |
|-------|---------------|-------------|----------------------------|------------|--------|
| **A** | Affricate | `[+delrel]` | `O:[+delrel]` | high | [Groupings O,P](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings); P requires `-delrel`; affricates = obstruent + delayed release |
| **B** | Back vowel | `V:[+back]` | `V:[+back]` | high | [Subnode +back](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode); host **V** avoids dorsal consonants |
| **C** | Consonant | *(no row)* | *(omit — identity)* | high | Index = ASCA **C** `[+cons,-syll]` since 0.10.0 |
| **D** | Voiced plosive | `P:[+voice]` | `P:[+voice]` | high | [Groupings P](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings) + [voice feature](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands) |
| **E** | Front vowel | `V:[+front]` | `V:[+front]` | high | [Subnode +front](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode) |
| **F** | Fricative | *(no row)* | *(omit — identity)* | high | Index = ASCA **F** |
| **H** | Laryngeal | `[-place]` | `[-place]` | medium | [Subnode `-place` → glottals](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode); misses pharyngeals/epiglottals (`[+pharyngeal]`) if Index meant those |
| **J** | Approximant | `[+approximant]` | `{L,G}` | high | [Groupings L,G](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings); bare `[+approximant]` also matches vowels ([Feature shorthands](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands)) |
| **K** | Velar | `[+cons,-fr,+bk,+hi,-lo]` | `C:[-front,+back,+hi,-lo]` | high | Crate TODO for **K** velar ([`parser.rs` L780](https://github.com/Girv98/asca-rust/blob/0.10.2/src/rule/parser.rs)); **C:** host matches `SoundChangeRuleSet.aliases` intent |
| **Ḱ** | Palatovelar | `[+cons,+front,+high]` | `C:[+front,+hi,-lo]` | medium | No exact palatovelar node; nearest dorsal +front +hi consonant; overlaps plain palatals |
| **L** | Liquid | *(no row)* | *(omit — identity)* | high | Index = ASCA **L** |
| **M** | Diphthong | `VV` | **unmapped** (validation cluster) | low | No diphthong feature/group; `VV` = two **V** tokens ([Sets/sequences](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#sets)), not a syllable nucleus class; fails as output token (`unknown_grouping` in inventory) |
| **N** | Nasal | *(no row)* | *(omit — identity)* | high | Index = ASCA **N** |
| **O** | Obstruent | *(no row)* | *(omit — identity)* | high | Index = ASCA **O** |
| **P** | Labial/bilabial | `C:[+labial]` | `C:[+labial]` | high | [Subnode +labial](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode); avoids ASCA **P** (plosive) |
| **Q** | Uvular or click | `[+click]` | `{C:[-front,+back,-hi,-lo],[+click]}` | medium | Crate TODO for **Q** uvular ([`parser.rs` L781](https://github.com/Girv98/asca-rust/blob/0.10.2/src/rule/parser.rs)); [click feature](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands); dual meaning remains ambiguous |
| **R** | Resonant/sonorant | `S` | `[+son,-syll]` | high | ASCA **S** = nasals+liquids only; Index **R** includes glides (**W**); `[+son,-syll]` = **S** ∪ **G** ([parser.rs](https://github.com/Girv98/asca-rust/blob/0.10.2/src/rule/parser.rs)) |
| **S** | Plosive | `P` | `P` | high | Index plosive ↔ ASCA **P** ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)) |
| **T** | Voiceless plosive | `P:[-voice]` | `P:[-voice]` | high | ASCA **P** + [-voice](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands) |
| **U** | Syllable | `%` | `%` | medium | ASCA **`%`** = whole syllable ([Special Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters)); Index **`%`** = syllable *boundary* → ASCA **`$`**, not **`%`** — symbol mapping is separate (ticket 06) |
| **V** | Vowel | *(no row)* | *(omit — identity)* | high | Index = ASCA **V** |
| **W** | Semivowel | `G` | `G` | high | ASCA **G** = glides `[-cons,+son,-syll]` ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)) |
| **Z** | Continuant | `[+continuant]` | `[+cont]` | medium | [continuant feature](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands); includes vowels and fricatives; excludes stops/affricates (`-cont` / **A** class) |

---

## Per-letter analysis

### Letters aligned with ASCA (no CSV row)

**C, O, F, L, N, V** — Index definitions match ASCA groupings ([Key to Abbreviations](../../../data/diachronica/sound_change_abbreviations.txt), [doc.md Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)). Do **not** add rows: extra mappings would break rules that rely on ASCA-native semantics (especially **C** post-0.10.0).

**C caveat:** Index “consonant” in prose sometimes includes semivowels; ASCA **C** excludes glides. Section-specific `{C,G}` overrides belong in validation clusters, not the global CSV.

---

### A — Affricate

- **Index:** `A = Affricate` ([sound_change_abbreviations.txt L13](../../../data/diachronica/sound_change_abbreviations.txt)).
- **ASCA:** No affricate grouping. Plosives **P** require `-delrel`; affricates are obstruents with `+delrel` ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)).
- **Current:** `[+delrel]` — valid but matches any segment with delayed release without obstruent scope.
- **Recommended:** `O:[+delrel]` — obstruent affricates (matches `t͡s`, `d͡ʒ`, etc.).
- **Gap:** Prenasalised stops and edge affricate/fricative splits may need cluster overrides.

---

### B — Back vowel

- **Index:** `B = Back vowel`.
- **ASCA:** `V:[+back]` using dorsal subnode [+back](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode).
- **Current:** Correct.
- **Gap:** Bare `[+back]` also matches velars/uvulars; keep **V:** host.

---

### D — Voiced plosive / T — Voiceless plosive

- **Index:** `D = Voiced plosive`, `T = Voiceless plosive`.
- **ASCA:** **P** = `[+cons,-son,-syll,-delrel,-cont]` ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)).
- **Recommended:** `P:[+voice]` / `P:[-voice]` — matches inventory normalisation patterns.
- **Gap:** Ejectives / implosives have non-binary laryngeal features; may need cluster rules.

---

### E — Front vowel

- Same pattern as **B** with `V:[+front]`. Current row is correct.

---

### H — Laryngeal

- **Index:** `H = Laryngeal` (typically /h/, /ɦ/, /ʔ/).
- **ASCA:** `[-place]` → “glottal segments; h, ɦ, ʔ, etc.” ([Matching a subnode](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode)). `[+laryngeal]` names the **laryngeal node**, not a matchable ± feature ([Nodes and Subnodes](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#nodes-and-subnodes)).
- **Current:** `[-place]` — best global default.
- **Gap:** Pharyngeals/epiglottals (ħ, ʕ, ʜ) use `[+pharyngeal]`, not `[-place]`. Optional cluster expansion: `{[-place],[+pharyngeal]}`.

---

### J — Approximant

- **Index:** `J = Approximant` (j, w, l, etc. in section tables).
- **ASCA:** **L** = liquids; **G** = glides ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)).
- **Current:** `[+approximant]` — overbroad (vowels are +approximant).
- **Recommended:** `{L,G}` — consonantal approximants without nasals (Index **N** is separate).

---

### K — Velar / Ḱ — Palatovelar

- **Index:** `K = Velar`, `Ḱ = Palatovelar`.
- **ASCA:** Commented future groupings in [`parser.rs` L779–781](https://github.com/Girv98/asca-rust/blob/0.10.2/src/rule/parser.rs):
  - **K** (velar): `[+cons, -fr, +bk, +hi, -lo]`
  - **Q** (uvular): `[+cons, -fr, +bk, -hi, -lo]`
- **Current K:** Same matrix as [`SoundChangeRuleSet.aliases`](../../../src/conlanger/tools/SoundChangeRuleSet.py) but without **C:** host — can match high back vowels.
- **Recommended K:** `C:[-front,+back,+hi,-lo]` (equivalent shorthands: `-fr`, `+bk`).
- **Recommended Ḱ:** `C:[+front,+hi,-lo]` — palatal/palatovelar consonants; not exact (medium confidence).

---

### M — Diphthong

- **Index:** `M = Diphthong`.
- **ASCA:** No diphthong class, no “two nuclei in one syllable” predicate.
- **Current:** `VV` — parses as **two** **V** groupings in sequence; works for some rules (`VV > V` passes inventory) but:
  - Fails when **M** is a standalone output (`VrV > V:[+long], M` → `unknown_grouping`).
  - `{M,V:[+long]}` env-set conditions (Tamil 14.3.1) cannot be fixed globally.
- **Recommendation:** **Remove row; leave unmapped.** Treat **M** via validation clusters (section-specific rewrites, prose excision, or hand-authored rules).
- **Do not** claim `VV` is faithful Index semantics.

---

### P — Labial/bilabial

- **Index:** `P = Labial/Bilabial`.
- **ASCA:** **P** = Plosive — must remap.
- **Recommended:** `C:[+labial]` ([+labial subnode](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode)).

---

### Q — Uvular or click

- **Index:** `Q = Uvular consonant; click consonant (Khoisan)` — intentional disjunction.
- **ASCA:** `[+click]` feature ([Feature shorthands](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands)); uvular place per crate TODO `[+cons,-fr,+bk,-hi,-lo]`.
- **Current:** `[+click]` only — misses uvulars (e.g. /q/, /χ/, /ʁ/).
- **Recommended:** `{C:[-front,+back,-hi,-lo],[+click]}` — union of uvular consonants and click segments.
- **Gap:** Index does not disambiguate uvular vs click in notation; same letter in one rule may mean only one branch — cluster review required.

---

### R — Resonant/sonorant

- **Index:** `R = Resonant/Sonorant`.
- **ASCA:** **S** = nasals + liquids only (excludes glides) ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings)).
- **Current:** `S` — too narrow (drops semivowels / **W**).
- **Recommended:** `[+son,-syll]` — all consonantal sonorants (**S** ∪ **G**), excludes vowels (**V**).

---

### S — Plosive

- **Index:** `S = Plosive`.
- **ASCA:** **S** = Sonorant — direct letter clash.
- **Recommended:** `P` (ASCA plosive grouping). Current row is correct.

---

### U — Syllable

- **Index:** `U = Syllable`.
- **ASCA:** `%` = whole syllable ([Special Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters)).
- **Recommended:** `%` when **U** denotes a syllable constituent (not a single segment).
- **Gap:** Index **`%`** is syllable *boundary* → ASCA **`$`**, handled under symbol normalisation (ticket 06), not this CSV. **`%` ↔ segment** substitutions remain invalid per ASCA typing.

---

### W — Semivowel

- **Index:** `W = Semivowel`.
- **ASCA:** **G** = glides `[-cons,+son,-syll]`.
- **Recommended:** `G`. Current row is correct.

---

### Z — Continuant

- **Index:** `Z = Continuant` (contrasts with **S** plosive and often **A** affricate).
- **ASCA:** `[+cont]` / `[+continuant]` ([Feature shorthands](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands)).
- **Recommended:** `[+cont]` — fricatives, approximants, vowels; excludes plosives (`-cont`) and typical affricates (`-cont,+delrel`).
- **Gap:** Nasals are `-cont`; trills/taps vary; overincludes vowels when rule meant “consonantal continuant only” (`{F,L,G}` or `O:[+cont]`).

---

## Inventory: `unknown_grouping` failures

From [`.scratch/cleaned-rule-corpus/inventory/asca-rule-inventory.csv`](../inventory/asca-rule-inventory.csv) (16 `unknown_grouping` rows):

| Grouping | Typical cause | CSV / cluster action |
|----------|---------------|----------------------|
| **M** | Diphthong | **Unmapped** — cluster (see above) |
| **X** | Meta-variable “any segment” ([Key `(…X)`](../../../data/diachronica/sound_change_abbreviations.txt)) | Not a class letter — validation cluster |
| **Y**, **I** | Section-local series (Tlapanec, Finnic, Salish) | Not in Key — cluster / section overrides |
| **M** in `V_V (Marathi)` | Prose paren, not grouping | Parser/fog fix, not CSV |

No inventory `unknown_grouping` for **A, B, D, E, H, J, K, P, Q, R, S, T, U, W, Z** once rows below are applied — remaining failures are meta-notation or **M**.

---

## Recommended `group_mappings.csv`

Paste-ready block (18 rows — aligned letters omitted; **M** removed):

```csv
grouping,mapping,comment
A,O:[+delrel],Index affricate → obstruent with delayed release (ASCA has no affricate grouping)
B,V:[+back],Index back vowel; V host avoids matching velar/uvular consonants
D,P:[+voice],Index voiced plosive
E,V:[+front],Index front vowel; V host avoids matching palatal consonants
H,[-place],Index laryngeal ≈ glottals (h ɦ ʔ); pharyngeals need cluster override
J,{L,G},Index approximant ≈ liquids + glides; avoids bare [+approximant] matching vowels
K,C:[-front,+back,+hi,-lo],Index velar consonant (matches crate TODO K matrix with C host)
Ḱ,C:[+front,+hi,-lo],Index palatovelar approx; overlaps palatals — medium fidelity
P,C:[+labial],Index labial/bilabial; not ASCA P (plosive)
Q,{C:[-front,+back,-hi,-lo],[+click]},Index uvular OR click; dual meaning — cluster disambiguation often required
R,[+son,-syll],Index resonant/sonorant ≈ ASCA S ∪ G (not ASCA S alone)
S,P,Index plosive ↔ ASCA plosive grouping P
T,P:[-voice],Index voiceless plosive
U,%,Index syllable ≈ ASCA whole-syllable % (Index % boundary → ASCA $ separately)
W,G,Index semivowel ≈ ASCA glides G
Z,[+cont],Index continuant; includes vowels — use {F L G} or O:[+cont] in clusters if too broad
```

### Changes from current CSV

| Letter | Change |
|--------|--------|
| **A** | `[+delrel]` → `O:[+delrel]` |
| **J** | `[+approximant]` → `{L,G}` |
| **K** | bare matrix → `C:[-front,+back,+hi,-lo]` |
| **Ḱ** | bare matrix → `C:[+front,+hi,-lo]`; fix `+high` → `+hi` shorthand |
| **M** | **Row removed** — no faithful mapping |
| **Q** | `[+click]` → `{C:[-front,+back,-hi,-lo],[+click]}` |
| **R** | `S` → `[+son,-syll]` |
| **Z** | `[+continuant]` → `[+cont]` (equivalent; shorter canonical shorthand) |

---

## Source index

| Claim | Primary source |
|-------|----------------|
| Index class letter definitions | [`data/diachronica/sound_change_abbreviations.txt`](../../../data/diachronica/sound_change_abbreviations.txt); [HTML §5 Key to Abbreviations](file:///home/pappa/Projects/Pappa/conlanger/notebooks/data/index_diachronica_original.html#Abbreviations) |
| ASCA grouping matrices | [doc.md § Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings); [`src/rule/parser.rs` `get_group`](https://github.com/Girv98/asca-rust/blob/0.10.2/src/rule/parser.rs) |
| C = `[+cons,-syll]` breaking change | [CHANGELOG 0.10.0](https://github.com/Girv98/asca-rust/blob/0.10.2/CHANGELOG.md) |
| Place/laryngeal subnodes | [doc.md § Matching a subnode](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#matching-a-subnode) |
| Feature shorthands (`delrel`, `click`, `cont`, `bk`, `fr`, …) | [doc.md § Feature Shorthands](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands) |
| `%` syllable, `$` boundary | [doc.md § Special Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters) |
| Word-only capital aliases (not rule groupings) | [doc.md § Inbuilt Aliases](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#inbuilt-aliases) |
| K/Q velar/uvular TODO matrices | [`src/rule/parser.rs` L778–781](https://github.com/Girv98/asca-rust/blob/0.10.2/src/rule/parser.rs) |
| Validity / pipeline | [`asca-rule-validity.md`](./asca-rule-validity.md) |
| `maketrans` application | [`IndexDiachronicaParser.apply_group_mappings`](../../../src/conlanger/tools/IndexDiachronicaParser.py) |
