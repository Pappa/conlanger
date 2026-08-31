# Compile fields use a field-token intermediate representation at SoundChangeRule construction

At ASCA compile, each of **input**, **output**, **env**, and **exception** is a pydantic compile-field object (`RuleInput`, `RuleOutput`, `RuleEnv`; exception reuses `RuleEnv`) holding Index-raw text, an ordered **field-token** intermediate representation, and a compiled ASCA string. Alternative detection and structural transforms read field tokens; render joins compiled strings from those objects. YAML **stages** stay opaque ([ADR-0002](0002-applier-neutral-yaml-rule-index.md), [ADR-0011](0011-index-rule-stages.md)). Grill: [ticket 94](../../.scratch/cleaned-rule-index/issues/94-grill-structured-soundchangerule-ir.md).

## Considered Options

- **String-only compile (status quo after [ADR-0014](0014-per-field-asca-compile.md))** — alternatives and parallel rules detected via regex on field strings; `(ː)` optional length fights transform order.
- **Full syntax tree now** — one recursive AST for all Index notation before implementation; high design cost and long blocking refactor.
- **Phased field-token v1 (chosen)** — ordered tuple of field tokens per compile field (singleton or ordered brace set); rule-level zip for parallel alignment; optional-length node; richer tree and ticket 71 shapes deferred to v2 / string layer.

## Field-token v1

- **Field token:** one top-level unit after splitting on spaces outside groupers — either a singleton opaque string or an ordered set of brace members (not a Python `set`).
- **Parallel tokens:** multiple field tokens on one compile field, aligned by index with the other side (e.g. `c ɲ > ∅ n`).
- **Optional outputs:** one output field token that is an ordered set while input is not “one field token that is an ordered set.”
- **Optional-length `(ː)`:** dedicated node expanding to ordered alternation `{segment, segment:[+long]}` (matrix/template analogues) before suffix `length_marks` ([ticket 104](../../.scratch/cleaned-rule-index/issues/104-correction-pass-parenthesized-optional-length-marker.md)).

## Consequences

- **Alternatives** stay on `SoundChangeRule`; detection moves from string gates to field-token structure ([tickets 66](../../.scratch/cleaned-rule-index/issues/66-implement-optional-outputs-alt-idx.md), [81](../../.scratch/cleaned-rule-index/issues/81-correction-pass-parallel-output-null.md)).
- **Transforms:** hybrid v1 — walk field tokens for parallel/null/set/optional-length paths; other passes may stringify → existing function → reparse until migrated.
- **Render:** each compile field renders its intermediate representation to a compiled ASCA string; `__str__` joins four compiled strings (extends [ticket 99](../../.scratch/cleaned-rule-index/issues/99-compiled-fields-join-at-render.md)).
- **Tests:** structure assertions for token shape and alternative fan-out plus golden `.rsca` on representative rules.
- **Out of v1:** ticket 71 optional-prefix parallel shapes stay on parenthetical / cartesian string layer until a follow-on extends the tree.
- **Implementation:** [ticket 105](../../.scratch/cleaned-rule-index/issues/105-implement-compile-field-intermediate-representation.md).
