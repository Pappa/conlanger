Type: grilling
Status: needs-grilling
Blocked by: 148

# Grill: parse-time ASCA env/exception strings vs structured `IndexContext`

Spawned from wayfinder session 2026-10-17. Owner input: **ASCA environment sets** (boundary templates, feature matrices in env, `//` exception tails, prose-position encodings) are still created or rewritten during **parse**; they should move to **compile-time** where possible, which may require new **parse-time representations** (structured `position`, relation templates, exception scopes) instead of ASCA literals in `context`.

## Question

Which parse passes must stop emitting **ASCA env/exception strings** into applier-neutral YAML, and what **Index-shaped or structured** representation replaces each shape until [144](144-implement-indexcontext-compile-resolution.md) projects to ASCA?

## Anchors in current code

- Prose position → ASCA literals (`U#`, `%[-stress]`, `#_[+stress]`, `V_V`, …): `ingest/utils/prose_position_env.py` (ticket 107).
- `//` env shorthand and exception tails: `ingest/utils/double_slash_env.py` (ticket 108).
- Medial pairing → `#_, _#` exception: `resolve_rule_env_exception_for_compile` + `MEDIAL_BOUNDARY_EXCEPTION` in `ingest/models/index_models.py` (compile hook today, constant lives in parse utils).
- Stress env prose → `_ when stressed` patterns: `transform_fields.normalize_stress_conditions` (ticket 22).
- Syllable-position editorial strip importing **compile** module: `ingest/utils/transforms.py` → `compile.tools.asca.syllable_position`.

## Depends on

[Grill: ASCA-shaped syntax in the applier-neutral rule index](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) — without a SoT syntax policy, “move to compile” is ambiguous.

## Deliverable

Per-pass **keep at parse / defer to compile / retire** with target schema; ordered migration notes (inventory regression strategy, `raw` unchanged per ADR-0010).
