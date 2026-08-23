Type: task
Status: resolved
Blocked by: 23

# Correction pass: smart quotes and typographic apostrophes

Target cluster: `unknown_character` — `"` `"` `'` (U+201C/U+201D/U+2019)

## What was built

- Parse-time `strip_embedded_quoted_gloss_from_field()` — removes embedded `"…"` prose and orphan `"`/`"` at field ends (wired into `strip_trailing_gloss_from_field`)
- Compile-time `normalize_typographic_apostrophes()` — U+2019 after segments → U+02BC before ejective pass

## Answer (before/after)

Baseline (after issue 23): **6254 / 9316** ok (67.1%).

Full inventory re-run:

- **6422 / 9317** ok (**+168** rules, **68.9%**)
- `"` errors **31 → 3**; `"` **44 → 42** (remainder mostly unexpanded stress marks); `'` **24 → 10**
