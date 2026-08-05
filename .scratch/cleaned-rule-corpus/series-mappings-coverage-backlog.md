# Series mappings — coverage backlog

Follow-up work to raise **in-scope** extraction coverage beyond the ticket-28 baseline.  
Regenerate metrics after any change: `uv run extract_series_mappings`.

**Related:** [28-extract-correspondence-series-mappings-from-html](issues/28-extract-correspondence-series-mappings-from-html.md) (done), [27-implement-parse-time-correspondence-series-expansion](issues/27-implement-parse-time-correspondence-series-expansion.md) (blocked on parse-time wiring), live report [series-mappings-coverage.md](series-mappings-coverage.md).

## Baseline (2026-08-05)

| Metric | Value |
| --- | --- |
| CSV rows | 60 |
| HTML citation/table definitions mapped | 9/9 (100%) |
| In-scope tokens in rules mapped | 78/101 (77.2%) |
| In-scope gaps | 23 |
| Out-of-scope subscript tokens (excluded) | ~150 |

Family coverage (in-scope rule tokens only):

| Family | Mapped | Total | Coverage |
| --- | ---: | ---: | ---: |
| 6 Afro-Asiatic | 51 | 53 | 96.2% |
| 17 Indo-European | 25 | 36 | 69.4% |
| 10 Austronesian | 0 | 8 | 0% |
| 30 Niger-Congo | 2 | 2 | 100% |
| 46 meta vowel shifts | 0 | 2 | 0% |

Regression guards: `tests/conlanger/tools/test_series_mappings.py::test_extraction_confidence_benchmarks_on_full_html` (§6 ≥ 95%, §17 ≥ 65%).

---

## Work items (to push in-scope coverage)

Estimated impact is **in-scope rule pairs** closed if the row is authored; re-run the audit to confirm.

### A. Parallel rule I/O — extractor already supports, rules not picked up (~8 pairs, family 10 → ~85% overall)

These sections have equal-length input/output chains; the extractor should infer mappings but does not yet (likely tokenization: class letter `Z`, set braces, or `b d₂ → {v,b} z` mismatch).

| Section | HTML source | Rule (abbrev.) | Tokens to map |
| --- | --- | --- | --- |
| 10.6 | `index_diachronica_original.html:3822` | `t₁ d₁ d₃ Z → t d ɖ ɟ` | `t₁`→`t`, `d₁`→`d`, `d₃`→`ɟ` (confirm alignment) |
| 10.6 | `:3824` | `b d₂ → {v,b} z` | `d₂`→`z` (singleton; input side only) |
| 10.6 | `:3825` | `S₁ s c → s t ts` | `S₁` is **positional** (uppercase) — skip |
| 10.7 | `:3849` | `{t₁,c} {d₁,z} d₃ → t d ɖ` | `t₁`, `d₁`, `d₃` from parallel sets |

**Work:** extend `_tokenize_rule_side` / parallel inference for braced alternates and mixed-length outputs; add fixture tests from these lines.

---

### B. Omotic x-series — no §6 citation (~2 pairs, family 6 → ~100%)

| Section | Gap | Evidence | Suggested approach |
| --- | --- | --- | --- |
| 6.1.2.1 Aari | `x₁`, `x₂` | `{x₁,x₂}→ɡ` (`:1149`); x-series mapped in all **6.1.1.*** subsections (`x₁`→`k`, etc.) | Add **§6.1** or **§6.1.2** ancestor row from North Omotic rule consensus, or infer `x₁`/`x₂` targets from subsection CSV rows with longest-prefix at `6.1.1` |

**Work:** policy decision — family-wide Omotic row vs subsection-only inheritance; no HTML prose defines x-series at §6.

---

### C. PIE vowel+laryngeal compounds (~11 pairs, family 17 → ~100%)

Tokens like `eh₂` are matched as correspondence-series on base `eh` (lowercase). They need **compound-segment** handling, not single-letter series.

