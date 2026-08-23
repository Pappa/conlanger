# unknown_character → IPA mapping candidates

Spike for [42-spike-unknown-character-ipa-mappings](../issues/42-spike-unknown-character-ipa-mappings.md).

**Source:** `.scratch/cleaned-rule-index/inventory/asca-rule-inventory-error.csv` (ASCA 0.10.2 baseline: **613** `unknown_character` rows).

**Method**

1. Collect distinct `error_token` values where `failure_class == unknown_character`.
2. **Exclude punctuation** — Unicode categories `P*`, env syntax (`_`, `#`, `+`), and bare combining marks (`́`, `̣`, …).
3. **Exclude non-segment letters** — length modifiers (`ː`, `ˑ`; tickets 15/25) and subscript correspondence glyphs (`ₓ`, `ₙ`, `ₛ`, `ᵤ`, `ᵚ`).
4. For each remaining letter token, propose an `ipa_target` that **ASCA 0.10.2 accepts** in a single-segment smoke rule (`segment > ∅`), with confidence `high` | `medium` | `low` | `defer`.

**Deliverable CSV:** [unknown-character-ipa-mappings.csv](./unknown-character-ipa-mappings.csv) — paste-ready review set; **not** auto-seeded into `data/common/ipa_mappings.csv`.

---

## Summary

| Bucket | distinct tokens | inventory rows (approx.) |
|--------|----------------:|-------------------------:|
| Letter-like (in CSV) | 42 | ~470 |
| Excluded length marks | 2 | 52 |
| Excluded subscript notation | 5 | 30 |
| Excluded punctuation / combining | 27 | ~61 |

**High-confidence wins (seed first):** PIE/Leiden `ḱ`/`ǵ`, Americanist `š`/`ś`/`Ṣ`/`Ṭ`, Melanesian `Ṽ`, precomposed nasal vowels → decomposed tilde (`ã`→`ã`), French phoneme letters `è`/`é`, Slavic yer `ь`/`ъ`, Polish `ȵ`.

**Defer:** `Ω` (author ad-hoc Vietnamese placeholder; no stable IPA target).

---

## Excluded tokens (not in letter CSV)

### Length marks (compile passes 15/25)

| token | count | notes |
|------:|------:|-------|
| `ː` | 49 | triangular colon; `normalize_asca_length_marks` |
| `ˑ` | 3 | half-length |

### Subscript correspondence / notation (parse/compile subscript tickets)

| token | count | notes |
|------:|------:|-------|
| `ₓ` | 11 | collective subscript placeholder |
| `ₙ` | 5 | |
| `ₛ` | 2 | |
| `ᵤ` | 1 | |
| `ᵚ` | 2 | |

### Punctuation, combining marks, syntax (other clusters)

`"`, `"`, `'`, `(`, `#`, `_`, `+`, `〈`, `˟`, `͜`, `͡`, and bare combining diacritics (`́`, `̣`, `̊`, `̆`, `̺`, `̀`, `̂`, `̌`, `̚`, `̲`, `̻`, `̼`, `̈`) — env prose, matrix adjacency, or diacritic-prerequisite failures; not segment letter mappings.

---

## Confidence rubric

| Level | Meaning |
|-------|---------|
| **high** | Stable convention in Index / Americanist / Leiden literature; ASCA accepts target; rule context consistent |
| **medium** | Likely correct in dominant inventory contexts but section-variant readings exist |
| **low** | Plausible target; needs cluster review before seeding |
| **defer** | Not a phonological segment mapping (author notation, prose, or unrepresentable without rule rewrite) |

---

## ASCA acceptance notes (0.10.2 smoke)

- Precomposed nasal vowels (`ã`, `ẽ`, `õ`, `ũ`) → **reject**; decomposed (`ã`, `ẽ`, `õ`, `ũ`) → **accept**.
- `ṽ` accepts; capital `Ṽ` rejects → map to lowercase `ṽ`.
- `ł`, `ʝ`, `ð`, `ŋ`, `ɛ` already accepted when used as segments (some inventory hits are **prose** in env, not segment tokens).
- `ɚ` rejects; nearest accepted rhotic vowel targets: `ɜ`, `ə`, `ɻ` (context-dependent).

---

## References

- Index inventory: [asca-rule-inventory-summary.md](../inventory/asca-rule-inventory-summary.md)
- Existing ingest: `data/common/ipa_mappings.csv`, `apply_ipa_mappings()`
- PIE palatovelars: Index reconstruction tables (`ḱ`, `ǵ`) → IPA `kʲ`, `ɡʲ`
- ASCA validity: [asca-rule-validity.md](./asca-rule-validity.md)
