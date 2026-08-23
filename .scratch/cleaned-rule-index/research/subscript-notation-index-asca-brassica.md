# Subscript notation: Index Diachronica vs ASCA vs Brassica

Primary-source comparison of how the four Index Diachronica **subscript notation** uses map (or fail to map) onto ASCA 0.10.2 and Brassica, and what that implies for HTML→YAML **parse/ingest** vs applier **compile**.

---

## 1. Executive summary

Index Diachronica encodes four distinct subscript uses under one HTML `<sub>` mechanism; ASCA and Brassica each have **no** Unicode-subscript grammar. Correspondence-series and collective uses become **ordinary phonological content** once expanded (IPA segments / member lists), so both appliers can consume them after ingest — but ASCA **sets** `{a,b}` and Brassica **categories** `[a b]` are different surface forms for the same idea. Positional slots and identity subscripts are **co-reference / template machinery**: ASCA uses numbered **references** (`C=1` … `2`, `V=0` … `0`); Brassica uses **identifier/numeric backreferences** (`@#id Category`, `@n Category`) and, for adjacent duplicates, **gemination** (`>`). Those surface forms are incompatible and must not be baked into applier-neutral YAML.

**Parse-time vs compile-time takeaway (by use):**

| Use | Recommendation |
|-----|----------------|
| Correspondence-series index | **Parse-time** expand to concrete IPA (already decided: ticket 26 / ADR-0004 amendment). |
| Collective subscript | **Parse-time** expand to a member list / set (already decided); prefer structured members over opaque ASCA `{…}` if Brassica remains a real target. |
| Positional slot | **Compile-time** per applier; keep Index-shaped `C₁`… in YAML. |
| Identity subscript | **Compile-time** per applier; keep Index-shaped `V₀`… in YAML. |

---

## 2. Glossary alignment

Restate from [`CONTEXT.md`](../../../CONTEXT.md) (do not conflate):

| Term | Meaning | CONTEXT anchor |
|------|---------|----------------|
| **Correspondence-series index** | Ordinal subscript on a *concrete segment* selecting the *n*th series member for that section (`s₁`, `x₂`, `eh₂`) | [Correspondence-series index](../../../CONTEXT.md) |
| **Positional slot** | Ordinal subscript on a *class letter* for numbered template co-reference (`C₁C₂ → C₂`) | [Positional slot](../../../CONTEXT.md) |
| **Identity subscript** | `₀` co-reference (“same instance”) (`V₀V₀ → V₀`) | [Identity subscript](../../../CONTEXT.md) |
| **Collective subscript** | `ₓ` / `x` “all members” (`{Hₓ,m̩,n̩} → a`, `sₓ → ʃ`) | [Collective subscript](../../../CONTEXT.md) |

Index HTML Key ([`index_diachronica_original.html`](../../../data/diachronica/index_diachronica_original.html) §5, lines 898–901) collapses two of these into one bullet:

> `Xₙ` = The *n*th X of a sequence or series  
> `Xₓ` = All X of a sequence or series  
> `X₀` = The same/an identical X

Project glossary splits `Xₙ` by base type (class letter → positional; concrete segment → correspondence-series). HTML `<sub>x</sub>` normalises to Unicode `ₓ` via `SUBSCRIPT_MAP` in [`parsers.py`](../../../src/conlanger/tools/parsers.py).

### Similar terms that must not be conflated

