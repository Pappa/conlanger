Type: grilling
Status: needs-grilling
Blocked by: None

# Grill: ASCA-shaped syntax in the applier-neutral rule index

Spawned from wayfinder session 2026-10-17 on [Cleaned rule index SoT](../map.md). Owner input: Index Diachronica **Symbol** normalisation and other parse-time surface cleanup have introduced **ASCA-specific** tokens into YAML and working-line transforms; some may be defensible as **applier-agnostic canonical** surface, others are ASCA-only and belong at compile.

## Question

For each class of non-Index surface in parsed YAML (`stages`, structured `env`/`exception` `context`, and working-line-only transforms), decide whether it may remain in the **applier-neutral SoT**, must stay **Index-shaped** until compile, or should become **structured fields** (no applier syntax in strings). Lock policy for **`normalize_symbols()`** / **`normalize_stress_marks()`** in `conlanger.utils.symbols` (Index `%` → `$`, syllable vs stem `$`, stress `”` → `segment:[+stress]`, etc.).

## Scope for the grill

| Area | Examples in tree today | Tension |
| --- | --- | --- |
| Boundary / stress symbols | `%` → `$`, `[+stress]` on segments | ADR-0013 applier-neutral YAML vs ASCA env vocabulary |
| Working line vs persisted fields | `IndexRule.update_rule(normalize_symbols(...))` before split | SoT may not match `raw` or Index HTML |
| “Canonical” cross-applier forms | `∅`, `#`, `_` already shared with ASCA | vs Brassica / future appliers |
| Historical passes | Tickets 22, 55, 107, 108 wrote ASCA env strings at parse | Retrofit vs grandfather |

## Out of grill scope (separate tickets)

- **Module placement** → [150](150-grill-parse-compile-module-seams.md).
- **Compile diagnostic dump** → [151](151-grill-validate-rules-asca-rules-yaml-diagnostic.md).
- **Inventory `ok` encoding** → [152](152-grill-inventory-ok-column-string-enum.md).
- **Structured `IndexContext` compile projection** — baseline already decided in [139](139-grill-parse-indexrule-model-and-surface-normalization.md) / [144](144-implement-indexcontext-compile-resolution.md); this grill decides **what may still be ASCA-shaped in strings** before compile.

## Deliverable

Decision table: **token or transform** → **SoT allowed?** → **if not, target** (Index surface / structured YAML / compile-only). Feeds [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) and implementation tickets 140–144.
