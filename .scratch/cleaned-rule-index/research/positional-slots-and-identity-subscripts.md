# Positional slots and identity subscripts → ASCA

Research for handling Index Diachronica **positional slots** (`C₁`, `V₂`) and **identity subscripts** (`V₀`) in the cleaned rule index pipeline.

Primary sources:

- Glossary: [`CONTEXT.md`](../../../CONTEXT.md) — **Subscript notation**, **Positional slot**, **Identity subscript**
- ADR: [`docs/adr/0004-series-indices-per-section-maps.md`](../../../docs/adr/0004-series-indices-per-section-maps.md) — correspondence-series only; positional/identity explicitly separate
- Ticket: [26-parse-time-correspondence-series-indices](../issues/26-parse-time-correspondence-series-indices.md)
- ASCA **0.10.2**: [`doc/doc.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md) — [References](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#references), [Alpha notation](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#alpha-notation)
- Prior art: [`asca-rule-validity.md`](./asca-rule-validity.md), [`series_mappings.py`](../../../src/conlanger/tools/series_mappings.py)
- HTML SoT: [`data/diachronica/index_diachronica_original.html`](../../../data/diachronica/index_diachronica_original.html)
- Inventory: [`.scratch/cleaned-rule-index/inventory/asca-rule-inventory.csv`](../inventory/asca-rule-inventory.csv) (ASCA 0.10.2, 2026-08-06)

Local ASCA probes run with `asca 0.10.2` on `PATH`.

---

## 1. Executive summary

**Recommendation:** implement a **compile-time** transform in `SoundChangeRule` (ASCA emission layer) that maps Index subscript notation to ASCA **reference syntax** (`X=n` … bare `n`), leaving index YAML fields and `raw` Index-shaped.

| Index use | Index example | ASCA target (validated locally) |
|-----------|---------------|----------------------------------|
| Positional slot | `C₁C₂ → C₂` | `C=1 C=2 > 2` |
| Identity subscript | `V₀V₀ → V₀` | `V=0 V=0 > 0` |
| Identity + length | `V₀V₀ → V₀ː` | `V=0 V=0 > 0:[+long]` |
| Identity + features | `V₀[+nas]V₀[-nas] → V₀[+nas]` | `V:[+nas]=0 V:[-nas]=0 > 0:[+nas]` |
| Env co-reference | `h → ʔ / V₀V₀` | `h > ʔ / _ V=0 V=0` (env needs `_` focus) |

**Why compile-time, not parse-time (unlike correspondence-series):**

- Correspondence-series expansion (ticket 27) produces **IPA segments** — still phonological content. Reference syntax is **ASCA-specific** surface form ([ADR-0004](../../../docs/adr/0004-series-indices-per-section-maps.md) defers positional/identity to “ASCA reference/alpha syntax”).
- Keeps the index **applier-neutral** in the sense that `C₁` remains visible in YAML for audit; only the ASCA compiler emits `C=1` / `2`.
- Mirrors **`group_mappings.csv`** (class letters expanded at compile, not ingest).

**Why not `status: skipped`:** all **75** HTML rules that use positional or identity subscripts currently fail validation (`unknown_character` 72, `unknown_feature` 3). A faithful reference mapping should clear most of them without owner skip approval (ADR-0010 class-first safe transform).

**Alpha notation** is **not** the right tool for slots — alphas express feature polarity agreement across segments, not numbered template positions ([ASCA doc — Alpha notation](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#alpha-notation)).

**Residual hard cases** (need separate cluster tickets or skip): compounds (`mV₀nV₀`), inter-slot diacritics (`C₁ˤC₂`), mixed meta-notation (superscript tone on `V₀`), prose env tails, and `S₁` on uppercase class letters (Athabaskan — may be section-local abbreviation, not positional).

---

## 2. Index semantics

From [`CONTEXT.md`](../../../CONTEXT.md):

### Positional slot

Ordinal subscript on a **class letter** — numbered positions in a rule template; tokens sharing the same base+subscript co-refer within the rule.

- Index key: `Xₙ` on class letters (e.g. `C₁C₂ → C₂`, `N₁N₂ → N₂ː`)
- **Not** correspondence-series (`s₁` on lowercase segments)
- **Not** expandable via `group_mappings.csv` or `series_mappings.csv`

Detection in code: `is_positional_slot_token()` — regex `^[A-Z][₁₂₃₄₅₆₇₈₉]$` ([`series_mappings.py`](../../../src/conlanger/tools/series_mappings.py)).

### Identity subscript

Subscript `₀` on any base — “the same instance as other tokens bearing the same base+₀ in this rule.”

- Index key: `X₀` (e.g. `V₀V₀ → V₀`, `h → ʔ / V₀V₀`)
- Co-reference, not series selection
- Compounds like `mV₀`, `CʔV₀` attach a segment literal to a vowel slot

Detection: `is_identity_subscript_token()` — regex `^[A-Za-z]₀$` (includes `V₀`, `C₀`; also matches inside compounds when tokenized as whole `mV₀` — see §6).

### HTML examples (with line numbers)

| Line | Rule (abbrev.) | Use |
|-----:|----------------|-----|
| 2793 | `C₁C₂ → C₂` | Positional (Austronesian) |
| 2816 | `V₀V₀ → V₀` | Identity |
| 2896 | `h → ʔ / V₀V₀` | Identity in env |
| 1478 | `C₁ˤC₂ → C₁C₂ˤ` | Positional + segment diacritic |
| 7661 | `V₀[+nas]V₀[-nas] → V₀[+nas]` | Identity + feature matrices |
| 12552 | `CʔV₀ → CV₀ʔV₀` | Consonant cluster + identity vowel |
| 12764 | `mn → mV₀nV₀ / #_` | Segment + identity slot compounds |
| 7317 | `C₁C₂C₃C₄ → (C₃)C₄` | Four positional slots + optional |

---

## 3. ASCA representation options

### 3.1 References (recommended)

[ASCA References](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#references):

> References are declared by using the `=` operator, followed by a number. This number can then be used later in the rule to invoke the reference.  
> Currently; matrices, groups, and syllables can be referenced.

**Mapping convention (proposed):**

| Index token | Role | ASCA form |
|-------------|------|-----------|
| `Xₙ` (class letter + subscript 1–9) | First occurrence in a field | `X=n` (ascii digit) |
| `Xₙ` | Later occurrence (output/env) | bare `n` |
| `X₀` | Any occurrence | `X=0` on first binding in field order, bare `0` thereafter |
| `X₀[±feat…]` | Matrix on identity slot | `X:[±feat…]=0` (declaration), `0:[±feat…]` (invoke) |

**Validated locally (parse OK, `asca trace kata` exit 0 unless noted):**

```
C=1 C=2 > 2                    ← C₁C₂ → C₂
V=0 V=0 > 0                    ← V₀V₀ → V₀
V=0 V=0 > 0:[+long]            ← V₀V₀ → V₀ː
N=1 N=2 > 2:[+long]             ← N₁N₂ → N₂ː
V:[+nas]=0 V:[-nas]=0 > 0:[+nas] ← Portuguese V₀[+nas]V₀[-nas] → V₀[+nas]
h > ʔ / _ V=0 V=0               ← h → ʔ / V₀V₀ (env requires `_`)
```

**Fails (Unicode subscripts not accepted):**

```
C₁ C₂ > C₂     → Syntax Error: Unknown character '₁'
V₀ V₀ > V₀     → Syntax Error: Unknown character '₀'
```

**Fails (wrong reference shape):**

```
V=0:[+nas] …   → ':' not allowed on `V=0` declaration
N=1 N=2 > N=2:[+long]  → output must use bare ref `2:[+long]`, not `N=2:[+long]`
0:[+nas] 0:[-nas] > 0:[+nas]  → Runtime Error: Unknown reference '0' (must declare with `V:[+nas]=0` first)
```

Reference numbers **need not start at 1** — `0` is valid for identity (`V=0`).

### 3.2 Alpha notation — not applicable

Alphas (`A`…`Z`, `α`…) copy feature bundles between segments for assimilation/dissimilation rules. They do not encode “first consonant / second consonant” template positions. Do not use for `C₁`/`C₂`.

### 3.3 Strip subscripts — rejected

Stripping `₁`/`₀` to yield `C`, `V` changes phonological meaning and violates ADR-0010 / ADR-0004 (no silent deletion of subscripts).

### 3.4 Section CSV maps — not applicable

Correspondence-series maps (`series_mappings.csv`) key on **lowercase segment + subscript** (e.g. `s₁ → f1`). Positional slots use **uppercase class letters**; identity uses `₀`. Different mechanism.

---

## 4. Corpus policy options

| Policy | Corpus YAML | `raw` | Pros | Cons |
|--------|-------------|-------|------|------|
| **Compile-time ref expansion** (recommended) | Keeps `C₁`, `V₀` | Unchanged | Applier-neutral YAML; ASCA-only syntax at compile; matches class-letter policy | Brassica path needs its own ref syntax later |
| Parse-time expansion | `C=1`, `0` in fields | Unchanged | Single shape for all appliers if they share refs | Bakes ASCA syntax into index; breaks applier-neutral goal |
| `status: skipped` | `""` / `""` | Unchanged | Safe for unrepresentable edge cases | Loses 75 rules from compile surface; owner approval for permanent skip |

**Edit ladder** ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)): reference mapping is a **class-first mechanical transform** (like `→` → `>`), not a meaning-changing rewrite. Apply without per-rule owner approval. Use `status: skipped` only for rules that remain unrepresentable after the transform (prose env, meta-notation).