| Foreign term | Looks like | Actually means | Source |
|--------------|------------|----------------|--------|
| ASCA optional `(C,0)` / prose “standard notation `C₀`” | Index identity `C₀` | Zero-or-more repetition in **env/structure**, not co-reference | [ASCA Optionals](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#optionals) |
| ASCA **alpha notation** (`α`, `A`…`Z`) | Slot / identity labels | Feature-polarity / node agreement across segments | [ASCA Alpha Notation](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#alpha-notation) |
| Brassica **category index** (1st/2nd element of `[p t k]` ↔ `[b d g]`) | Correspondence-series index | Parallel membership order inside categories, not Index `s₁` reconstruction labels | [Writing Sound Changes — Categories in the replacement](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#categories-in-the-replacement) |
| Brassica **geminate** `>` | Identity subscript | “Same grapheme as last matched/produced” (adjacent only) | [Writing Sound Changes — Gemination](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#gemination) |
| Brassica `@n` **numeric backreference** | Index `Cₙ` | Refers to the *n*th *matched category* in the target list, not Index series member *n* | [Reference — Category backreferences](https://github.com/bradrn/brassica/blob/master/docs/Reference.md#category-backreferences) |
| Index Athabaskan `TŠ` / uppercase `S₁` | Positional or series subscript | Often **section-local abbreviation**, not a subscript use | [`CONTEXT.md` Section-local abbreviation](../../../CONTEXT.md) |

Token classifiers in [`series_mappings.py`](../../../src/conlanger/tools/series_mappings.py): `classify_subscript_token`, `is_positional_slot_token`, `is_identity_subscript_token`, `is_collective_subscript_token` (lowercase base + `ₓ` only), `is_correspondence_series_token`. Uppercase `Hₓ` currently classifies as **`other`**, not `collective` — see coverage backlog.

---

## 3. Comparison tables

### 3.1 Correspondence-series index

| | Index Diachronica | ASCA 0.10.2 | Brassica |
|--|-------------------|-------------|----------|
| **Example** | `s₁ → ʃ` (Dizin, HTML:1015); `x₁ → k` (Bench, HTML:993); `eh₂` compounds | No subscript characters | No subscript characters |
| **Native representation** | Concrete segment + ordinal `<sub>` | **Unrepresentable** as `s₁` — `Unknown character '₁'` / `'ₓ'` (validated; see prior research + probe below) | **Unrepresentable** as Index subscripts (docs define graphemes/categories/backrefs only) |
| **Faithful workaround** | Section map → IPA / matrix / set in index fields; `raw` keeps `s₁` | After expansion: plain IPA / features / sets (`ʃ`, `{…}`) | After expansion: plain graphemes or categories (`ʃ`, `[…]`) |
| **Notes** | Requires **section-scoped** maps ([ADR-0004](../../../docs/adr/0004-series-indices-per-section-maps.md)); ASCA refs **cannot** attach to IPA literals (`IPACannotBeRefd` — [asca-rule-validity.md](./asca-rule-validity.md)) | Same phonological content once expanded; category *order* is a different mechanism |

### 3.2 Positional slot

| | Index Diachronica | ASCA 0.10.2 | Brassica |
|--|-------------------|-------------|----------|
| **Example** | `C₁C₂ → C₂` (Proto-Chamic, HTML:2793); `C₁ˤC₂ → C₁C₂ˤ` (Moroccan Arabic, HTML:1478) | `C=1 C=2 > 2` | `@#c1 C @#c2 C / @#c2 C` (identifier backrefs) or numeric `@1`/`@2` forms |
| **Native representation** | Class letter + ordinal subscript | **References** on groups/matrices/syllables: declare `X=n`, invoke bare `n` | **Category backreferences**: `@#id Category` (preferred) or `@n Category` |
| **Unrepresentable / rejected** | — | Unicode `C₁` → `Unknown character '₁'`; stripping subscripts changes meaning | No Index `C₁` syntax; must compile to Brassica backref form |
| **Notes** | Not expandable via `group_mappings.csv` / `series_mappings.csv` | Alpha notation is **wrong tool** (feature agreement, not slots) — [positional-slots research](./positional-slots-and-identity-subscripts.md) | Brassica tutorial itself describes the linguistic pattern as “V₁ʔC → V₁ʔV₁C” then shows `@#v V` syntax — [Backreferences](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#backreferences) |

### 3.3 Identity subscript

| | Index Diachronica | ASCA 0.10.2 | Brassica |
|--|-------------------|-------------|----------|
| **Example** | `V₀V₀ → V₀` (Chamorro, HTML:2816); `h → ʔ / V₀V₀` (Madurese, HTML:2896) | `V=0 V=0 > 0`; env `h > ʔ / _ V=0 V=0` | `@#v V @#v V / @#v V`; env co-ref via same `@#id` |
| **Native representation** | `X₀` = “same/identical X” (HTML:898) | Same **reference** machinery as slots; digit `0` is valid | Identifier backref forces same category index; **geminate** `>` for *adjacent* same grapheme only |
| **Trap** | — | Do **not** confuse with optional `(C,0)` “`C₀`” zero-or-more | Geminate `>` ≠ general `V₀…V₀` across non-adjacent sites |
| **Notes** | Compounds `mV₀`, `CʔV₀` need split/tokenization at compile | Feature-attached: `V:[+nas]=0` … (validated in positional-slots research) | Feature backrefs (`$Name#id`) are for **feature values**, not Index identity — [Feature syntax](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#feature-syntax) |

### 3.4 Collective subscript

| | Index Diachronica | ASCA 0.10.2 | Brassica |
|--|-------------------|-------------|----------|
| **Example** | `sₓ → ʃ` (Bench, HTML:997); `{ʔ,hₓ} → ∅` (Bench, HTML:998); `{Hₓ,m̩,n̩} → a` (Aeolian Greek, HTML:6557) | After map: `{s,ʃ} > tʃ` (set) — probe OK; literal `sₓ` → `Unknown character 'ₓ'` | After map: `[s ʃ] / tʃ` (inline category) or predefined category |
| **Native representation** | `Xₓ` = all of sequence/series (HTML:901) | **Sets** `{…}` ([Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#sets)) | **Categories** `[…]` / predefined ([Categories](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#categories-of-sounds)) |
| **Gap** | Lowercase `sₓ`/`hₓ` fit series maps; uppercase `Hₓ` is class-letter “all laryngeals” — backlog marks out of series CSV ([series-mappings-coverage-backlog.md](../series-mappings-coverage-backlog.md)) | Set syntax is ASCA-shaped | Category syntax is Brassica-shaped — **same members, different delimiters** |

---

## 4. ASCA deep dive (0.10.2)

Primary doc: [`doc/doc.md` @ tag 0.10.2](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md). Local CLI: `asca 0.10.2`.

### 4.1 References (positional + identity)

From [References](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#references):

> References are declared by using the `=` operator, followed by a number. This number can then be used later in the rule to invoke the reference.  
> Currently; matrices, groups, and syllables can be referenced.

Validated mappings (from [positional-slots-and-identity-subscripts.md](./positional-slots-and-identity-subscripts.md); re-confirmed earlier in that research):

| Index | ASCA |
|-------|------|
| `C₁C₂ → C₂` | `C=1 C=2 > 2` |
| `V₀V₀ → V₀` | `V=0 V=0 > 0` |
| `V₀V₀ → V₀ː` | `V=0 V=0 > 0:[+long]` |
| `h → ʔ / V₀V₀` | `h > ʔ / _ V=0 V=0` |

Constraints relevant to Index:

- IPA literals **cannot** be referenced → correspondence-series tokens cannot become ASCA refs; they must expand to segments first ([asca-rule-validity.md](./asca-rule-validity.md) References row).
- Unicode subscripts are syntax errors (`Unknown character`).

### 4.2 Alpha notation (not for slots/identity)

[Alpha Notation](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#alpha-notation): alphas copy feature polarity/nodes (assimilation, harmony). They do not encode “first consonant / second consonant” template positions. Do not use for `C₁`/`C₂` or `V₀`.

### 4.3 Sets / groupings (collective after expansion)

[Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#sets): curly-brace choice/mapping; [Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings): `C O S P F L N G V` as feature-matrix shorthands.

**New probe** (workspace temp, then deleted): `{s,ʃ} > tʃ` applies; literal `sₓ > ʃ` fails with `Unknown character 'ₓ'`. Optional rule `a > e / (C,0)_` parses — confirming ASCA’s `(C,0)` is **not** Index identity.

### 4.4 What ASCA does *not* have

- No Index-style series indices on segments.
- No collective `ₓ` quantifier.
- No shared notation with Brassica backrefs.

---

## 5. Brassica deep dive

Primary sources:

- [docs/README.md](https://github.com/bradrn/brassica/blob/master/docs/README.md)
- [Writing Sound Changes](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md)
- [Reference](https://github.com/bradrn/brassica/blob/master/docs/Reference.md)

Rule shape (different from ASCA): `target / replacement / environment` ([Sound change syntax](https://github.com/bradrn/brassica/blob/master/docs/Reference.md#sound-change-syntax)).

### 5.1 Categories ≈ classes / expanded collectives

Inline `[a e i o u]` or predefined `categories … end` ([Categories of sounds](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#categories-of-sounds)). Closest Brassica home for Index collective expansion and for class letters (once mapped to grapheme lists).

**No equivalent** of Index `sₓ` / `Hₓ` as a subscript operator — only expanded member lists.

### 5.2 Backreferences ≈ positional slots + identity

From [Backreferences](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#backreferences):

> Sometimes, categories in the target must be duplicated, deleted, or rearranged…  
> Brassica provides **identifier backreferences**. Specify these as `@#identifier` before a category…  
> Every category given the same identifier must take on a corresponding value.

Tutorial example (linguistic gloss uses Index-like `V₁`):

```brassica
@#v V ʔ / @#v V ʔ @#v V / _ C
```

[Reference — Category backreferences](https://github.com/bradrn/brassica/blob/master/docs/Reference.md#category-backreferences) also defines numeric `@n Category` (n ≥ 1). Identifier backrefs are the preferred modern form (numeric described as older/less capable in the tutorial).

**Implication for Index `C₁C₂ → C₂`:** compile toward something like `@#c1 C @#c2 C / @#c2 C` (or discard `~` for the dropped slot), **not** ASCA `C=1 C=2 > 2`.

**Implication for Index `V₀V₀ → V₀`:** `@#v V @#v V / @#v V` — same identifier forces identity. This is **co-reference of category index**, matching Index identity semantics more closely than gemination alone.

### 5.3 Gemination (narrow identity subset)

[Gemination](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#gemination): `>` matches/produces the **last** grapheme. Useful for adjacent duplicates (`[p t k] / / _ >`), **not** a general substitute for arbitrary `X₀` sites in env/output.

### 5.4 Phonetic features / feature backrefs (not Index subscripts)

[Phonetic features](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#phonetic-features) and `$Name#id` agree on **feature values** (e.g. vowel harmony). Closest cousin to ASCA alphas — **not** positional slots or correspondence-series indices.

### 5.5 What Brassica does *not* have

| Index use | Brassica gap |
|-----------|--------------|
| Correspondence-series `s₁` | No series-index syntax; expand offline |
| Collective `sₓ` / `Hₓ` | No collective subscript; expand to category members |
| Index Unicode subscripts | Not in grammar |
| ASCA-style `X=n` references | Different backref syntax entirely |

---

## 6. Parse-time vs compile-time implications

### 6.1 Already decided in this repo

| Decision | Source |
|----------|--------|
| Correspondence-series + collective → **parse-time** expansion when mapped; `raw` keeps Index; unmapped stay literal | [Ticket 26](../issues/26-parse-time-correspondence-series-indices.md), [ADR-0004 amendment](../../../docs/adr/0004-series-indices-per-section-maps.md) |
| Positional + identity **out of scope** for series maps; need reference/co-ref mapping | Same ADR / ticket 26 “Not in scope” |
| Applier-neutral YAML; ASCA/Brassica are compile targets | [ADR-0002](../../../docs/adr/0002-applier-neutral-yaml-rule-index.md), [ADR-0001](../../../docs/adr/0001-sound-change-applier-backends.md) |
| Validate **after** compile | [ADR-0003](../../../docs/adr/0003-validate-after-applier-compile.md) |
| Class-first fidelity; no silent subscript strip | [ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md) |
| ASCA-only research recommended compile-time refs for positional/identity | [positional-slots-and-identity-subscripts.md](./positional-slots-and-identity-subscripts.md) |

### 6.2 Per-use argument

#### Correspondence-series index — **parse-time** (confirmed)

- Expansion yields **shared phonological content** (specific IPA), not applier control syntax.
- ASCA cannot reference IPA; Brassica has no series indices — both need the expanded segment.
- Ticket 26 / ADR-0004 already chose parse-time (same seam as Symbol normalisation).
- **YAML:** store expanded IPA (when mapped); keep Index in `raw`. Unmapped `s₁` may remain Index-shaped until maps exist (option A).

#### Collective subscript — **parse-time** (confirmed), with IR caveat

- Semantics = “union of members” → ASCA set or Brassica category.
- Ticket 26 maps e.g. `sₓ → { s, ʃ }` (ASCA set spelling).
- **Tension with ADR-0002:** baking `{…}` into index fields is ASCA-shaped; Brassica wants `[s ʃ]` (space-separated).
- **Recommendation:** treat parse-time expansion as producing a **member list** (structured field or normalised set token that compilers rewrite). Near-term ASCA-only execution can keep `{…}` strings if Brassica compile stays deferred — but the ASCA↔Brassica delimiter gap is real.
- Uppercase `Hₓ`: not covered by lowercase collective classifier; needs class/set expansion (laryngeals), separate from `series_mappings.csv` rows for `sₓ`/`hₓ`.

#### Positional slot — **compile-time** (confirmed; Brassica reinforces)

- Remains Index-shaped in applier-neutral YAML (`C₁`, `V₂`).
- ASCA compiler → `C=1` / bare `n`; Brassica compiler → `@#…` / `@n` + category.
- Putting `C=1` in YAML would violate ADR-0002 relative to Brassica (and vice versa for `@#c1 C`).
- Class letters still go through `group_mappings` / category defs at compile as today.

#### Identity subscript — **compile-time** (confirmed; Brassica reinforces)

- Same reasoning as positional: shared Index `V₀` in YAML; applier-specific co-ref emission.
- Brassica may sometimes use `>` for adjacent-only cases; general env/output identity needs `@#id`.
- Do not parse-normalise `₀` away; do not confuse with ASCA `(C,0)`.

### 6.3 What stays Index-shaped in YAML

| Keep Index-shaped in `input`/`output`/`env`/`exception` | Expand at parse when mapped |
|----------------------------------------------------------|-----------------------------|
| Positional `C₁`, `N₂`, … | Correspondence `s₁`, `x₂`, … |
| Identity `V₀`, `C₀`, … | Collective `sₓ`, `hₓ`, … (and eventually `Hₓ` via class mechanism) |

`raw` always Index-shaped for all four.

### 6.4 Structured IR beyond opaque Index strings?

**Suggested by the ASCA↔Brassica gap — yes, selectively:**

1. **Positional / identity:** Index tokens *are* already a workable shared IR (`C₁`, `V₀`). Compilers project to refs/backrefs. No need to invent a third notation in YAML for those two uses.
2. **Correspondence:** Expanded **IPA string** is shared enough; structured “series member id → IPA” lives in section maps, not in every rule field.
3. **Collective (and multi-member correspondence sets):** A structured **member list** (e.g. YAML list or tagged set node) would let ASCA emit `{a,b}` and Brassica emit `[a b]` without choosing one applier’s delimiters at ingest. Ticket 26’s “ASCA-parseable sets in fields” is acceptable as an ASCA-first interim, but is the main place ADR-0002 pressure shows up.

---

## 7. Open questions

1. ~~**Collective IR shape:**~~ **Settled (grill):** ASCA `{…}` in index fields; Brassica `[…]` rewrite at compile if/when Brassica is supported.
2. **`Hₓ` / class-letter collectives:** Expand via `group_mappings` / section laryngeal inventory, or a dedicated collective-on-class path? (Classifier today: `other`.)
3. **Brassica category definitions for Index class letters:** Global `C`/`V`/… blocks vs per-section inventories — out of scope here, but required before a real Brassica compile of slot rules.
4. **Cross-field ASCA ref binding** for env-only identity (`h → ʔ / V₀V₀`) vs Brassica env backref scope — implementation detail already flagged in positional-slots research; still needs whole-rule compile tests per applier.
5. **Uppercase `S₁` / Formosan series labels:** positional vs section-local abbreviation — unresolved classification edge (not answered by Brassica/ASCA docs).

---

## 8. References

### Local

| Path | Role |
|------|------|
| [`CONTEXT.md`](../../../CONTEXT.md) | Four subscript uses + avoid-conflation notes |
| [`docs/adr/0001-sound-change-applier-backends.md`](../../../docs/adr/0001-sound-change-applier-backends.md) | ASCA-first, multi-applier boundary |
| [`docs/adr/0002-applier-neutral-yaml-rule-index.md`](../../../docs/adr/0002-applier-neutral-yaml-rule-index.md) | Applier-neutral YAML |
| [`docs/adr/0003-validate-after-applier-compile.md`](../../../docs/adr/0003-validate-after-applier-compile.md) | Post-compile validation |
| [`docs/adr/0004-series-indices-per-section-maps.md`](../../../docs/adr/0004-series-indices-per-section-maps.md) | Series/collective parse-time; positional/identity out of scope |
| [`docs/adr/0010-historical-fidelity-class-first-status.md`](../../../docs/adr/0010-historical-fidelity-class-first-status.md) | Fidelity / class-first ladder |
| [`.scratch/cleaned-rule-index/issues/26-parse-time-correspondence-series-indices.md`](../issues/26-parse-time-correspondence-series-indices.md) | Parse-time policy for series + collective |
| [`.scratch/cleaned-rule-index/research/positional-slots-and-identity-subscripts.md`](./positional-slots-and-identity-subscripts.md) | ASCA ref probes for slots/identity |
| [`.scratch/cleaned-rule-index/research/asca-rule-validity.md`](./asca-rule-validity.md) | ASCA validity / refs / IPACannotBeRefd |
| [`.scratch/cleaned-rule-index/research/asca-class-letter-mappings.md`](./asca-class-letter-mappings.md) | Class letter ↔ ASCA groupings |
| [`.scratch/cleaned-rule-index/series-mappings-coverage-backlog.md`](../series-mappings-coverage-backlog.md) | `Hₓ` out of series CSV |
| [`src/conlanger/tools/series_mappings.py`](../../../src/conlanger/tools/series_mappings.py) | Token classifiers + collective row synthesis |
| [`src/conlanger/tools/parsers.py`](../../../src/conlanger/tools/parsers.py) | `<sub>` → Unicode subscripts |
| [`data/diachronica/index_diachronica_original.html`](../../../data/diachronica/index_diachronica_original.html) | SoT examples (Key §5; rule lines cited above) |

### ASCA (primary)

| URL | Section |
|-----|---------|
| https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md | References; Alpha Notation; Groupings; Sets; Optionals |
| https://github.com/Girv98/asca-rust (tag/docs 0.10.2) | Crate / CLI 0.10.2 |

### Brassica (primary)

| URL | Section |
|-----|---------|
| https://github.com/bradrn/brassica/blob/master/docs/README.md | Doc index |
| https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md | Categories; Gemination; Backreferences; Phonetic features |
| https://github.com/bradrn/brassica/blob/master/docs/Reference.md | Sound change syntax; Category backreferences; Categories; Phonetic features |

### Probes

Local `asca 0.10.2` probes for collective set expansion and `sₓ` rejection were run under `.scratch/cleaned-rule-index/tmp-subscript-probes` and removed after this note. Brassica claims are from GitHub docs only (no local Brassica binary exercised).
