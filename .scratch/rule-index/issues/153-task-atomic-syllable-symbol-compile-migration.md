Type: task
Status: ready-for-agent
Blocked by: None

# Task: atomic migration of syllable/stem symbols to ASCA compile

Spawned from [Grill: ASCA-shaped syntax in the applier-neutral rule index](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) (2026-10-17).

## Question

Move Index **`%`** (syllable boundary) and stem **`$`** handling out of parse-time `normalize_symbols()` into ASCA **compile**, in **one** change set with full impact review (acceptance per ticket 148).

## Acceptance

- SoT keeps Index `%` and `$`; no syllable `%` → ASCA `$` at parse.
- ASCA compile applies syllable/stem projection before or as part of existing symbol steps.
- All unit tests, fixtures, and docs that assumed ASCA `$` in parsed YAML updated.
- Regen impact summarized (inventory/changelog); breaking regen expected.

## Out of scope

- Stress mark rewrite (separate: postfix `[+stress]` at parse).
- `position.in: U#` structured env (separate implementation ticket under [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md)).
