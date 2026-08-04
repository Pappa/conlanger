Type: task
Status: resolved
Blocked by: 19

# Correction pass: trailing bracket / quote glosses

Target cluster: `malformed_comment`, `syntax_other`, `unknown_character` from English prose after rule syntax — trailing `(…)`, `"…"`, and `; …` tails.

## Policy

Keep the phonological rule; strip Index editorial glosses at **parse time** (same seam as sporadic). ``raw`` unchanged.

## What was built

- `strip_trailing_gloss_from_field()` / `apply_trailing_glosses()` in `parsers.py`:
  1. Trailing quoted prose (smart or ASCII quotes)
  2. Trailing `(…)` blocks — URLs, dialect labels (`Ōgami`), language lists, `except…`, semicolon prose inside parens
  3. Trailing `; …` English prose (ASCA malformed-comment class)
- Preserves phonological `(?)`, `(kʼ)`, `C(…C)`, etc.
- Wired after `apply_sporadic_qualifier` in `parse_rule_element`.

## Examples

| Before (field) | After |
|----------------|-------|
| `p (some Polynesian languages, …)` | `p` |
| `f (Common Celtic; I'm not sure…)` | `f` |
| `s̩ f̩ (Ōgami) (http://…)` | `s̩ f̩` |
| `ɔa "(except NV… > a:[+long])"` | `ɔa` |

## Acceptance criteria

- [x] Parse-time strip; `raw` preserved
- [x] Unit + integration tests on user examples
- [x] Inventory re-baseline recorded

## Answer (before/after)

Baseline (after issue 20): **5713 / 9334** ok (61.2%).

Full inventory re-run:

- **6204 / 9316** ok (**+491** rules, **66.6%**)
- `malformed_comment` cluster **100 → 12**
- Corpus rows **9334 → 9316** (chain re-split after gloss removal from some chained outputs)
- Fields that would strip to empty `input`/`output` are left unchanged (e.g. quoted-only outputs)
