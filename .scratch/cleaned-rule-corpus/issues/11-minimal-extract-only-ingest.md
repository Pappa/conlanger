Type: task
Status: ready-for-agent
Blocked by: None

# Minimal extract-only ingest

## What to build

Parse Index Diachronica HTML into applier-neutral cleaned YAML carrying the four rule parts — `input`, `output`, optional `env`, optional `exception` — plus required `raw` and `source` provenance on every **corpus rule**.

Apply **no transforms** at this stage except **Symbol** normalization (`#`, `$`, `%`, `∅`, stress notation → ASCA-canonical form in corpus fields; `raw` unchanged). See `CONTEXT.md` **Symbol**.

Sound-change sections map one-to-one with HTML `<h2>` blocks (section title, index, optional citation). Multi-line `raw` preserved via YAML literal blocks. Parse with lxml (non-strict HTML).

## Explicitly out of scope

- Class-letter expansion and `group_mappings.csv` (retire ingest-time `str.maketrans` from `IndexDiachronicaParser`)
- Feature-matrix synonym replacement (`feature_mappings.csv`)
- `PhonologicalRuleSet` compile layer
- `status` assignment on corpus rules
- Trailing-comment extraction, prose-env mapping, meta-notation, series indices

## Blocked by

None — can start immediately.

## Acceptance criteria

- [ ] `IndexDiachronicaParser` emits spec-aligned YAML (`abbreviations` + `sections`; corpus rules with `input`/`output`/`raw`/`source`; optional `env`/`exception` omitted when absent)
- [ ] Only **Symbol** normalization runs on corpus fields; `raw` preserves Index form byte-for-byte
- [ ] Ingest-time class-letter `maketrans` / `group_mappings` application removed from the parser path
- [ ] `tests/conlanger/tools/test_IndexDiachronicaParser.py` passes for `html_extract` fixture rows (field splitting and provenance)
- [ ] Regenerated YAML is git-diffable from `datadiachronica/index_diachronica_original.html`
