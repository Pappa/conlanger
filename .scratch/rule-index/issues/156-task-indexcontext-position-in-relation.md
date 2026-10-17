Type: task
Status: ready-for-agent
Blocked by: None

# Task: compile projection for `IndexContext.position.in`

Spawned from triage when closing [143](143-implement-index-rule-normalisation-passes.md) / [144](144-implement-indexcontext-compile-resolution.md) (2026-10-17). Parse already emits `position.in` for some rules; compile ignores it.

## Question

Index env prose **`in <target>`** (syllable position, feature matrix, segment set, …) is partially normalized at parse to structured **`position.in`**. How should compile project that relation to ASCA env/exception strings — consistently with [144](144-implement-indexcontext-compile-resolution.md) neighbour templates and mechanical `#U` / `U#` handling from [98](98-correction-pass-syllable-position-u-hash.md)?

## Current state

| Layer | Status | Detail |
| --- | --- | --- |
| **Parse** | Partial | [`index_context_position.py`](../../../src/conlanger/ingest/utils/index_context_position.py) treats `in` like `adjacent_to` / `near` for **whole-field** `context` (`^in\s+<target>$`). Wired at parser D6 after feature/IPA on `context`. |
| **Corpus** | Mixed | ~**38** rules with YAML `position.in`; many env strings still embed `… in U[…]` inline (not yet split into `context` + `position`). |
| **Compile** | Missing | [`resolve_index_context_to_string`](../../../src/conlanger/ingest/models/index_models.py) projects only `adjacent_to` and `near`; **`in` is dropped**, which can yield empty compile env for neighbour-only rows. |
| **Config** | Missing | [`compiler_config.yml`](../../../config/compile/asca/compiler_config.yml) `position_templates` has no `in` key. |
| **Tests** | Parse only | [`test_transforms.py`](../../../tests/conlanger/tools/ingest/test_transforms.py) (`in U#` → `position.in`); no compile round-trip for `in`. |

**Do not confuse** with dialect manual rows (`in … dialects` in [`manual_mappings.yml`](../../../config/parser/manual_mappings.yml)) — those are separate from syllable/segment **`in <phonology target>`**.

## Answer (direction for implementer; grill if templates disagree)

1. **Relation semantics** — Decide per target class:
   - Mechanical `#U` / `U#` (and comma lists): prefer reusing or calling into existing syllable-position compile ([`syllable_position.py`](../../../src/conlanger/ingest/utils/syllable_position.py) / compile overrides from ticket 98), not a naive `{v}_, _{v}` neighbour template.
   - Segment / matrix / set targets (`U[+hi]`, `{ħ,ʕ}`, …): relation-keyed template and/or structural `context` merge (same comma-join policy as 144).
2. **Config** — Extend `position_templates.in` (or document hardcoded syllable branch) in `compiler_config.yml`; defaults must not regress inventory on the ~38 migrated rules.
3. **Parse follow-on (optional same PR)** — Inventory-driven extraction for **embedded** `in <target>` tails on non-empty `context` (e.g. `C_CV in U[-stress]`), aligned with 143 extraction style; defer ambiguous prose to `manual_mappings` / comments.

## Acceptance

- [ ] `resolve_index_context_to_string` / `resolve_rule_env_exception_for_compile` project `position.in` (and `context` + `in` together) to ASCA env strings.
- [ ] `position_templates` (or documented syllable delegate) in `compiler_config.yml`; loader tests updated.
- [ ] Unit tests: at least `in U#`, `in U[+hi]`, and `context` + `in` merge; inventory rule-id fixture if available.
- [ ] `docs/system/sound-change-applier.md` compile projection table includes `position.in`.
- [ ] `uv run validate_rules`: no ok-count regression vs current baseline; changelog note if regen required.

## Out of scope

- Dialect scope `in … dialects` (manual mappings / `IndexContext.dialect`).
- Full audit of all legacy env regex passes ([149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md)).

## Related

- [143](143-implement-index-rule-normalisation-passes.md) (neighbour/medial extraction v1; `in` added in code but not ticket table)
- [144](144-implement-indexcontext-compile-resolution.md) (neighbour/medial compile v1)
- [98](98-correction-pass-syllable-position-u-hash.md) (`#U` / `U#` ASCA emission)
- [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) (parse-time ASCA-shaped env cleanup)