**Relation to ticket 27:** correspondence-series expansion stays **parse-time**; positional/identity stays **compile-time**. No overlap — `classify_subscript_token()` already separates them.

---

## 5. Inventory impact

Survey (`extract_text_with_subs` + `find_subscript_tokens` + `classify_subscript_token` on full HTML):

| Class | Token occurrences in rules | Unique token shapes |
|-------|---------------------------:|--------------------:|
| Positional | 63 | 16 (`C₁`, `C₂`, `V₁`, `V₂`, `N₁`, `N₂`, `S₁`, …) |
| Identity | 30 | 2 (`V₀`, `C₀`) |
| Correspondence | 95 | (ticket 27 — separate) |
| Collective | 6 | (ticket 27 — separate) |

**Rules touching positional or identity:** **75** HTML rule lines.

**Current validation (all 75 fail):**

| failure_class | count |
|---------------|------:|
| `unknown_character` | 72 |
| `unknown_feature` | 3 |

Inventory `error_token` counts for subscript digits (overlapping correspondence + positional): `₀` 49, `₁` 37, `₂` 4. Positional/identity work should eliminate most `₀` failures and a subset of `₁` (positional `C₁` vs correspondence `s₁`).

**Expected uplift if reference mapping lands:** up to **~75** rules move from fail → ok (0.8% of 9317 index rules), plus downstream env-focus fixes for rules like `h → ʔ / V₀V₀`.

