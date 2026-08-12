Type: task
Status: needs-triage
Blocked by: None

# Correction pass: flatten nested sets in env / exception

Target cluster: `nested_brackets` — nested `{…}` in **env** or **exception** only (~16 inventory rows at 2026-08-12 baseline).

Spawned from [spike 67](67-spike-nested-sets.md). Findings: [nested-sets-inventory.md](../research/nested-sets-inventory.md) §4.2–4.4.

## Problem

Index encodes env/exception alternations with nested braces, e.g.:

- `_ə{(C){p,kʷ},m,w}` (`index_diachronica_original.html:1903`)
- `_{s,({m,j,w})V}` (`index_diachronica_original.html:5509`, `:5510`)
- `{{C[-fr,+bk,-hi,-lo],K}ʷ,w}_` (`index_diachronica_original.html:11552`)

ASCA 0.10.2 rejects nested `{}` of the same bracket type at lex time (`NestedBrackets`).

## What to build

1. Compile-time flatten for env/exception fields (mirror ticket [23](23-correction-pass-labialized-class-letters.md) set flattening).
2. Expand common shapes: `({m,j,w})V` → `{mV,jV,wV}`; one-level union flatten `{a,{b,c}}` → `{a,b,c}` when semantically safe.
3. TDD on representative inventory lines; full regen + metrics.

## Policy

- ADR-0010: no valid-but-inaccurate rewrites; preserve `raw`.
- YAML `env` / `exception` may change at compile emission only, or via parse-time normalizer if already used for env — follow [asca-compile-transform-order.md](../research/asca-compile-transform-order.md).

## Acceptance criteria

- [ ] Handler + tests on §4.2–4.4 examples from research
- [ ] Full inventory re-baseline; `nested_brackets` count reduced; metrics in **Answer**
- [ ] Residual rows documented (manual_mappings / skip)
