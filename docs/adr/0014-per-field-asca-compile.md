# ASCA compile transforms run per field at SoundChangeRule construction

The applier-neutral index stays Index-shaped YAML (**stages**, optional env/exception). The ASCA **applier compiler** applies string transforms to **input**, **output**, **env**, and **exception** separately when constructing `SoundChangeRule`, then joins those already-compiled fields only when rendering `.rsca` text. That replaces join-then-rewrite on a single rule string. Grill: [ticket 92](../../.scratch/cleaned-rule-index/issues/92-grill-pydantic-compile-refactor.md). Implementation: [ticket 93](../../.scratch/cleaned-rule-index/issues/93-pydantic-compile-refactor.md).

## Considered Options

- **Join then rewrite (previous)** — matches `.rsca` layout; transforms can accidentally see separators; subscript expansion had to split the blob back into fields.
- **Per-field at instantiation (chosen)** — each field is a compile seam; join is render-only. Cross-field work (shared subscript `declared` set; optional-output / parallel-∅ alternatives) stays explicit on `SoundChangeRule`.

## Consequences

- `DiachronicSeries` still maps one **sound-change section** to compiled parts and expands **stages** into adjacent pairs. It does not detect **optional outputs**.
- Alternatives stay on `SoundChangeRule` (split raw I/O, then compile each peer). Inventory keeps reading `.alternatives`.
- Transform **functions** remain in `compile/asca/`; pydantic validators on the compile models orchestrate them (may change later).
- Brassica remains deferred ([ADR-0001](0001-sound-change-applier-backends.md)). Spike-38 transform **order** still applies per field unless a later grill changes it.
