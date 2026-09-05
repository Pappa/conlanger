Type: task
Status: resolved
Blocked by: None

# Minimal extract-only ingest

## What to build

Parse Index Diachronica HTML into applier-neutral cleaned YAML carrying the four rule parts — `input`, `output`, optional `env`, optional `exception` — plus required `raw` and `source` provenance on every **index rule**.

Apply **no transforms** at this stage except **Symbol** normalization (`#`, `$`, `%`, `∅`, stress notation → ASCA-canonical form in index fields; `raw` unchanged). See `CONTEXT.md` **Symbol**.

Sound-change sections map one-to-one with HTML `<h2>` blocks (section title, index, optional citation). Multi-line `raw` preserved via YAML literal blocks. Parse with lxml (non-strict HTML).

## Explicitly out of scope

- Class-letter expansion and `group_mappings.csv` (retire ingest-time `str.maketrans` from `IndexDiachronicaParser`)
- Feature-matrix synonym replacement (`feature_mappings.csv`)
- `DiachronicSeries` compile layer
- `status` assignment on index rules
- Trailing-comment extraction, prose-env mapping, meta-notation, series indices

## Blocked by

None — can start immediately.

## Acceptance criteria

- [x] `IndexDiachronicaParser` emits spec-aligned YAML (`abbreviations` + `sections`; index rules with `input`/`output`/`raw`/`source`; optional `env`/`exception` omitted when absent)
- [x] **Symbol** normalization runs on index fields; `raw` preserves Index form byte-for-byte
- [x] Ingest-time class-letter `maketrans` / `group_mappings` application removed from the parser path
- [x] `tests/conlanger/tools/test_IndexDiachronicaParser.py` passes for `html_extract` fixture rows (field splitting and provenance)
- [x] Regenerated YAML is git-diffable from `data/diachronica/index_diachronica_original.html`

## Answer

Delivered via `IndexDiachronicaParser` (`src/conlanger/tools/parsers.py`) and `write_cleaned_index` (`src/conlanger/tools/index_io.py`). Output: `data/diachronica/index_diachronica_parsed.yml`.

Core ticket scope met: four rule parts + **Symbol** normalization; class letters and feature matrices deferred. Correction passes [14–25](14-correction-pass-unknown-grouping.md) later added parse-time class-first transforms (em dash, arrows, chain split, glosses, stress, `sporadic`) per ticket [13](13-correction-pass-template.md) — beyond the original “symbol-only” milestone but consistent with the edit ladder.

Regenerate:

```bash
uv run create_index --skip-validation
```
