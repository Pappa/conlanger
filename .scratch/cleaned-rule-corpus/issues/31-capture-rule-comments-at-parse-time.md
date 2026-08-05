Type: task
Status: ready-for-agent
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

- [ ] `comment` field on corpus rules when inline prose is stripped
- [ ] Semicolon tails captured (~87 rules in current corpus have `;` in `raw`)
- [ ] Trailing gloss strip (ticket 21 paths) captures to `comment`
- [ ] `raw` byte-auditable against HTML
- [ ] Qualifier / comment phrase summary artifact written
- [ ] Tests on semicolon, `short only`, and parenthetical examples from inventory
- [ ] Full inventory re-run optional; note delta in ticket **Answer**
