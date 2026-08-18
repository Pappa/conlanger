Type: task
Status: ready-for-agent
Blocked by: 76

# Implement first-`;` comment cut before chain split

Spawned from [grill 76](76-grill-double-semicolon-rule-comment-delimiter.md) (owner confirmed 2026-08-18). **Manual mapping** CSV already uses `;` (not `;;`); do not re-introduce `;;`.

## Problem

`extract_rule_parts` splits every `→` on the working line **before** comment capture. Editorial tails that contain arrows (Archi `ɣ → q ; (more likely, *ɢ → q instead of → ɣ)`) become spurious **stages**. Leftover `;` in stages also feeds ASCA `malformed_comment` / `trailing-comment`. Grill 76: peel the first `;` **before** that split.

## What to build

### Pass order in `parse_rule_element`

After **Manual mapping** and `is_quoted_prose_paragraph` (unchanged), **before** `normalize_symbols` / `extract_rule_parts`:

1. Find the **first `;`** on the working line (naive: anywhere, including inside parens/quotes). If none, continue as today.
2. Cut: **remainder** = text before `;` (rstrip); **tail** = text after `;` (strip).
3. Run `normalize_symbols` + `extract_rule_parts` on the **remainder only**.
4. If `extract_rule_parts` returns `None` (no `→`): emit `stages: []`, `status: skipped`, **rule comment** = tail (omit `comment` if tail empty). `raw` unchanged.
5. If it parses: seed `comment` from the tail (omit if empty), then the rest of today’s remainder pipeline (series expansion, sporadic, trailing glosses, stress, medial, feature/IPA). Later captures still `join_rule_comment` onto that seed.
6. Do **not** scan **rule comment** for `sporadic` / gloss / stress / medial. Detectors stay on **stages** / **env** / **exception** only. Uncertainty that should set `sporadic: true` must appear **before** `;` (mapping convention).
7. Do **not** run symbol / feature / IPA / series transforms on the tail. Later `;` inside the comment stay in the comment (no second split).
8. Stop calling `apply_semicolon_field_comments` — the whole-line cut replaces it. `extract_semicolon_prose_from_field` inside trailing glosses may remain as a harmless no-op on remainder.

### Docs

Update [docs/index-diachronica-parser.md](../../docs/index-diachronica-parser.md): insert the first-`;` peel **before** Phase C structural split; note remainder-only symbol norm; note that field-level env/exception `;` capture is retired.

### Tests (minimum)

- Archi-style: `ɣ → q ; (more likely, *ɢ → q instead of → ɣ)` → **stages** `ɣ`, `q` (no extra chain); gloss in **rule comment**.
- Native editorial tail: `VOR → VːR; “this is a tad unclear…”` → last stage has no trailing `;`; quote in **comment**.
- Leading `;` / no arrow in remainder → skipped with **comment** = tail (Romanian / Guānhuà mapping shape).
- `/ sporadic ; in Mentasta Ahtna` (or equivalent) still sets `sporadic: true` from remainder.
- Keyword **after** `;` only (`yː ; (sometimes)` with no `sporadic` before the cut) does **not** set `sporadic`.
- Tail is not symbol-normalised (prose `#` / `%` in comment stay as in the tail).

### Regen

`uv run regenerate_corpus` (or the repo’s usual inventory regen). Note changelog `ok` flips in **Answer**. Watch `malformed_comment` / `trailing-comment` and `Archi-ɢ,ɣ`.

## Out of scope

- Detector-on-comment (looking at the tail for `sporadic` / gloss)
- Field-source detection counts in `asca-rule-inventory-summary.md`
- Bracket-aware / quote-aware `;` (owner mappings cover false positives)
- Emitting corpus **rule comment** as ASCA `;;`
- ADR-0012
- Re-authoring **Manual mapping** rows (owner already converted `;;` → `;` and added Kyrgyz/Blackfoot/Greek rows)

## Acceptance criteria

- [ ] First `;` peeled from working line after mappings / quoted-prose skip, before `extract_rule_parts`
- [ ] Remainder-only symbol norm + structural split; tail is **rule comment** as-is
- [ ] No-`→` remainder → skipped with `comment` = tail
- [ ] `apply_semicolon_field_comments` no longer runs
- [ ] Sporadic/gloss detectors do not read `comment`
- [ ] Tests above green; full gate (`uv run pytest`, ruff) when finishing
- [ ] Parser docs updated
- [ ] Inventory regen; `ok`-flip delta and `malformed_comment` / Archi notes in **Answer**

## References

- [Grill 76](76-grill-double-semicolon-rule-comment-delimiter.md)
- [Ticket 30](30-rule-comment-field-on-corpus-rules.md) (order amended)
- `src/conlanger/tools/ingest/parser.py` — `parse_rule_element`
- `src/conlanger/tools/ingest/transforms.py` — `apply_semicolon_field_comments`, `join_rule_comment`
- `data/common/manual_mappings.csv`
