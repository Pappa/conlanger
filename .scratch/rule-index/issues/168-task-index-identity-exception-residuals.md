Type: task
Status: ready-for-agent
Blocked by:

# Task: `! Host =` identity exception residuals (Family B strip + env-infer)

Spawned from [Grill: `! Host =` env-slot exception compile (suffix policy + residuals)](167-grill-index-identity-exception-env-splice.md) (2026-10-17). Builds on [Correction pass: Index identity exceptions (`! Host = seg`)](128-correction-pass-index-identity-exceptions.md).

## Question

Fix compile gaps so rules with Index `! Host = RHS` stop emitting invalid ASCA `// Host = RHS` tails after Family B input narrowing, and recover additional mechanical ok-flips where env implies the host slot (e.g. `_#` + `C = t` on input `C`) without prose/disjunction rewrites.

## Acceptance

- [ ] When Family B narrows input, compiled `exception` is empty / omitted (no `// Host = RHS` left for ASCA to parse).
- [ ] Inventory re-run: delta on `expected_number` cluster and ok count documented in **Answer**; list remaining prose/disjunction/Cn rows as hold-outs per grill 167.
- [ ] Unit tests for Anejom-C-shaped rules and any newly fixed ids.
- [ ] No parse-time rewrite of YAML `exception` (ADR-0010).

## Out of scope

- Prose tails (`or when reduplicated`, `unless …`, `and/or`), disjunction (`or one C =`), compound `Cn` + `V_V` without a C slot — manual/overlay unless a future grill expands policy.
- Bare matrix exceptions without `Host =` — [119](119-grill-distinctive-features-env-exception.md).
- Compiled-YAML → `DiachronicSeries` round-trip false failures (`// Host = RHS` after Family B) — [169](169-task-validate-compiled-yaml-without-series-roundtrip.md).
