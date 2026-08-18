Type: task
Status: resolved

# Implement parser_config section skip

Owner added `skip_sections` to `data/parser_config.yml` (seed: section **37.1.2.4.2** — Index misrepresents source material). **Section-level** hold-out: distinct from per-rule `status: skipped` (rule-level skipping remains inventory-driven / ADR-0010).

## Problem

Heavy-residual sections may be skipped when Index Diachronica does not faithfully represent the source (see map Notes). Config entries exist but `ParserConfig` does not load them, parsed YAML has no section flag, compile still runs, and inventory counts those rules as ordinary OK/Fail.

**Config shape today is invalid YAML** (loads as `{section: null, id: …, reason: …}` siblings). Fix to a documented list shape as part of this ticket.

## What to build

### 1. `parser_config.yml` — `skip_sections` schema

Normalize to a flat list (preferred):

```yaml
skip_sections:
  - id: "37.1.2.4.2"
    reason: "Index Diachronica does not represent the source material correctly: …"
```

- **`id`**: matches section **`index`** in parsed YAML (dotted ancestry key from `<h2>` heading).
- **`reason`**: operator documentation only; not required on the corpus section object.

Load into `ParserConfig` (extend `ParserConfig` + `load_parser_config()` in `src/conlanger/utils/mappings.py` / `file_io.py`).

### 2. Parse-time — `IndexDiachronicaParser`

When emitting a section whose `index` is listed in `skip_sections`:

1. Parse the HTML section **as today** (rules, citation, comments unchanged).
2. Append **`skipped: true`** on the section dict in `index_diachronica_parsed.yml`.
3. Do **not** set `status: skipped` on individual rules inside the section.
4. Do **not** strip or rewrite rule fields; `raw` unchanged.

### 3. Compile-time

When a section has **`skipped: true`**:

- **No compile** for any rule in that section (skip `SoundChangeRule` construction / ASCA pipeline for those rules).
- Implement at the compile boundary (`DiachronicSeries` or the inventory/compile caller) — not by mutating corpus rules.

Distinction from rule-level hold-outs: `status: skipped` / `skip` on a rule still applies only to that rule inside an otherwise active section.

### 4. Inventory — `corpus_inventory.py` + summary

Rules in **`skipped: true`** sections:

- Do **not** call `validate_asca`.
- Emit inventory rows marked **skipped** (e.g. `ok=True`, `failure_class=section_skipped` or dedicated `skipped` column — pick one approach and use consistently in CSV + summary).
- **`summarize_inventory`** adds lines matching:

  ```
  - Skipped: **N** (pct%)
  - Sections skipped: **M / total** (pct%)
  ```

  Percentages are of **total corpus rules** / **total sections** respectively (same style as OK/Fail lines). Example target after seeding one section:

  ```
  - Rows: **9638** (one per corpus rule)
  - OK: **8026** (83.3%)
  - Fail: **1612** (16.7%)
  - Skipped: **30** (0.3%)
  - Sections all OK: **286 / 714** (40.1%)
  - Sections skipped: **3** (0.3%)
  ```

- Optionally list skipped section ids/names in summary **Notes** or a small table.

### 5. Tests

- Parser: listed section gets `skipped: true`; unlisted section does not.
- Config load: flat `id`/`reason` list; unknown section id is harmless.
- Compile/inventory: skipped-section rules produce no ASCA validation attempt and appear in Skipped counts.
- `section_all_ok_stats` excludes skipped sections from the “all OK” denominator (or document if they count as neither OK nor fail — align with summary math above).

### 6. Docs

- `docs/index-diachronica-parser.md` — `skip_sections` config + `skipped` section field.
- `CONTEXT.md` or schema ticket cross-link if section `skipped` amends the corpus schema (optional field on section objects).

### Regen

`uv run regenerate_corpus`; record rule/section skip counts and any OK/Fail delta in **Answer**.

## Policy

- **Section skip** = owner-curated config (`parser_config.yml`); permanent, citation-backed.
- **Rule skip** (`status: skipped`) = per-rule hold-out after class-first work (ADR-0010); unchanged by this ticket.
- Parse still extracts skipped sections so rules remain visible in the corpus and inventory.

## Out of scope

- Rule-level `status: skipped` policy changes (edge-split / ADR-0005 triage).
- Auto-skipping sections from validation fail counts.
- Storing `reason` on the section object in parsed YAML (config only unless owner asks).
- Brassica compile path.

## Acceptance criteria

- [x] `skip_sections` loads from `parser_config.yml` with corrected YAML shape
- [x] Listed sections parse normally and gain `skipped: true` on the section object
- [x] Compile path skips all rules in `skipped: true` sections
- [x] Inventory CSV + `asca-rule-inventory-summary.md` report **Skipped** rule count and **Sections skipped** count
- [x] Tests green; full gate when finishing
- [x] Parser docs updated

## Answer

Implemented 2026-08-18.

- **`ParserConfig.skip_section_ids`** loaded from flat `skip_sections: [{id, reason}]` in `data/parser_config.yml` (seed **37.1.2.4.2**).
- **Parse:** `IndexDiachronicaParser` sets `skipped: true` on matching sections; rules unchanged.
- **Compile:** `DiachronicSeries` returns after metadata when `section.skipped`; no `SoundChangeRule` parts.
- **Inventory:** `validate_corpus_rule` short-circuits with `failure_class=section_skipped`; summary adds **Skipped** / **Sections skipped** lines; skipped rows excluded from success/error CSV splits; section all-OK stats exclude skipped sections.

**Regen (`uv run regenerate_corpus`):** **9638** rules — OK **8007** (83.1%), Fail **1600** (16.6%), **Skipped 31** (0.3%); **Sections skipped 1 / 714** (0.1%); sections all OK **286 / 713** (40.1%). Changelog **12** ok-flips (rules moved out of OK/Fail into skipped). Parsed YAML: one section with `skipped: true` at **37.1.2.4.2**.

## References

- [`data/parser_config.yml`](../../../data/parser_config.yml)
- [`src/conlanger/tools/ingest/parser.py`](../../../src/conlanger/tools/ingest/parser.py) — section emission
- [`src/conlanger/tools/corpus_inventory.py`](../../../src/conlanger/tools/corpus_inventory.py) — `validate_corpus_rule`, `summarize_inventory`
- [`src/conlanger/tools/rules.py`](../../../src/conlanger/tools/rules.py) — `DiachronicSeries`
- [Corpus rule `stages` schema / rule `status: skipped`](59-corpus-rule-stages-schema.md)
- [Parse-time correspondence-series indices (no pre-emptive rule skip)](26-parse-time-correspondence-series-indices.md)