Baseline before this work: **6518 / 9317 ok (70.0%)** ([inventory summary](../inventory/asca-rule-inventory-summary.md)).

---

## 6. Implementation sketch

### 6.1 Where

**`SoundChangeRule`** in [`src/conlanger/tools/rules.py`](../../../src/conlanger/tools/rules.py) — new function e.g. `expand_index_subscript_references(text: str) -> str`, called when rendering ASCA strings (after or before `group_mappings`, order TBD: likely **after** group expansion so `C` is still a grouping letter).

**Not** in `IndexDiachronicaParser` — index fields and `raw` stay Index-shaped.

**Not** in `series_mappings.csv` — no per-section table; mapping is purely positional/identity grammar.

### 6.2 Token patterns

Reuse [`series_mappings.py`](../../../src/conlanger/tools/series_mappings.py) classifiers:

- `is_positional_slot_token(token)` → `C₁` … `C=1` / `2`
- `is_identity_subscript_token(token)` → `V₀` → `V=0` / `0`

**Per-field algorithm (input, output, env, exception):**

1. Tokenize field (respect `{…}`, `[…]`, `⟨…⟩`, boundaries — reuse or share `_RULE_TOKEN_RE` from series_mappings).
2. Walk left-to-right; maintain `declared_refs: set[int]` for numbers already bound in this field.
3. For each token:
   - If positional `Xₙ`: if first binding of digit `n` in field, emit `X=n`; else emit `n`.
   - If identity `X₀`: if `0` not declared, emit `X=0`; else emit `0`.
   - If compound `mV₀`: split into literal `m` + identity `V=0` / `0` (needs compound regex — see open questions).
   - If matrix-attached `V₀[+nas]`: emit `V:[+nas]=0` / `0:[+nas]` per ASCA ref+matrix rules.

