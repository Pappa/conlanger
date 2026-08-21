Type: task
Status: ready-for-agent
Blocked by: 92

# Refactor compile classes to pydantic (per-field transforms)

Grill 2026-08-21 Q8. Re-implement compile assembly in `src/conlanger/tools/rules.py` as **pydantic** models (**latest** pydantic 2.x — `uv add pydantic` when claiming this ticket; owner approved). Target names from the owner: **`DiachronicRuleset`**, **`SoundChangeRule`**, and the other classes in `rules.py`. Transforms run on **input / output / env / exception separately at instantiation**; join is render-time. **Do not claim until [ticket 92](92-grill-pydantic-compile-refactor.md) is resolved** — that grill is the spec.

## Placeholder scope (replace with grill 92 answer)

Until 92 closes, treat this as the owner’s intent, not a license to invent details:

- Pydantic models for every `rules.py` compile type the grill includes.
- Per-field string transforms on instantiation; `__str__` joins already-transformed fields into ASCA.
- Cross-field behaviour (subscript `declared` set, optional-output alternatives, length-1 `stages`) only as 92 decides.
- Keep transform **functions** in `compile/asca/` unless 92 says otherwise; validators call them.
- Skip / missing-arrow behaviour from [89](89-unify-status-skipped.md) / [90](90-missing-arrow-single-stage.md) / `CONTEXT.md`.
- Rename `DiachronicSeries` → `DiachronicRuleset` if 92 confirms; update callers, tests, docs.

## Out of scope unless 92 says otherwise

- Brassica compiler
- Changing corpus YAML (`stages` stays parse SoT)
- Re-ordering transforms contrary to [spike 38](../research/asca-compile-transform-order.md) without an explicit grill decision

## Acceptance criteria

- [ ] Ticket 92 **Answer** is inlined or linked here as the spec before coding
- [ ] `pydantic` is a project dependency via `uv add pydantic` (latest 2.x at claim time)
- [ ] `rules.py` types are pydantic models; compile transforms are not a post-join string pipeline
- [ ] Callers (`validate_asca`, inventory, tests) updated; full gate passes
- [ ] Living docs (`sound-change-applier.md` or successor) match the grilled shape
