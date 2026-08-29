# Index syllable position `#U` / `U#` → ASCA

Research for handling Index Diachronica **syllable-position** tokens (`#U` = word-initial syllable, `U#` = word-final syllable) in **exception** and **environment** fields on **segment-level** rules.

Primary sources:

- Glossary: [`CONTEXT.md`](../../../CONTEXT.md) — boundary / syllable marks (`#`, `%`, class `U`)
- `group_mappings.csv`: [`data/asca/group_mappings.csv`](../../../data/asca/group_mappings.csv) — `U` → `%` row (syllable **class** only)
- Ticket: [58-spike-index-syllable-position-u-hash](../issues/58-spike-index-syllable-position-u-hash.md)
- ASCA **0.10.2**: [`doc/doc.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md) — [Special Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters), [Environment Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#environment-sets), [Syllable Structure Matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching), [Underline Structures](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#underline-structures)
- HTML SoT: [`data/diachronica/index_diachronica_original.html`](../../../data/diachronica/index_diachronica_original.html) — e.g. Old Norse line 6221, Proto-Norse 6179, Iroquoian 12384
- Parsed YAML: [`data/diachronica/index_diachronica_parsed.yml`](../../../data/diachronica/index_diachronica_parsed.yml)

Local ASCA probes run with `asca 0.10.2` on `PATH`. Probe files: [`.scratch/cleaned-rule-index/research/probes-58/`](./probes-58/).

---

## 1. Executive summary

**Recommendation: partial pass** — implement a **compile-time** rewrite in `SoundChangeRule` (ASCA emission) for **mechanical** `#U` / `U#` tails in `exception` and simple positive `env` fields. Use ASCA **underline structures** + **environment-set exceptions**; do **not** ship the failed `// #_%` / `U`→`%` boundary rewrite.

| Index pattern | ASCA target (validated) | Fidelity |
|---------------|-------------------------|----------|
| `! in #U` / `exception: #U` | `// :{#_#, #<.._>}:` | **High** (segment rules; incl. consonant-initial first syllable + monosyllables) |
| `! in U#` / `exception: U#` | `// :{#_#, <.._>#}:` | **High** |
| `! #U, U#` (Proto-Norse) | `// :{#_#, #<.._>, <.._>#}:` | **High** (incl. trisyllabic medial-only shortening) |
| `in #U` (positive env) | `/ #<.._>` | **High** |
| `in U#` (positive env) | `/ <.._>#` | **High** |
| Prose tails (`#U before a U with /iː/`, `between #U and U[+stress]`, …) | — | **Defer** (`status: skipped` or separate cluster tickets) |

**Why not `U`→`%` at `#U`:** Index `#U` means “segment inside the **word-initial syllable constituent**.” ASCA `%` is a **whole-syllable** token; `#_%` anchors the segment focus at the **word-onset / syllable junction**, not syllable membership ([failed candidates](#4-candidate-encodings-evaluated)). The `group_mappings.csv` `U`→`%` row applies to the **class letter** `U` in templates (`U → U[+stress] / #U_`), not to the boundary-adjacent position markers `#U` / `U#`.

**Inventory uplift (estimate):** ~**16** mechanical exception rules + ~**13** simple positive-env rules (`env: '#U'` or `env: U#`) ≈ **29** rules unblocked. Remaining ~**60+** occurrences of `#U` / `U#` are prose env, comments, or multi-condition tails — defer.

**Parse-only (safe now):** strip editorial `in` before `#U` / `U#` in `exception` (e.g. `in #U` → `#U`). Do **not** expand `#U`→`#%` at parse or compile.

---

## 2. Index semantics

From grill consensus (ticket 58) and HTML SoT:

| Token | Meaning |
|-------|---------|
| `#` | Word boundary (Index; maps to ASCA `#` in env) |
| `U` | Syllable **class** in rule templates; at boundaries, part of position marker |
| `#U` | Segment is in the word's **first syllable** (any onset/nucleus/coda position inside that syllable) |
| `U#` | Segment is in the word's **final syllable** |
| `in #U` / `in U#` | Editorial glue (“in the first/final syllable”); not ASCA syntax |
| `! in #U` | **Exception** — block the change when the target is in the first syllable |
| `! in U#` | **Exception** — block when target is in the final syllable |
| `! #U, U#` | **Exception** — block in first **or** final syllable (Proto-Norse long-vowel shortening) |

### Worked Index examples

| Rule (abbrev.) | HTML line | Intended behaviour |
|----------------|----------:|--------------------|
| `Vː → V[- long] / ! in #U` | 6221 | Shorten long vowels **except** anywhere in the first syllable (incl. `ska:.ta:`) |
| `Vː → V[- long] / ! #U, U#` | 6179 | Shorten only **medial** syllables in trisyllables; block mono- and disyllabic edge syllables |
| `Vː → V[-long] / ! in U#` | 12384 | Shorten long vowels except in the **final** syllable |
| `Vː → V[-long] / in #U` | 9415+ | Shorten **only** in the first syllable (positive env) |
| `V[+nas] → V[-nas] / in U#` | 7660 | De-nasalize except in final syllable → positive env: only final syllable |

Monosyllables are both `#U` and `U#`; exceptions for either edge must **also** block monosyllables.

---

## 3. ASCA semantics (cited)

From [ASCA 0.10.2 Special Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters):

- `%` — whole syllable
- `$` — syllable boundary
- `#` — word boundary (env only; peripheral)

From [Underline Structures](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#underline-structures):

- `_` may sit **inside** `⟨…⟩` / `<…>` structures to fix segment position **within a syllable** (onset `⟨_..⟩`, rhyme `⟨(..)_⟩`, etc.).
- `#<.._>` — word-initial syllable with focus anywhere in that syllable's rhyme/onset template.

From [Environment Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#environment-sets):

- Exception env-sets use `:{ … }:` so multiple blocking environments apply in **one pass** (OR semantics for “do not apply here”).
- **Member order matters empirically** — `{#_#, #<.._>}` blocks monosyllables; `{#<.._>, #_#}` does not (see probes).

**Root cause of `// #_%` failure:** `#_%` matches a segment immediately after `#` and before `$` — i.e. word-onset **segment** position, not “any segment in the first syllable.” A long vowel after a consonant cluster in `ska:.ta:` is not at `#_%`.

**Syllable-tier rules** (`%:[+long]`) are invalid — ASCA syllables only carry stress/tone features ([probe E](#4-candidate-encodings-evaluated)).

---

## 4. Candidate encodings evaluated

Probed with `V:[+long] > [-long]` unless noted. Test words: `ska:.ta:`, `a:`, `ta:.ska:`, `a:.ta:`, `a` (no length).

| # | Candidate | Intended | Result |
|---|-----------|----------|--------|
| A | `// #_%` | except first syllable | **Wrong** — shortens first-syllable `ska:` and monosyllable `a:` |
| B | `// #_` | except first syllable | **Partial** — blocks only word-initial **segment** (`a:.ta:` ok; `ska:.ta:` fails) |
| C | `// #%_`, `// #_$` | except first syllable | Same as A/B |
| D | `/ $ _` (env inversion) | only non-initial | **Wrong** — monosyllable shortens; needs explicit `$` |
| E | `%:[+long] > …` (syllable tier) | syllable membership | **Syntax error** — syllables cannot take length features |
| F | `// <_(..)>` | except syllable-initial | **Wrong** — blocks by onset position, not syllable |
| G | `// #<.._>` alone | except first syllable | **Partial** — polysyllabic ok; **monosyllable `a:` still shortens** |
| H | `// #_#` alone | except monosyllable | **Partial** — mono ok; polysyllabic first syllable not protected |
| I | `// :{#_#, #<.._>}:` | except first syllable + mono | **Pass** — see §5 |
| J | `// :{#_#, <.._>#}:` | except final + mono | **Pass** (Iroquoian) |
| K | `// :{#_#, #<.._>, <.._>#}:` | except first, final, mono | **Pass** (Proto-Norse) |
| L | `// :{#<.._>, <.._>#}:` (no `#_#`) | Proto-Norse disyllable | **Pass** disyllable; **mono fails** |
| M | Multi-rule feature marking (`[+sg]`, tone) | decomposition | **Fragile** — feature-only env needs `_`; tone alters surface |

**Do not ship** candidates A–H as a correction pass. **Ship** I–K (+ positive env `/ #<.._>`, `/ <.._>#`) for mechanical tails.

---

## 5. Recommended ASCA encodings

### 5.1 Compile-time mapping table

| Index surface (after `in` strip) | Field | ASCA emission |
|----------------------------------|-------|---------------|
| `#U` | `exception` | `// :{#_#, #<.._>}:` |
| `U#` | `exception` | `// :{#_#, <.._>#}:` |
| `#U, U#` | `exception` | `// :{#_#, #<.._>, <.._>#}:` |
| `#U` | `env` (positive) | `/ #<.._>` |
| `U#` | `env` (positive) | `/ <.._>#` |

**Preconditions:**

1. Run **after** `group_mappings` expansion so bare `U` class letters are not confused with `#U` / `U#` tokens (boundary-adjacent `U` must not be expanded).
2. Apply only when the exception/env value is **exactly** the mechanical pattern (possibly comma-separated `#U, U#`).
3. Preserve index YAML / `raw`; rewrite only ASCA compile output.

### 5.2 Test word table (recommended encoding I — Old Norse `! in #U`)

Rule: `V:[+long] > [-long] // :{#_#, #<.._>}:`

| Word | Index expected | ASCA actual | OK? |
|------|----------------|-------------|-----|
| `ska:.ta:` | no change in `ska:`; shorten `ta:` | `skaː.ta` | yes |
| `a:` | no change (first/only syllable) | `aː` | yes |
| `ta:.ska:` | shorten `ska:` only | `taː.ska` | yes |
| `a:.ta:` | no change in `a:`; shorten `ta:` | `a.ta` | yes |
| `a` | no change (no long feature) | `a` | yes |

### 5.3 Proto-Norse `! #U, U#` (trisyllabic)

Rule: `V:[+long] > [-long] // :{#_#, #<.._>, <.._>#}:`

| Word | Index expected | ASCA actual | OK? |
|------|----------------|-------------|-----|
| `ska:.ta:.mi:` | shorten **medial** `ta:` only | `skaː.ta.miː` | yes |
| `a:` | no change | `aː` | yes |
| `ska:.ta:` (disyllable) | no change (both edge syllables) | `skaː.taː` | yes |

### 5.4 Iroquoian `! in U#`

Rule: `V:[+long] > [-long] // :{#_#, <.._>#}:`

| Word | Index expected | ASCA actual | OK? |
|------|----------------|-------------|-----|
| `ska:.ta:` | shorten `ska:`; keep `ta:` | `ska.taː` | yes |
| `a:` | no change | `aː` | yes |
| `ta:.ska:` | shorten `ta:`; keep `ska:` | `ta.skaː` | yes |

---

## 6. Corpus inventory

Counts from `index_diachronica_parsed.yml` (2026-08-29, `rg`):

| Slice | Count | Notes |
|-------|------:|-------|
| `exception: 'in #U'` | 7 | Yupik consonant/gemination/deletion clusters |
| `exception: '#U'` | 6 | Old Norse, Proto-Norse, Tamil, … |
| `exception: U#` | 2 | Standard Malay parallel column; Iroquoian |
| `exception: '#U, U#'` | 1 | Proto-Norse |
| **Mechanical exceptions** | **16** | Eligible for §5 rewrite |
| `exception: '#U with the following U…'` | 4 | Middle English — **defer** |
| `env:` containing `#U` or `U#` | 29 | Includes prose |
| `env: '#U'` alone | 8 | Papuan `Vː → V[-long] / in #U` |
| `env: U#` alone | 5 | Positive final-syllable env |
| **Simple positive env** | **~13** | Eligible for §5 rewrite |
| `in #U` anywhere | 64 | Superset (raw, comments, prose) |
| `in U#` anywhere | 8 | |
| `#U` anywhere | 108 | |
| `U#` anywhere | 31 | |

**Defer clusters (examples):**

- `env: '#U before a U with /iː/'` — Kentish/ME (4 rules)
- `exception: '#U with the following U containing /iː/…'` — ME raising (4 rules)
- `env: '… between #U and U[+stress]'` — Portuguese apocope (3 rules)
- `env: 'O_ in #U'` — Blackfoot (segment-specific + prose)
- `comment: '(except in #U)'` — Yupik rules where exception stayed in comment (parse gap)
- `env: '_V(…V), after #U'` — Unaaliq Yupik (positional “after first syllable”, not exception)

---

## 7. Policy recommendation

| Tier | Action |
|------|--------|
| **Pass** | Compile-time `apply_syllable_position_exceptions()` (name TBD) for mechanical `#U` / `U#` in `exception` and simple `env`, using §5 table |
| **Parse-only** | Strip `in` before `#U` / `U#` in exception/env during ingest normalisation |
| **Do not** | Rewrite `#U` → `#%` or `// #_%`; do not run `U`→`%` on `#U` / `U#` boundary tokens |
| **Defer** | Prose env/exception tails; rules where `#U` is only in `comment`; complex “between #U and …” patterns → `status: skipped` per ADR-0010 until cluster tickets |
| **group_mappings.csv** | **Amend comment** on `U`→`%` row: clarify that `#U` / `U#` are syllable-**position** markers at word edges, not instances of class letter `U`; position markers compile via structure rewrite, not `%` substitution |

---

## 8. Follow-on ticket shape

**Ticket A — `correction-pass-syllable-position-u-hash`**

- Scope: `SoundChangeRule` compile pipeline, after group mappings, before validate
- Detect mechanical `exception` / `env` values per §6
- Emit ASCA per §5; unit tests from §5.2–5.4
- Parse-only: `in` strip in `split_env_exception` / normaliser (may overlap trailing-slash fix noted in ticket 58)
- Expected uplift: ~29 rules (`expected_ok`); re-run `create_index` inventory

**Ticket B — `correction-pass-prose-env-hashU` (defer)**

- Middle English `#U before a U with /iː/` env + matching exceptions
- Owner decision: skip vs multi-rule approximation

**Ticket C — `correction-pass-between-hashU-and-stress` (defer)**

- Portuguese `between #U and U[+stress]` — needs stress + syllable scaffolding

---

## 9. References

| Source | Location |
|--------|----------|
| Spike ticket | [58-spike-index-syllable-position-u-hash](../issues/58-spike-index-syllable-position-u-hash.md) |
| `group_mappings.csv` | [`data/asca/group_mappings.csv`](../../../data/asca/group_mappings.csv) |
| Compile pipeline | [`src/conlanger/tools/compile/asca/pipeline.py`](../../../src/conlanger/tools/compile/asca/pipeline.py) |
| Env/exception parse | [`src/conlanger/utils/parsing.py`](../../../src/conlanger/utils/parsing.py) — `split_env_exception()` |
| ASCA 0.10.2 docs | https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md |
| Empirical probes | [`.scratch/cleaned-rule-index/research/probes-58/`](./probes-58/) |
