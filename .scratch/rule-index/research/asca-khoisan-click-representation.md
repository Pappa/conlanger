# ASCA representation of Khoisan / Index click segments

Spike for [138-spike-asca-khoisan-click-representation](../issues/138-spike-asca-khoisan-click-representation.md).  
Primary sources: [ASCA 0.10.2 `doc/doc.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md) (IPA, aliases, feature shorthands), local **`asca 0.10.3`** fork (`lib/bin/asca`, tag `v0.10.3-dev-validate` per [DEV.md](../../../docs/DEV.md)), cluster [invalid_ipa_errors.csv](../inventory/error_clusters/invalid_ipa_errors.csv) (**47** rules; **46** in §20.x, **1** in §17.7.2.1.4).

## Summary

Index Diachronica uses **bare** Khoisan click letters (`!` → `ǃ`, plus `ǀ`, `ǁ`, `ǂ`, sometimes `ʘ` and `!!`) as **single segments**. ASCA accepts clicks only as **clusters** with an explicit velar/uvular (or nasal) onset (`kǃ`, `gǀ`, `ŋʘ`, …) or as the feature **`[+click]`** (optionally hosted, e.g. `C:[+click]`). Bare click codepoints are **not** in the PHOIBLE segment inventory, so validation fails with `Could not get value of IPA 'ǃ'` (and the same for `ǀ`, `ǁ`, `ǂ`, `ʘ`).

**Recommendation for ticket 136:** add a **compile-time** normaliser (same seam as ejectives / length) that rewrites Index bare clicks into ASCA clusters (default `k` onset, special-case `!!`, `ˀ` → `:[+cg]` on clusters), then a **small manual overlay** for the §17 outlier and any rows that still fail field validation (optional `(n)`, idiosyncratic accompaniment). Do **not** rely on parse-time `ipa_mappings.yml` alone.

---

## ASCA model (primary sources)

### Documented segment shape

From [IPA Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#ipa-characters):

> Clicks are preceded by a velar or uvular plosive/nasal, denoting place of rear articulation, voicing, and nasality. These do not need to be, but can be, joined by a tie as it is implicit (i.e. `ŋʘ` over `ŋ^ʘ`, and **never `ʘ`**).

So ASCA treats the **accompaniment + release** as the segment; Index’s bare letter is only the release articulation.

### Alias `!` → `ǃ`

[Inbuilt aliases](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#inbuilt-aliases): `! => ǃ`. The lexer still requires a valid **segment**; alias does not make bare `ǃ` legal.

### Feature `[+click]`

[Feature shorthands — Click](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands): `click` / `clik` / `clk` / `clck` on the **manner** node ([feature table](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#feature-shorthands) row “click consonants”). Matches any click regardless of type; combine with place features when needed (e.g. `C:[+click,+lateral]` validates).

### Index class letter `Q` vs ASCA grouping `Q`

ASCA’s inbuilt **`Q`** grouping is **uvular consonants** only ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings) — `[+cons, -fr, +bk, -hi, -lo]`); `Q > k` validates as uvular, not click.

Conlanger [`group_mappings.yml`](../../../config/compile/asca/group_mappings.yml) maps Index **`Q`** (uvular **or** click in the Index key) to `{C:[-front,+back,-hi,-lo],[+click]}`. That is unrelated to Unicode click **glyphs** in §20.x rules.

### Inventory segments (fork source)

In `Pappa/asca-rust` (`v0.10.3-dev-validate`), clicks live in `cardinals.json` / `setup/features.tsv`: **no** bare `ǃ`/`ǀ`/`ǁ`/`ǂ`/`ʘ`; segments are **rear + click** (`kǃ`, `ɡǂ`, `ɴǃ`, `qǃ`, …) and **contour** orders (`ǃq`, …). Grammar: `doc/grammars/rule_peg.md` (`ClickChar` includes `ʘ` `ǀ` `ǃ` `ǁ` `‼` `ǂ`). Parser rejects unknown segments via `CARDINALS_MAP` (`UnknownIPA`).

**`‼` (U+203C)** is the IPA **lateral alveolar** click letter in ASCA’s inventory — distinct from **`ǁ`** (lateral click) and from Index ASCII **`!!`** (usually two alveolar clicks, not one `‼` glyph).

### Fork 0.10.3

Probes below use **`asca 0.10.3`** with `validate`. Fork delta vs crates.io 0.10.2 is mainly **`validate`** and encoding fixes for `q`+click clusters (`CHANGELOG.md`); click **model** matches 0.10.2 `doc/doc.md`.

---

## Probe matrix (`asca validate -s …`)

Environment: `lib/bin/asca` (0.10.3). ✓ = exit 0; ✗ = syntax/IPA error (representative message).

| Input pattern | Result | Notes |
|---------------|--------|--------|
| `ǃ`, `ǀ`, `ǁ`, `ǂ` as I/O segment | ✗ | `Could not get value of IPA '…'` |
| `!` as I/O segment | ✗ | Normalised to `ǃ`, same error |
| `ʘ` as I/O segment | ✗ | `Could not get value of IPA 'ʘ'` |
| `!x`, `ǀx` (no onset) | ✗ | |
| `k!`, `kǃ`, `kǀ`, `kǁ`, `kǂ`, `gǃ`, `ŋǀ`, `kʘ`, `ŋʘ` | ✓ | Default cluster form |
| `k!x` | ✓ | Index-style click + fricative release |
| `[+click]`, `C:[+click]`, `C:[+click,+nasal]` | ✓ | Field fragments `-f input` |
| `[+click] > k`, `C:[+click] > C:[+click]` | ✓ | Whole rule |
| `kǃ̬ > ɡ`, `k!̬ > ɡ` | ✓ | Voicing diacritic on cluster |
| `kǃ:[+cg] > k`, `kǀ:[+cg] > k` | ✓ | Glottalised / ejective-style click |
| `kǃʼ > k` | ✓ | Ejective/glottal via `ʼ` on cluster (prefer over `ˀ`) |
| `kǃˀ`, `k!ˀ`, `kǀˀ` | ✗ | `ˀ` diacritic: “Must be [+sonorant]” |
| `ŋǃˀ > ŋ` | ✓ | Nasal onset exception |
| `ɡǃ`, `qǃ`, `q‼`, `k‼` | ✓ | Non-default rear; lateral alveolar `‼` |
| `k > ǁ`, `k > ǂ` | ✗ | Bare click in output |
| `k > kǁ`, `k > kǂ`, `k > kǂ̃n` | ✓ | Output must use cluster |
| `!! > ǁ`, `k!! > kǁ` | ✗ | `!!` is two `!` tokens; second bare `ǃ` fails |
| `kǃ kǃ > kǁ` | ✓ | Model for Index `!! > ǁ` |
| `kǃ kʘ > kǁ kǀ` | ✓ | Model for `!! ʘ > ǁ ǀ` after token rewrite |
| `kǂ > kǃ kǃ`, `kǂ > k‼ kǃ` | ✓ | Models for `ǂ > !!` — pick per rule (double alveolar vs `‼` + alveolar) |
| `ɡǂ > k` | ✓ | Nama-style `ǂɡ` → voiced rear `ɡǂ` when rule demands it |
| `{kǀ̃,kǀ̃n} > kǂ̃n` | ✓ | Set members with `k` onset |
| `{kǀˀ,kǀx:[+cg]} > kǀ` | ✗ | `kǀˀ` still invalid; use `kǀ:[+cg]` |
| `k! k!:[+cg] k! k!̃ > k ɡ ŋɡ` | ✓ | Multi-segment Nama-style row (transformed) |
| `ʊ > ɤ k! C:[+labial]_ and _l` | ✗ | Env parse: `!` in wrong field (§17 — not Khoisan) |
| `ʊ > ɤ / _C:[+labial] // _l`, `… \| _l` | ✓ | Manual ASCA env/exception for §17 (`!` was not a click) |
| `ɴǃ > ǃɴ` | ✓* | *Whole rule passes; `kǃ > ǃ` alone ✗ — do not emit bare click outputs |

---

## Inventory cluster classification

Token counts from validation messages (inventory summary): **`ǃ` 25**, **`ǀ` 11**, **`ǁ` 6**, **`ǂ` 5** (ASCII `!` in rules aliases to `ǃ`).

| Index surface | ASCA target (faithful default) | Class | Notes |
|---------------|-------------------------------|-------|--------|
| `!`, `ǃ` | `kǃ` / `k!` | **mappable** (compile) | Default voiceless velar onset per doc |
| `ǀ`, `ǁ`, `ǂ` | `kǀ`, `kǁ`, `kǂ` | **mappable** (compile) | Preserves click **type** |
| `ʘ` | `kʘ` (or `ŋʘ` if accompaniment known) | **mappable** (compile) | Never bare `ʘ` |
| `!!` | `kǃ kǃ`, or `k‼` / `kǁ` per rule | **mappable** (compile) | Not `k!!`; do not equate Index `!!` with IPA `‼` without context |
| `!ˀ`, `ǀˀ`, `ǁˀ`, `ǂˀ` | `k{click}:[+cg]` or `k{click}ʼ` | **mappable** (compile) | `ˀ` diacritic invalid on cluster; `ʼ` validates |
| `ǂɡ` (segment) | `ɡǂ` | **manual / rule-specific** | Voiced rear on palatal click |
| `!x`, `ǁxʼ`, etc. | `k!x`, `kǁx:[+cg]` | **mappable** (compile) | `x`/`ʼ` patterns already mixed in inventory |
| `!̬`, `!̃`, complex sets | `kǃ̬`, `kǃ̃`, … | **mostly mappable** | Voicing/nasal diacritics on cluster validate |
| `!̃(n)`, optional groups | — | **manual-only** | `Options can only be used in Environments` on I/O |
| `Q` (class letter) | `{C:[…],[+click]}` | **already** | `group_mappings.yml`; not §20 glyph issue |
| §17.7.2.1.4 `!` in `ʊ > ɤ ! C:…` | `ʊ > ɤ / _C:[+labial] // _l` (or `\| _l`) | **manual-only** | English; `!` is exception prose, not a click |
| Rules requiring `g`/`ŋ` onset | `gǃ`, `ŋǀ`, … | **manual-only** when semantics demand | Default `k` is lossy for accompaniment contrasts |

---

## Fidelity

| Preserved with `k` + type letter | Collapsed or lost |
|----------------------------------|---------------------|
| Click **place/type** (`ǃ` vs `ǀ` vs `ǁ` vs `ǂ`) | Rear onset **manner/place** (Index often omits `k` vs `g` vs `ŋ`) |
| Sequences of clicks (`! !ˀ !̬`) as separate segments | `!!` as single glyph → must become **two** alveolar clusters |
| Ejective/glottal series via `:[+cg]` | `ˀ` as segment diacritic on `kǃ` (invalid); must use features |
| Broad “any click” intent | `[+click]` or Index `Q` expansion |

Rules that change accompaniment (e.g. `! !ˀ !̬ !̃ > k ɡ ŋɡ`) need the normaliser to **only** supply default onset on **each** bare click token, not flatten to a single `[+click]` unless the rule is genuinely class-level.

---

## Pipeline fit

| Stage | Verdict |
|-------|---------|
| **Parse-time** `ipa_mappings.yml` | **Insufficient** — single-char map to `kǃ` does not handle `!!`, sets, `ˀ`, `!x`, or output-side glyphs; breaks if applied to non-click `!` |
| **Compile-time** normalisation | **Primary** — mirror `normalize_asca_ejective_marks()` in [`pipeline.py`](../../../src/conlanger/tools/compile/asca/pipeline.py) (`compile_asca_field_post_subscript`): token-aware `k` onset, `!!` → `ǃ ǃ`, `ˀ` on clicks → `:[+cg]`, apply to input/output (and env/exception only when whole-field segmentiser agrees) |
| **Manual** `manual_mappings.yml` / `index_diachronica_corrections.yml` | **Secondary** — §17 row, optional `(n)` on clicks, rows where default `k` onset is wrong |
| **`skip_sections` / `skip_rules`** | **Last resort** — not recommended for bulk §20.x; spike 64 deferral superseded for `invalid_ipa` by this policy |

Ordered combination for **136**: **compile normaliser → per-rule manual residuals → skip only ADR-0010 hold-outs**.

---

## Recommendation (ticket 136)

1. Implement **`normalize_asca_index_click_segments()`** (name TBD) in the ASCA compile pipeline on **input and output** strings (and env/exception with the same segment rules used for ejectives).
2. **Transforms (minimal spec):**
   - Bare click glyph (`!`, `ǃ`, `ǀ`, `ǁ`, `ǂ`, `ʘ`) → prefix `k` when not already preceded by `k`/`g`/`ŋ`/`ɡ`.
   - Token `!!` → two segments `kǃ kǃ` (space-separated).
   - Click + `ˀ` where `k{click}ˀ` is invalid → `k{click}:[+cg]` or `k{click}ʼ` (both validate).
   - Rule-specific `!!` / `ǂ > !!` → choose among attested outputs (`kǃ kǃ > kǁ`, `kǂ > k‼ kǃ`, …) after default `k` expansion.
   - Outputs: always **cluster** form (`> kǂ`, never `> ǂ`).
   - Leave existing `…x:[+cg]` and feature matrices unchanged.
3. Add **manual mappings** for `Early-Modern-English-ʊ` (env `!` → `/ _C:[+labial] // _l` or equivalent) and any rules still failing `asca validate` after the pass (optional I/O parens, `ɡ`/`q`/`ŋ` rear, `ǂɡ`-style segments).
4. Re-run inventory; record `invalid_ipa` delta in **136 Answer**.

**Not in scope for 136:** extending the ASCA fork IPA table to accept bare `ǃ` (would contradict documented model).

---

## References

- [ipa-correction-prioritization.md](./ipa-correction-prioritization.md) — prior deferral of §20.x clicks
- [asca-ejective-notation.md](./asca-ejective-notation.md) — compile-time precedent (`:[+cg]`)
- [asca-class-letter-mappings.md](./asca-class-letter-mappings.md) — Index `Q` vs ASCA `[+click]`
- [136 correction pass](../issues/136-correction-pass-khoisan-click-invalid-ipa.md) — implementation ticket
