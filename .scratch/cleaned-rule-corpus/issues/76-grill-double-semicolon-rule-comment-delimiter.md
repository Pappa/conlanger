Type: grilling
Status: ready-for-human
Blocked by:

# Grill: `;;` as rule-line comment delimiter at parse

Spawned from wayfinder session on [Cleaned rule corpus SoT](map.md) ingest pipeline (2026-08-18). Owner expects `;;` to start editorial **comment** prose; current ingest does not treat `;;` uniformly ([Capture rule comments at parse time](31-capture-rule-comments-at-parse-time.md) shipped single-`;` / `; ` heuristics only).

## Question

When and how should **`;;`** delimit **comment** prose during `IndexDiachronicaParser` ingest — relative to today's passes, **Manual mapping** ` ;; ` inserts, and ASCA's `;;` comment syntax at compile?

Decide policy **before** implementation (details and edge cases TBD in this grill).

## Facts (do not re-litigate without new evidence)

- **Structural split first:** `extract_rule_parts` runs on the working line **before** comment capture. Output **chain split** uses every `→` in the post-arrow segment — arrows inside editorial tails can create spurious `stages` (e.g. [Archi `Archi-ɢ,ɣ`](inventory/asca-rule-inventory-error.csv) / manual mapping `ɣ → q ;; (more likely, *ɢ → q instead of → ɣ)`).
- **Today's semicolon capture:**
  - `apply_semicolon_field_comments` — first **single** `;` in **`env` / `exception` only** (`split_field_semicolon_comment`).
  - `extract_semicolon_prose_from_field` — **`; `** (semicolon + space) + English-prose heuristic on stages/env/exception via `apply_trailing_glosses`.
  - No `;;` handling in `src/` (grep empty).
- **Manual mappings** often author ` ;; ` in the `to` column as an editorial marker (see `data/common/manual_mappings.csv` and `manual_mappings_matched_rules.csv`).
- **Corpus `comment`** is ingest-side only — not emitted into ASCA rule strings ([Rule comment field](30-rule-comment-field-on-corpus-rules.md)); compile `malformed_comment` / `trailing-comment` when `; ` fragments remain in `stages`.
- **Distinct from** section-level `comments`, **Index Diachronica correction** overlay, and compile-time ASCA `;;` lines.

## Edge cases to grill (non-exhaustive)

1. **`;;` vs `; ` vs single `;`** — unify on `;;`, treat `;;` as two-char delimiter, or keep field-specific rules?
2. **Which fields** — whole line before split, `stages` only, all of stages/env/exception, input side as well as output?
3. **Order vs chain split** — must `;;` (or comment tail) be stripped **before** `build_stages_from_spine` splits on `→`?
4. **Manual mapping convention** — should ` ;; ` in `manual_mappings.csv` remain author SoT, or should corrections overlay / native Index `;` tails drive capture without manual rows?
5. **Matrix / set punctuation** — `{a,b;c,d}`, feature matrices, nested brackets — false positives on `;` or `;;`.
6. **Index HTML surface** — rules with native `;` editorial tails in `env` (ticket 30 examples) vs double-semicolon only in manual rewrites.
7. **Interaction with** sporadic strip, trailing parens/quotes, stress/medial env passes — one canonical comment pass vs distributed append.
8. **Chained rules** — comment attached to first segment only vs whole spine.
9. **Acceptance** — inventory clusters (`malformed_comment`, `trailing-comment`, Archi-class chain corruption); whether to re-normalise existing manual-mapping ` ;; ` rows after policy lands.

## Outcomes

- Recorded delimiter policy (`;;` scope, field scope, pass order relative to `→` split).
- List of edge cases: handle now vs defer vs document as won't-fix.
- Whether [ADR-0012](../../docs/adr/0012-index-diachronica-corrections-overlay.md) or ticket 30 answer needs amendment.
- Implementation follow-on ticket (task) with acceptance criteria — **no code in this grill**.

## References

- `src/conlanger/tools/ingest/parser.py` — `parse_rule_element` pass order
- `src/conlanger/tools/ingest/transforms.py` — `apply_semicolon_field_comments`, `join_rule_comment`
- `src/conlanger/utils/gloss.py` — `extract_semicolon_prose_from_field`
- `src/conlanger/utils/parsing.py` — `extract_rule_parts`, `build_stages_from_spine`
- [docs/index-diachronica-parser.md](../../docs/index-diachronica-parser.md) (update after policy)

## Comments

- 2026-08-18: Filed from map wayfinder session. Owner direction: `;;` should start comment; implementation details and edge cases deferred to this grill.
