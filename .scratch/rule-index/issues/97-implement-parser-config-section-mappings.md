Type: task
Status: resolved

# Implement parser_config section_mappings

Owner added `section_mappings` to `data/parser_config.yml` (seed: section **10.1** — Austronesian series labels `*D`, `*R`, `*T` → class letters `D`, `R`, `T`). Config exists but is not loaded or applied; rules in affected sections still carry literal `*D` / `*R` / `*T` tokens.

Spawned from [Cleaned rule index SoT](../map.md) fog (**section-local abbreviations** / bulk section mapping rows).

## Problem

Index Diachronica uses section-scoped notation (e.g. Austronesian consonantal series `*D`, `*R`, `*T` in §10.1 and descendants) that should normalize to Index **class letters** at parse time — not via compile `group_mappings.csv` alone and not by populating YAML `abbreviations` tables on each section.

Today:

- `section_mappings` in `parser_config.yml` is ignored by `load_parser_config()`.
- Parse output still includes a top-level `abbreviations: {}` stub (`IndexDiachronicaParser.abbreviations()`), though section-level `abbreviations` are already omitted when empty ([ticket 74](74-implement-ingest-corrections-drop-series-csv.md)).

## What to build

### 1. `parser_config.yml` — `section_mappings` schema

Already present:

```yaml
section_mappings:
  "10.1":
    "*D": "D"
    "*R": "R"
    "*T": "T"
```

- **Keys**: dotted section `index` values (quoted when YAML would parse them as floats).
- **Values**: flat `from → to` string maps (token / substring replacements).
- Load into `ParserConfig` (extend dataclass + `load_parser_config()` in `src/conlanger/utils/file_io.py`).

**Section ancestry:** a mapping for section `10.1` applies to that section **and every descendant** (`10.1.2`, `10.1.2.1`, …). Reuse `section_index_prefixes()` from `src/conlanger/utils/series.py`.

**Merge policy:** same as compile `CompilerConfig.resolved_series_mappings()` — start empty, walk prefixes in order, `update()` each matching section row so **more specific section ids override** ancestor rows for the same `from` key.

### 2. Parse-time application

Apply in `IndexDiachronicaParser.parse_rule_element()` **after** Index Diachronica **corrections** (rule-id overlay on `raw`) and **before** **Manual mapping**:

```text
raw          ← extract + corrections (stored on index rule)
working      ← apply_section_mappings(raw, section_index, config)   # new
working      ← apply_manual_mappings(working, …)                     # existing
…            ← quoted-prose check, symbol norm, extract_rule_parts, … (unchanged)
```

**Transform policy:**

- Substring replace on the **working line** (pre-structural-split), same spirit as `apply_manual_mappings`: longest `from` key first, all occurrences (`str.replace`).
- **`raw` unchanged** — only `stages` / `env` / `exception` (via the working line) reflect mappings.
- Empty / missing `section_index` → no section mappings applied.
- No match → line unchanged (no warn unless owner asks later).

Optional: debug CSV `section_mappings_matched_rules.csv` (mirror manual-mapping artifact) — **out of scope** unless trivial; not required for acceptance.

### 3. Remove top-level `abbreviations` from parse output

Stop emitting the document-level `abbreviations` key from `IndexDiachronicaParser.parse()`:

- Remove `abbreviations()` method (or retire if only used for the stub).
- Return `{sections: [...]}` only.
- Update downstream loaders/tests that expect `doc["abbreviations"]` (`tests/conlanger/tools/ingest/test_parser.py`, `tests/conlanger/tools/test_index_io.py`, any inventory or IO helpers).
- Regen drops `abbreviations: {}` from `data/diachronica/index_diachronica_parsed.yml`.

**Do not** reintroduce per-section `abbreviations` objects in parsed YAML — section mappings are config-driven at parse, not stored tables ([ticket 74](74-implement-ingest-corrections-drop-series-csv.md), [grill 72](72-grill-series-mapping-manual-sot.md)).

### 4. Tests

- Config load: `section_mappings` parsed; quoted section ids; empty / absent key harmless.
- Ancestry: rule in `10.1.2.1` receives mappings from `10.1`; child section row overrides parent for same `from` key.
- Parse order: correction overlay → section mapping → manual mapping (fixture proving manual mapping sees post-section-mapping text).
- `*D` → `D` (and siblings) in seed section family; `raw` still contains `*D`.
- Parse output has no top-level `abbreviations` key.

### 5. Docs

- `docs/system/index-diachronica-parser.md` — new pipeline step (between corrections and Manual mapping); `section_mappings` row in config table; remove / update global `abbreviations` planned row.
- Cross-link from map Notes / [ADR-0004](../../../docs/adr/0004-series-indices-per-section-maps.md) if section-scoped parse policy should be recorded (optional).

### Regen

`uv run create_index`; record any `ok` / inventory delta for §10.x `*D`/`*R`/`*T` rules in **Answer**.

## Policy

- **Section mappings** = owner-curated `parser_config.yml`; applied at parse on the working line; not persisted in index YAML.
- Distinct from compile **`series_mappings`** (`compiler_config.yml`) — correspondence-series indices (`h₁`, `s₁`, …) stay compile-time per [grill 73](73-grill-series-mapping-config-sot.md).
- Distinct from **`group_mappings.csv`** — class-letter expansion remains compile-time; section mappings only rewrite Index surface tokens before structural split.

## Out of scope

- Bulk authoring of additional `section_mappings` rows beyond the seed (inventory-driven follow-up).
- `apply_section_local_abbreviations` compile stub (`planned.py`) — may later consume the same config or retire; not this ticket.
- Regenerating `section_abbreviations.yml` advisory file.
- Moving Austronesian mappings to compile if parse application proves insufficient (file a new ticket).

## Acceptance criteria

- [x] `section_mappings` loads from `parser_config.yml` into `ParserConfig`
- [x] Mappings apply to matching section and all descendants; child overrides parent
- [x] Applied after corrections, before manual mappings; `raw` unchanged
- [x] Top-level `abbreviations` removed from parse output and dependent tests
- [x] Tests green; full gate when finishing
- [x] Parser docs updated

## Answer

Regen (`uv run create_index`): **ok +18** for §10.x `*D`/`*R`/`*T` rules (18 changelog flips at 2026-08-27T22:04:06Z, sections 10.1.2–10.1.2.10). Inventory totals: ok=8606 (+18), fail=1070 (−18). Parsed YAML drops top-level `abbreviations`; Austronesian series tokens normalize to class letters `D`/`R`/`T` in `stages` while `raw` retains `*D`/`*R`/`*T`.

## References

- [`data/parser_config.yml`](../../../data/parser_config.yml) — seed `10.1` rows
- [`src/conlanger/tools/ingest/parser.py`](../../../src/conlanger/tools/ingest/parser.py) — `parse_rule_element` ordering
- [`src/conlanger/utils/mappings.py`](../../../src/conlanger/utils/mappings.py) — `apply_manual_mappings`, `CompilerConfig.resolved_series_mappings`
- [`src/conlanger/utils/series.py`](../../../src/conlanger/utils/series.py) — `section_index_prefixes`
- [Parse-time manual rule mappings](60-parse-time-manual-rule-mappings.md) — manual mapping runs after section mappings (order amended by this ticket)
- [Implement ingest corrections overlay](74-implement-ingest-corrections-drop-series-csv.md) — corrections before both
