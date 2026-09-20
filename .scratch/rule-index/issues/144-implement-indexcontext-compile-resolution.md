Type: task
Status: ready-for-agent
Blocked by: 141, 142

# Compile: resolve `IndexContext` to ASCA env/exception strings

## Question

Minimal compile-time changes so validation/render work when corpus YAML uses structured `env` / `exception` per [141](141-adr-structured-env-exception-indexcontext.md).

## Answer

- At **`SoundChangeRule`** construction (or single choke point loading index rules), coerce `IndexContext` → env/exception **strings** for existing per-field compile pipeline.
- **Position resolver v1:** map `position.adjacent_to`, `medial`, `penult`, `near`, … to compiled neighbour / boundary shapes (config table may start hardcoded; `context_resolution.yml` follow-on from 122 deferrals).
- **Dialect resolver v1:** no render gating in first slice unless owner scopes it — structure preserved in YAML; compile may ignore `dialect` until [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) render policy is re-grilled for compile gating.
- Loader accepts **legacy string** `env`/`exception` during transition.

## Acceptance

- [ ] Coercer + tests for 141 examples (`adjacent_to: C` → `C_, _C` or project policy)
- [ ] `uv run validate_rules` on regen index without regressions beyond expected schema migration
- [ ] Document resolver in [sound-change-applier.md](../../../docs/system/sound-change-applier.md)

## Related

- [139](139-grill-parse-indexrule-model-and-surface-normalization.md)
- [122](122-grill-proximity-conditions-yaml.md) (compile table items deferred here)
