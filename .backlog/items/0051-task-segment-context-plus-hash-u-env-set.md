Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Split segment env context from `position.in` `#U` and compile to ASCA env sets.
Blocked by:

## Problem Statement

Compound Index envs such as `O_ in #U` (Blackfoot-e_2) need a **segment neighbour** (`O_`) and a **word-initial syllable** (`#U`) at once. Compile today rewrites `in #U` to ` #<(..)_(..)>` in place, producing `O_  #<(..)_(..)>` with two incompatible underscores ([0039](../spikes/0039-index-syllable-position-u-hash.md) mechanical `#U` pass vs segment `_`).

Structured **`IndexContext`** can express `context: O_` and `position.in: #U` ([ADR-0017](../../docs/adr/0017-structured-env-exception-indexcontext.md)), but parse does not split `O_ in #U` from scalar env strings, `#U` is not a classified `position.in` target, and materialize joins classified syllable edges as `context in #<(..)_(..)>`, not `:{context, #<(..)_(..)>}:`.

## Description

**Represent** rules whose env is `«structural» in #U` / `«structural» in U#` (optional editorial `in`) as structured YAML:

```yaml
env:
  context: O_
  position:
    in: "#%"   # or "#U" once classified; Index syllable boundary token
```

**Parse (ingest):** Extend [`extract_position_from_context`](../src/conlanger/ingest/utils/index_context_position.py) / [`apply_index_context_position_extraction`](../src/conlanger/ingest/parser.py) so when `context` matches a **left-hand structural fragment** (segment template ending in `_`, neighbour host, or similar) followed by `in (#U|U#|#%|%)`, split into `context` + `position.in` target. Regenerate or correction-pass at least **Blackfoot-e_2** and **Old-Norse-waː-naː** (`%u in #U`).

**Compile:** When materializing `IndexContext` with non-empty `context` whose focus already contains `_` (or is otherwise segment-scoped) and classified `position.in` is a **mechanical syllable-at-word-edge** projection (`#<(..)_(..)>`, `<(..)_(..)>#`, and optionally stressed monosyllable `#<(..)_(..)>#`), emit an **environment set** `:{left, right}:` instead of `left in right`. Extend [`resolve_index_context_to_string`](../src/conlanger/compile/project_index_context.py) and/or [`project_position_in_compiled_field`](../src/conlanger/compile/tools/asca/syllable_position.py) so string envs that still arrive as `O_ in #U` get the same env-set shape before validation. Classify **`#U`** on `position.in` like `#%` in [`project_position_in_target`](../src/conlanger/compile/position_in_projection.py) (or normalize at materialize).

**In scope rule keys (initial):** Blackfoot-e_2, Old-Norse-waː-naː.

**References:** [0045](../spikes/0045-expected-underscore-syllable-compile-review.md) (compound env), [0048](0048-task-env-set-syllable-tail-projection.md) (env-set syllable tails), `tests/conlanger/tools/ingest/test_transforms.py`, `tests/conlanger/utils/test_syllable_position.py`.

**Out of scope:** Prose tails after `#U` (`in #U before a U with …`); exception-only `#U`; changing ASCA; bulk YAML regen of entire corpus unless needed for in-scope keys.

## Acceptance Criteria

- [ ] `Blackfoot-e_2` in `index_diachronica.yml` uses structured `env` with `context` + `position.in` for `#U` / `#%` (not scalar `O_ in #U`).
- [ ] `Old-Norse-waː-naː` structured likewise (`%u` / syllable host + `position.in` edge).
- [ ] Compile emits validated env shape for Blackfoot-e_2 equivalent to `:{O_, #<(..)_(..)>}:` (or ASCA-approved variant); inventory row passes `validate_rules` or failure is documented in **Comments** with a single explicit blocker.
- [ ] Unit tests cover parse split, materialize env-set, and full `compile_asca_rule_fields` for both representatives.
- [ ] [`sound-change-applier.md`](../../docs/system/sound-change-applier.md) notes segment context + `position.in` `#%` → env set when context already carries `_`.
- [ ] `uv run check` passes; **`Status: resolved`**; sync plan **Tasks** table.

## Comments