**Cross-field references:** ASCA binds refs within a rule part (input, env, output) in processing order ([doc — alphas/refs processed input → context → output](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#alpha-notation)). Implementation must declare refs in **input before invoking in output/env**, and may need a **whole-rule pass** (declare all input slots first, then rewrite output/env invocations). Spike with multi-field rules before coding.

### 6.3 Edge cases (defer or special-case)

| Pattern | Example line | Issue |
|---------|-------------|--------|
| Inter-slot diacritic | 1478 `C₁ˤC₂` | Diacritic between refs |
| Optional / meta | 7317 `(C₃)C₄` | Structures + slots |
| Prose env | 5485 `… / if C₂ was a plosive` | Not ASCA-representable → skip or `comment` |
| Superscript + subscript | 11420 `V₀³` | Meta-notation ticket |
| Uppercase `S₁` | §10 Austronesian | May be section-local series, not `is_positional_slot_token` |
| `V₀ = U` exception | 13878 Finnish | Prose exception — already in `comment`? |
| Identity `C₀` | rare | Same `=0` / `0` machinery as `V₀` |

### 6.4 Tests

- Unit tests in `test_SoundChangeRule.py` — parametrized Index → ASCA string pairs from §3.1.
- E2E: extend `test_index_pipeline.py` smoke — `C₁C₂ → C₂` with `expect_ok=True` after implementation.
- Regression: re-run `uv run create_index`; expect ~75-rule uplift.

---

## 7. Open questions (owner / grilling)

1. **Whole-rule ref numbering:** When `C₂` appears only in output, must input declare `C=2` first even if `C₂` absent from input? (ASCA likely requires declaration in input or env before output invoke — confirm with apply tests.)
2. **Compound tokenization:** Is `mV₀` one token or `m` + `V₀`? Index intent is segment + identity vowel slot — propose split on `(?<=[a-z])V₀` and similar.
3. **`C₀` identity:** Only 2 unique identity shapes (`V₀`, `C₀`); treat `C₀` identically to `V₀` with base `C`?
4. **Uppercase `S₁`, `B₁`:** Classify as positional or Athabaskan section-local? [`series-mappings-coverage-backlog.md`](../series-mappings-coverage-backlog.md) flags Greek `Hₓ` as out of scope — same for uppercase series?
5. **Brassica path:** Does Brassica have reference syntax? If unknown, compile-time ASCA-only transform is still correct per ADR-0001.
6. **Order vs group_mappings:** Expand `C₁` before or after `S → P`? Recommendation: **before** group mapping so `C=1` is not corrupted.

---

## 8. References

| Source | Location |
|--------|----------|
| Glossary (positional, identity, subscript notation) | [`CONTEXT.md`](../../../CONTEXT.md) |
| ADR-0004 (correspondence vs positional) | [`docs/adr/0004-series-indices-per-section-maps.md`](../../../docs/adr/0004-series-indices-per-section-maps.md) |
| ADR-0010 (edit ladder) | [`docs/adr/0010-historical-fidelity-class-first-status.md`](../../../docs/adr/0010-historical-fidelity-class-first-status.md) |
| Ticket 26 (parse-time policy) | [`.scratch/cleaned-rule-index/issues/26-parse-time-correspondence-series-indices.md`](../issues/26-parse-time-correspondence-series-indices.md) |
| Token classification | [`src/conlanger/tools/series_mappings.py`](../../../src/conlanger/tools/series_mappings.py) |
| ASCA validity / refs summary | [`.scratch/cleaned-rule-index/research/asca-rule-validity.md`](./asca-rule-validity.md) |
| ASCA 0.10.2 docs | https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md |
| Index HTML SoT | [`data/diachronica/index_diachronica_original.html`](../../../data/diachronica/index_diachronica_original.html) |
| Validation inventory | [`.scratch/cleaned-rule-index/inventory/asca-rule-inventory.csv`](../inventory/asca-rule-inventory.csv) |
