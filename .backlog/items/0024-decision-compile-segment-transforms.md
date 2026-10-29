Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Compile pipeline segment transforms (grouping, IPA, tone, clicks, etc.).
Blocked by:

## Question

Which **segment-level Index notations** are normalized or expanded at **compile** rather than stored as ASCA-shaped SoT?

## Answer

The compile pipeline applies, among others: **group mappings**, length and **ejective** normalisation, **parenthetical/meta** expansion, **superscript** modifiers, **IPA letter** mappings, **tone** matrices, **Khoisan click** defaults, labialized class letters, and dot-affricate / prenasal fixes.

SoT YAML stays Index-shaped; ASCA literals are produced at compile validation time—not baked into applier-neutral fields unless applier-agnostic.

## Comments

- Migrated summary (2026-10-29): compile correction-pass cluster + transform-order spike merged.