| Section | Tokens | HTML source | Notes |
| --- | --- | --- | --- |
| 17.2 | `eh₂` | `:5035` | `eh₂ → æː` — singleton inference candidate |
| 17.5 | `eh₁`, `eh₂`, `eh₃` | `:5467` | `— eh₁ eh₂ eh₃ → eː aː oː` — parallel chain |
| 17.10 | `eh₃`, `o₂` | (rule line TBD) | `o₂` may be vowel-series, not laryngeal |
| 17.13 | `eh₂`, `eh₃`, `ih₁`, `uh₁` | `:8268`+ | Tocharian diphthong rules |

**Work:** either (1) treat `eh`, `ih`, `uh`, `oh` as series bases in extraction, or (2) add compound decomposition `eh₂` → `e` + `h₂` with inherited `h₂` from §17 table; document in ADR if compounds get their own mechanism.

---

### D. Collective / ambiguous collectives (~1–10 pairs)

| Section | Token | HTML source | Notes |
| --- | --- | --- | --- |
| 17.4.1 Avestan | `hₓ` | `:5460` | `hₓ → ∅` — collective over §17 `h₁–h₃`; add `17,hₓ,{h1,h2,h3}` or similar |
| 17.8.* Greek (×10) | `Hₓ` | various | **Out of scope** — uppercase `H` is Index **class letter** (laryngeal), not correspondence collective; needs class-letter or section-local mechanism |

**Work:** only `hₓ` (lowercase) belongs in `series_mappings.csv`; Greek `Hₓ` is a separate ticket.

---

### E. Vowel-index series (~2 pairs, family 46)

| Section | Tokens | HTML source | Rule |
| --- | --- | --- | --- |
| 46.14 | `i₂`, `æ₂` | `:14441` | `aj → {æ₂,i₂}` — parallel/set inference |

**Work:** same as (A): set-output parallel inference.

---

### F. Section-local / uppercase series (defer — not clear correspondence-series)

| Token | Section | Why deferred |
| --- | --- | --- |
| `Sh₂` | 17.10.1 | Uppercase `Sh` — likely section-local abbreviation, not `s`+subscript series |
| `S₁` | 10.6, 10.7, 15.2.2 | Class letter + index → positional or local label |
| `B₁`, `P₂` | 17.10 | Positional/class-template |

**Work:** spike whether these are correspondence-series or Athabaskan-style section-local labels (`CONTEXT.md` **Section-local abbreviation**).

---

## Explicitly not this backlog

These appear in the full HTML survey but are **out of scope** for ticket 28 / `series_mappings.csv`:

| Kind | Examples | Handle in |
| --- | --- | --- |
| Positional slots | `C₁`, `V₂`, `N₁N₂` | ASCA reference/alpha syntax (future spike) |
| Identity subscripts | `V₀`, `C₀` | Co-reference syntax (future spike) |
| Class-letter collectives | `Hₓ` (Greek) | `group_mappings.csv` or section abbreviations |
| Template compounds | `CV₁`, `nV₁`, `kV₂` | Positional + identity combined |

See **Out-of-scope subscript tokens** in [series-mappings-coverage.md](series-mappings-coverage.md).

---

## Suggested order if picking this up later

1. **A** — Paiwan/Rukai parallel rules (biggest single-family win; family 10 0% → ~100%).
2. **C** — PIE `eh*` compounds (family 17 69% → ~100%).
3. **B** — Omotic x-series ancestor row (family 6 96% → 100%).
4. **D/E** — `hₓ`, Slavic `i₂`/`æ₂` (small tail).
5. **F** — only after owner decision on local abbreviations.

---

## How to verify after each item

1. `uv run extract_series_mappings`
2. Check **Extraction confidence** in `series-mappings-coverage.md`
3. `uv run pytest tests/conlanger/tools/test_series_mappings.py -q`
4. Optionally tighten `test_extraction_confidence_benchmarks_on_full_html` thresholds
5. After ticket 27: re-run `uv run regenerate_corpus` and compare `unknown_character` counts for `₁`, `₂`, … in [inventory/](inventory/)
