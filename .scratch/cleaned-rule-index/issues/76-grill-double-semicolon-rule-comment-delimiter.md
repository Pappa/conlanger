Type: grilling
Status: resolved
Blocked by:

# Grill: `;;` as rule-line comment delimiter at parse

Spawned from wayfinder session on [Cleaned rule index SoT](map.md) ingest pipeline (2026-08-18). Owner expects `;;` to start editorial **comment** prose; current ingest does not treat `;;` uniformly ([Capture rule comments at parse time](31-capture-rule-comments-at-parse-time.md) shipped single-`;` / `; ` heuristics only).

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
- **Corpus `comment`** is ingest-side only — not emitted into ASCA rule strings ([Rule comment field](30-rule-comment-field-on-index-rules.md)); compile `malformed_comment` / `trailing-comment` when `; ` fragments remain in `stages`.
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

## Settled (grill closed 2026-08-18; owner confirmed)

Delimiter is the **first `;`** on the working line (after **Manual mapping**), not `;;`. Naive cut (including inside parens/quotes). Peel **before** `extract_rule_parts`. Tail is **rule comment** as-is; detectors do **not** read it. Owner mappings plant the intended `;` first and plant `sporadic` before `;`.

Full policy in **Answer**. Implementation: [77](77-implement-first-semicolon-comment-cut.md).

## Answer

Owner confirmed (2026-08-18). Policy (amends ticket 30 extraction **order** only; schema unchanged):

1. **Delimiter.** First `;` on the working line after **Manual mapping**. Trim whitespace on both sides of the cut. Not `;;`. Naive — first `;` anywhere, including inside parens/quotes. Owner adds **Manual mapping** rows so the *intended* `;` is first (CSV already rewrote `;;` → `;`; Kyrgyz/Blackfoot/Greek sporadic convention rows present).
2. **Pass order.** Quoted-prose skip (unchanged) → peel that `;` tail from `working` → `normalize_symbols` + `extract_rule_parts` on the **remainder only**. The tail never becomes **stages**. One **index rule**, one **rule comment** for the whole spine.
3. **Empty remainder.** No `→` after the cut → `status: skipped`, `stages: []`, **rule comment** = the tail. `raw` unchanged.
4. **Comment vs remainder.** Tail stored as-is (no symbol/feature/IPA/series). Remainder keeps today’s sporadic / gloss / stress / medial / mappings. No second `;` pass on remainder. Detectors **do not** scan **rule comment**. Uncertainty that should set `sporadic: true` stays **before** `;`.
5. **Docs / ADRs.** Update [docs/system/index-diachronica-parser.md](../../docs/system/index-diachronica-parser.md) in the implement ticket. **No** ADR-0012 change. No new ADR. Ticket 30 “comment after `→` split” is amended by (2). Still do **not** emit index **rule comment** as ASCA `;;`.
6. **Out of scope.** Detector-on-comment; field-source telemetry in the inventory summary; bracket-aware `;`; unifying on `;;`.
7. **Acceptance watch.** Regen changelog `ok` flips; Archi chain corruption and `malformed_comment` / `trailing-comment` should move. New fails → a later ticket, not a different cut.

Handle now vs later:

| Case | Disposition |
| --- | --- |
| Native editorial `;` tails (`Old-Irish-VOR`, Moroccan `; the change…`) | Handle: whole-line first `;` before chain split |
| Archi `→` inside gloss | Handle: mapping inserts `;` before the gloss; cut before `extract_rule_parts` |
| Paren/quote-internal `;` (Kyrgyz, Blackfoot) | Owner mapping inserts an earlier `;`; naive cut otherwise |
| `sporadic` / `sometimes` after `;` | Won't-fix as detector-on-comment; mappings plant the keyword before `;` |
| Field-source detection counts | Won't-fix |
| ASCA compile `;;` emission from `comment` | Unchanged (ticket 30): not this slice |

Follow-on: [77 — Implement first-`;` comment cut before chain split](77-implement-first-semicolon-comment-cut.md).

## References

- `src/conlanger/tools/ingest/parser.py` — `parse_rule_element` pass order
- `src/conlanger/tools/ingest/transforms.py` — `apply_semicolon_field_comments`, `join_rule_comment`
- `src/conlanger/utils/gloss.py` — `extract_semicolon_prose_from_field`
- `src/conlanger/utils/parsing.py` — `extract_rule_parts`, `build_stages_from_spine`
- [docs/system/index-diachronica-parser.md](../../docs/system/index-diachronica-parser.md) (update in [77](77-implement-first-semicolon-comment-cut.md))

## Comments

- 2026-08-18: Filed from map wayfinder session. Owner direction: `;;` should start comment; implementation details and edge cases deferred to this grill.
- 2026-08-18: Grill closed. Owner reversed the `;;` delimiter to **first `;`**, rewrote mapping `to` values, and declined detector-on-comment / telemetry. Implementation is ticket 77.
