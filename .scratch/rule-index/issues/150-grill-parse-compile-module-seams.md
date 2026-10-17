Type: grilling
Status: needs-grilling
Blocked by: 148, 149

# Grill: parse vs compile package seams and shared utilities

Spawned from wayfinder session 2026-10-17. Owner input: **general utils** used by both stages are fine, but **compile-time logic** has landed in **parse** modules (e.g. `resolve_rule_env_exception_for_compile` in `ingest/models/index_models.py`, `compile.tools.asca` imports from `ingest/utils/transforms.py`).

## Question

Where should the **parse ↔ compile** boundary live in `src/conlanger/` (packages, modules, and public entrypoints) so that:

1. Parse loads HTML → applier-neutral YAML without importing ASCA compile transforms except shared pure helpers.
2. Compile + `validate_rules` own ASCA projection, env-set construction, and materialization (`materialize_index_rule_env_exception`, group mappings, etc.).
3. Shared code (`symbols`, gloss, IO) stays neutral and dependency direction is **ingest → (no compile)** and **compile → ingest models** only where unavoidable.

## Concrete relocations to decide

| Symbol | Today | Candidate home |
| --- | --- | --- |
| `resolve_rule_env_exception_for_compile` | `ingest/models/index_models.py` | `compile/resolve_index_rule.py` or dedicated resolver module |
| `resolve_index_context_to_string` / position templates | `ingest/models/index_models.py` | compile-side projection |
| `strip_editorial_in_before_syllable_position` import | parse `transforms.py` from `compile.tools.asca` | parse-only strip vs compile-only |
| `ingest/utils/mappings.py` ASCA feature targets | ingest | compile config application only? |

## Depends on

[148](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) and [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) — module moves follow what parse vs compile **owns**.

## Deliverable

Target module graph (one diagram or table), list of **allowed** cross-imports, and whether `index_models` stays parse-only Pydantic or splits into `ingest` + `compile` DTOs.
