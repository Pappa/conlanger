Type: task
Blocked by: 59
Status: resolved

# Parse-time manual rule mappings

Owner-authored rewrites for Index lines that cannot be fixed programmatically. Load `data/common/manual_mappings.csv` at parse time and apply **before** any other transform; **`raw`** in index YAML stays the HTML surface string.

Spawned from grill 2026-08-09 ([map](../map.md)).

## Problem

Some Index Diachronica rule lines are malformed, editorial, or ambiguous in ways no general correction pass can resolve safely. The maintainer has already decided the intended phonological rule and recorded it in `data/common/manual_mappings.csv` (seeded with two rows):

| `from` (excerpt) | `to` | `reason` |
| --- | --- | --- |
| `m̩ n̩ → am an / _{s,({m,j,w)V}` | `m̩ n̩ → am an / _{s,({m,j,w})V}` | bracket correction |
| `"The PIE rules for the voicing of s → z…"` (prose paragraph) | `s → z / _C[+voice]` | `*nisdos > nizdos` |

Today:

- Row 1 parses with a broken env (`_{s,({m,j,w)V}`) — compile/validation fail.
- Row 2 is `stages: []` / `status: skipped` as quoted prose ([`index_diachronica_parsed.yml`](../../../data/diachronica/index_diachronica_parsed.yml) ~20470).

## Decision (grill 2026-08-09)

| # | Decision |
| --- | --- |
| Q1 | **Substring match** — `from` must appear in the extracted HTML string; replace that substring with `to` to form the working parse string. `raw` on the index rule stays the unmodified extract. |
| Q2 | **No `comment` mutation** — emit debug CSV `manual_mappings_matched_rules.csv` (see below). `reason` stays human audit in `manual_mappings.csv` only. |
| Q3 | **No index flag** on the rule. |
| Q4 | **Console warning** once per unmatched `from` pattern per regen (not per HTML line). |
| Q5 | Manual mapping runs **before** `is_quoted_prose_paragraph` and all other parse transforms. |

### Debug artifact: `manual_mappings_matched_rules.csv`

Written each regen (rewrite, not append) under the inventory dir (same default as `asca-rule-inventory.csv`):

| Column | Value |
| --- | --- |
| `section_index` | Section index from HTML heading |
| `section_name` | Section title |
| `rule_idx` | 0-based index within section rules list (same convention as inventory) |
| `source` | `file:line` provenance |
| `manual_mapping` | The `to` column value applied |

One row per mapping hit (if multiple patterns match one rule in one pass, one row per applied pattern).

## What to build

### 1. CSV loader

- Path: `data/common/manual_mappings.csv` (default; overridable in tests).
- Required columns: `from`, `to`. Optional: `reason` (audit only; not written to index).
- Reject duplicate `from` keys at load time.
- `load_manual_mappings()` + apply helper in `parsers.py`.

### 2. Parse-time application (first transform)

In `IndexDiachronicaParser.parse_rule_element()` (or caller with section context), immediately after `raw = extract_text_with_subs(el)`:

```text
raw          ← HTML surface (stored on index rule)
working      ← apply_manual_mappings(raw)   # substring replace
…            ← is_quoted_prose_paragraph(working)? … NO — use working
…            ← normalize_symbols(working) → extract_rule_parts → … (unchanged order)
```

**Substring policy (implementation):**

- Scan mappings in CSV order; if `from in working`, replace **all occurrences** (`str.replace(from, to)`), record hit, continue (allow chained fixes only if multiple rows match disjoint substrings — unlikely).
- Prefer **longest `from` first** when building the apply list if order ambiguity matters (document in code if adopted).

Collect hits on the parser (or parse pass) with `section_index`, `section_name`, `rule_idx`, `source`, `manual_mapping` for regen to flush.

### 3. Regen integration

- `uv run create_index` writes `manual_mappings_matched_rules.csv` alongside inventory outputs.
- After full parse, emit **one console warning per `from` pattern** that never matched any rule in that regen.

### 4. Tests

- Unit: loader, duplicate-key error, substring hit/miss, first-occurrence replace.
- Integration: Old Irish HTML rows 5499 and 5509 — `raw` unchanged; `stages`/`env` reflect `to`; row 2 no longer `skipped`; hit row appears in debug CSV.
- Regression: rules without a manual row parse identically to today.

### 5. Regen + inventory

- Re-run `uv run create_index`; record ok-count delta in **Answer**.
- Expect row 1 env fix + row 2 new compileable rule (exact uplift TBD).

## Out of scope

- Regex / fuzzy matching
- `reason` → index `comment`
- Corpus-rule boolean flag for manual mapping
- Compile-time application
- Replacing `ipa_mappings.csv`, `feature_mappings.csv`, or correction passes for systematic clusters

## Acceptance criteria

- [x] `manual_mappings.csv` loaded at parse time; substring replace before all other transforms
- [x] Corpus `raw` always preserves pre-mapping HTML string
- [x] `manual_mappings_matched_rules.csv` written on regen with required columns
- [x] Unmatched `from` patterns: one console warning each per regen
- [x] Both seed rows produce expected `stages` / `env`; row 2 no longer skipped
- [x] Tests + full pytest gate green
- [x] Inventory re-baseline with before/after ok count in **Answer**

## References

- Seed file: [`data/common/manual_mappings.csv`](../../../data/common/manual_mappings.csv)
- Analogous loader pattern: [Correction pass: IPA letter mappings](49-correction-pass-ipa-letter-mappings.md) (`apply_ipa_mappings` — runs later, field-level)
- Glossary: **Manual mapping** in `CONTEXT.md`

## Answer

Parse-time **manual mappings** land in `parsers.py`: `load_manual_mappings` / `apply_manual_mappings` (longest-`from`-first, first-occurrence replace); `IndexDiachronicaParser` applies them immediately after extract, before `is_quoted_prose_paragraph` / `normalize_symbols`; index `raw` stays the HTML surface. Regen writes `manual_mappings_matched_rules.csv` and warns once per unmatched `from`.

**Inventory:** before **7184 / 9201 ok (78.1%)** → after **7185 / 9201 ok** (**+1**). Both seed rows match; HTML:5499 (`s → z / _C[+voice]`) flips to ok; HTML:5509 gets fixed env `_{s,({m,j,w})V}` but still fails `nested_brackets` under ASCA.
