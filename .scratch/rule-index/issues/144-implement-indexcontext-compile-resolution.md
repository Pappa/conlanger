Type: task
Status: ready-for-agent
Blocked by: 141, 142, 143

# Compile: resolve `IndexContext` to ASCA env/exception strings

## Question

When corpus YAML carries structured `env` / `exception` (`IndexContext` with `context`, `position`, `dialect`), how does compile project to the existing per-field ASCA pipeline — including **relation-keyed templates** and **medial** boundary behaviour?

## Answer

### Choke point

At **`SoundChangeRule`** construction (or single loader coercer used today via `env_exception_input_to_string`), project each `IndexContext` to the **string** consumed by `RuleEnv` / existing compile transforms.

### Relation-keyed templates (`compiler_config.yml`)

Add defaults under `config/compile/asca/compiler_config.yml` (schema TBD in implementation; YAML shape agreed here):

```yaml
position_templates:
  adjacent_to: "{v}_, _{v}"
  near: "{v}_, _{v}"
```

- **`{v}`** is the target taken from `position.adjacent_to` / `position.near` (string or first element of a list). After [143](143-implement-index-rule-normalisation-passes.md), neighbour-only rules often have **no `context`** (target lives only under `position`). When both are present, `context` must be **structural or qualifier material**, not a repeat of the neighbour target.
- If **`near`** template is omitted, use **`adjacent_to`** template (same projection).
- **Medial (v1):** no format string in v1 — hardcoded compile policy matching today’s parse outcome: when `position.medial` is true on **env** and the rule has no **exception** field, emit compiled env `_` and compiled exception `#_, _#` (today `MEDIAL_BOUNDARY_EXCEPTION`). Do not store `#_, _#` in index YAML from parse. Rules that already have an `exception` `IndexContext` keep owner semantics (known gap from [122](122-grill-proximity-conditions-yaml.md); do not silently drop medial).

### `context` + `position` together

When both are present (e.g. structural env + neighbour relation), resolver **merges** to one ASCA env string per field; v1 must not “context wins, ignore position” (fix `resolve_index_context_to_string` TODO).

### Dialect

Structure preserved in YAML; no render gating in v1 unless owner re-opens [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md).

### Legacy strings

Loader continues to accept scalar `env` / `exception` during transition.

## Acceptance

- [ ] `position_templates` (or equivalent) in `compiler_config.yml` with defaults above; overridable per relation key.
- [ ] Resolver tests: `adjacent_to: C` → `C_, _C`; `near: C` → same by default; `medial: true` → env `_` + exception `#_, _#` per policy.
- [ ] `context` + `position` merge covered by tests aligned with [143](143-implement-index-rule-normalisation-passes.md) examples.
- [ ] `uv run validate_rules` with regen index: no ok-count regression vs pre-143/144 baseline for the migrated relation set.
- [ ] Document resolver in [sound-change-applier.md](../../../docs/system/sound-change-applier.md).

## Related

- [139](139-grill-parse-indexrule-model-and-surface-normalization.md)
- [143 parse extraction](143-implement-index-rule-normalisation-passes.md)
- [122](122-grill-proximity-conditions-yaml.md) (compile table deferrals)

## Comments

- 2026-10-11: Templates relation-keyed; named presets (e.g. `ADJACENT_TO`) deferred. Blocked on 143 for structured YAML input.
