Type: task
Status: resolved
Blocked by: None

# Capture rule comments at parse time

## What to build

Implement [Rule comment field on corpus rules](30-rule-comment-field-on-corpus-rules.md) in `IndexDiachronicaParser`:

1. Add optional **`comment`** to emitted corpus rule dicts; omit when empty.
2. Refactor parse-time prose stripping (semicolon tails, trailing parens/quotes, sporadic gloss text, env qualifiers removed for ASCA) to **capture** removed text into `comment` instead of discarding.
3. **Semicolon rule:** text from first `; ` in a field → append to `comment`; remove from field (extends ticket 21 behaviour).
4. **`raw` unchanged**; `input`/`output`/`env`/`exception` stay ASCA-clean.
5. Emit a short **analysis artifact** under `.scratch/cleaned-rule-corpus/` — e.g. top `comment` n-grams / qualifier phrases (`short only`, `unstressed`, …) for later parser iteration.
6. Update fixtures and `html_extract` rows where comment capture changes field values.

## Notes

- Policy: ticket 30. Schema: ticket 03 (amended).
- Does **not** require restructuring env prose into valid ASCA env (prose-env mapping remains fog).
- Does **not** emit ASCA compile comments yet.

## Acceptance criteria

- [x] `comment` field on corpus rules when inline prose is stripped
- [x] Semicolon tails captured (~87 rules in current corpus have `;` in `raw`)
- [x] Trailing gloss strip (ticket 21 paths) captures to `comment`
- [x] `raw` byte-auditable against HTML
- [x] Qualifier / comment phrase summary artifact written
- [x] Tests on semicolon, `short only`, and parenthetical examples from inventory
- [x] Full inventory re-run optional; note delta in ticket **Answer**

## Answer

Implemented capture-not-discard in `IndexDiachronicaParser` via `extract_*` helpers and `join_rule_comment` / `_append_rule_comment_parts`. Stripped prose from sporadic, trailing-gloss, and stress-env passes accumulates into optional `comment`.

**Corpus re-parse:** **1139 / 9317** rules carry `comment` (field values unchanged vs pre-ticket; validation ok/fail unchanged at 6483/2834).

**Artifact:** [rule-comment-phrases.md](../rule-comment-phrases.md) — emitted by `uv run regenerate_corpus`.

**Tests:** semicolon tail, `(short only)` env paren, sporadic gloss, stress-after-`#` capture.
