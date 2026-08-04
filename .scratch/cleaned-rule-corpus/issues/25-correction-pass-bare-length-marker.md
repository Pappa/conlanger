Type: task
Status: resolved
Blocked by: 24

# Correction pass: remaining bare length marker ː

Target cluster: `unknown_character` — error_token `ː` (~242 rules)

## What was built

Extended `normalize_asca_length_marks()` in `rules.py`:

- Broader `_IPA_SEGMENT` (Latin extended + IPA modifiers like ʷ ʲ)
- `segment(ː,extra)` → `{segment:[+long],segmentextra}`
- `{set}(ː)` / `{set}ː` → `:[+long]` on set
- bare `ː` set members → `V:[+long]`
- dedupe `:[+long]ː`

## Answer (before/after)

Baseline (after issue 23): **6254 / 9316** ok; **242** rules with `ː` unknown_character.

Combined re-run with issue 24 (parse regen + compile):

- **6422 / 9317** ok (**+168** total vs 6254)
- `ː` unknown_character **242 → 40** (remainder: complex meta notation, `(ː,V)` env patterns, etc.)
