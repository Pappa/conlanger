# Series mappings — coverage backlog

> **Legacy artifact.** This backlog tracked parse-time `series_mappings.csv` coverage through [ticket 65](issues/65-series-mappings-coverage-pass.md) (closed 2026-08-12). The CSV path was retired 2026-08-18 ([grill 72](issues/72-grill-series-mapping-manual-sot.md) → [74](issues/74-implement-ingest-corrections-drop-series-csv.md) / [75](issues/75-implement-compiler-config-series-mappings.md)). Current SoT: `data/parser_config.yml` (`series_expansions`) and `data/compiler_config.yml` (`series_mappings`).

Follow-up work to raise **in-scope** extraction coverage beyond the original HTML-extract baseline.  
Regenerate metrics after any change: ~~`uv run create_index --update-series-mappings`~~ *(retired CLI)*.

**Related:** [27-implement-parse-time-correspondence-series-expansion](issues/27-implement-parse-time-correspondence-series-expansion.md) (done), live report [series-mappings-coverage.md](series-mappings-coverage.md), coverage pass [65](issues/65-series-mappings-coverage-pass.md) (done — **101/101**).

## Baseline (2026-08-05)

| Metric | Value |
| --- | --- |
| CSV rows | 60 |
| HTML citation/table definitions mapped | 9/9 (100%) |
| In-scope tokens in rules mapped | 78/101 (77.2%) |
| In-scope gaps | 23 |
| Out-of-scope subscript tokens (excluded) | ~150 |

## After ticket 65 (2026-08-12)

| Metric | Value |
| --- | --- |
| CSV rows | 107 |
| HTML citation/table definitions mapped | 9/9 (100%) |
| In-scope tokens in rules mapped | 101/101 (100%) |
| In-scope gaps | 0 |
| Out-of-scope subscript tokens (excluded) | 150 |

Family coverage (in-scope rule tokens only): **6 / 10 / 17 / 30 / 46 all 100%**.

Regression guards: `tests/conlanger/tools/test_series_mappings.py::test_extraction_confidence_benchmarks_on_full_html` (all in-scope families fully mapped).

---

## Work items

### A–E — closed by [65](issues/65-series-mappings-coverage-pass.md)

| Item | Status |
| --- | --- |
| A. Parallel rule I/O (family 10) | Done — mixed slots + braced alternates |
| B. Omotic x-series | Done — `{x₁,x₂}→ɡ` brace expansion |
| C. PIE vowel+laryngeal compounds | Done — length marks + I/O + digit attestation |
| D. Collectives (`hₓ`) | Done — collectives from inventory tables |
| E. Vowel-index series (§46) | Done — digit attestation for `æ₂`/`i₂` |

### F. Section-local / uppercase series (defer — not clear correspondence-series)

| Token | Section | Why deferred |
| --- | --- | --- |
| `Sh₂` | 17.10.1 | Uppercase `Sh` — likely section-local abbreviation, not `s`+subscript series |
| `S₁` | 10.6, 10.7, 15.2.2 | Class letter + index → positional or local label |
| `B₁`, `P₂` | 17.10 | Positional/class-template |

**Work:** spike whether these are correspondence-series or Athabaskan-style section-local labels (`CONTEXT.md` **Section-local abbreviation**).

---

## Explicitly not this backlog

These appear in the full HTML survey but are **out of scope** for `series_mappings.csv`:

| Kind | Examples | Handle in |
| --- | --- | --- |
| Positional slots | `C₁`, `V₂`, `N₁N₂` | ASCA reference/alpha syntax (future spike) |
| Identity subscripts | `V₀`, `C₀` | Co-reference syntax (future spike) |
| Class-letter collectives | `Hₓ` (Greek) | `group_mappings.csv` or section abbreviations |
| Template compounds | `CV₁`, `nV₁`, `kV₂` | Positional + identity combined |

See **Out-of-scope subscript tokens** in [series-mappings-coverage.md](series-mappings-coverage.md).

---

## How to verify after each item

*(Historical — steps below applied to the retired CSV path only.)*

1. ~~`uv run create_index --update-series-mappings`~~
2. Check **Extraction confidence** in `series-mappings-coverage.md`
3. ~~`uv run pytest tests/conlanger/tools/test_series_mappings.py -q`~~
4. Optionally tighten `test_extraction_confidence_benchmarks_on_full_html` thresholds
5. Re-run `uv run create_index` and compare `unknown_character` counts for `₁`, `₂`, … in [inventory/](inventory/)
