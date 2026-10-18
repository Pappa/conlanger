Type: task
Status: resolved
Blocked by: None

# Task: compile-time ASCA projection for `position.in` and `in <target>` env tails

Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-10-18). Implements spike [173](173-spike-position-in-asca-compile-projection.md). **Compile only** — do not change ingest/parser passes.

## Question

Implement the compile projection chosen in [173](173-spike-position-in-asca-compile-projection.md) so Index **`position.in`** and string env/exception tails **`in <target>`** (including `#U`, `U#`, syllable stress matrices) become **valid ASCA** at compile time, consistently with **`context`** and other **`position`** relations.

## Constraints (owner 2026-10-18)

- **No parse-time code changes** for this ticket.
- **Spike [173](173-spike-position-in-asca-compile-projection.md) chose B2:** one post-materialize env/exception transform in the ASCA field pipeline ([`compile_asca_rule_fields`](../../../src/conlanger/compile/tools/asca/pipeline.py)), implemented by extending [`syllable_position.py`](../../../src/conlanger/compile/tools/asca/syllable_position.py). Do **not** emit ASCA from [`project_index_context.py`](../../../src/conlanger/compile/project_index_context.py) / materialize.
- Reuse ASCA targets from [98](98-correction-pass-syllable-position-u-hash.md) / [`syllable_position.py`](../../../src/conlanger/compile/tools/asca/syllable_position.py) as shared helpers; avoid duplicating `#<.._>` / `<.._>#` tables.
- Do not regress mechanical `#U` / `U#` behaviour resolved in [98](98-correction-pass-syllable-position-u-hash.md).
- **Documented defer / manual** (inventory `defer_or_manual`): see [173 Answer](173-spike-position-in-asca-compile-projection.md#answer-2026-10-18) and findings §3.4–3.6.

## Acceptance

- [x] Compile projection matches [173](173-spike-position-in-asca-compile-projection.md) findings for all in-scope target classes.
- [x] Structured `env` / `exception` with `position.in` round-trip through `uv run compile_rules` to ASCA that passes `validate_rules` (or documented defer for spike-excluded rows).
- [x] String env/exception fields with embedded `in <target>` (no YAML restructure) compile per spike table.
- [x] `context` + `in` composition covered when spike specifies ASCA (future-shaped tests even if corpus has zero rows today).
- [x] Unit tests on compile module(s) touched; update [`docs/system/sound-change-applier.md`](../../../docs/system/sound-change-applier.md) projection table.
- [x] `uv run compile_rules && uv run validate_rules`; record ok delta and ok-changelog if flips; follow [implement-closure.md](../../../docs/agents/implement-closure.md).

## Answer (2026-10-18)

- **B2:** `project_position_in_compiled_field` in [`syllable_position.py`](../../../src/conlanger/compile/tools/asca/syllable_position.py), wired from `apply_syllable_position_compiled_overrides` after ticket 98 mechanical overrides and `project_syllable_stress_compiled_env`.
- **Rewrites:** embedded / comma `in U…` / `in %…` stress tails → ` in $[±stress]`; whole `in U:[+stress]…` / `in %:[+stress]…` → `_ %[+stress]…`; embedded mechanical `in #U` / `in U#` (non-prose) → `#<.._>` / `<.._>#`; prose `#U before/with…` and `U[+lo]` / `U[+hi]` feature matrices unchanged (spike defer).
- **Inventory:** `create_index && compile_rules && validate_rules` — **9274** OK (**+10** vs **9264**); changelog flips: Hittite-V, Hittite-e-o, Luwian-V, Palaic-a-e, Catawba-tʲ, Dakota-tʲ, Mandan-ã, Proto-Čiwere-Winnebago-tʲ, Proto-Dhegiha-tʲ, Proto-Dhegiha-u.

## Out of scope

- Parse extraction of `C_CV in U[-stress]` → structured `context` + `position.in`.
- Retiring [`apply_syllable_position_compiled_overrides`](../../../src/conlanger/compile/tools/asca/syllable_position.py) unless spike requires consolidating duplicate logic (if so, keep behaviour byte-identical for ticket 98 fixtures).

## Related

- [156](156-task-indexcontext-position-in-relation.md) (v1 materialize `in {v}`)
- [173](173-spike-position-in-asca-compile-projection.md) (resolved) · [findings](../research/position-in-asca-compile-projection.md)
