# Structured `env` and `exception` as `IndexContext` in the rule index

Rule-level **environment** and **exception** in the applier-neutral index may be represented as structured **`IndexContext`** objects in YAML and in the parse-time **`IndexRule`** model ([ticket 142](../../.scratch/rule-index/issues/142-implement-indexrule-pydantic-and-yaml-schema.md)), not only as opaque Index-shaped strings.

Each of `env` and `exception` is either **absent** or an **`IndexContext`**:

| Key | Type | Role |
| --- | --- | --- |
| `context` | `str` (optional) | Structural / target Index material (`#_`, `V_C`, `C`, `{S,s,l̥}`, …) when not carried solely under `position` keys |
| `position` | `object` (optional) | Open map: any property name; each value is **`bool` \| `str` \| `list[str]`** |
| `dialect` | **`bool` \| `str` \| `list[str]`** (optional) | Dialect / region scope for this field |

Inclusive vs exclusive semantics for position and dialect come from **whether the object is on `env` or `exception`**, not from extra flags on `IndexContext`.

**Compile (option A from grill 139):** YAML stays structured; at **compile** (or a dedicated resolver when constructing `SoundChangeRule`) `position`, `dialect`, and `context` project to applier env/exception **strings** ([ticket 144](../../.scratch/rule-index/issues/144-implement-indexcontext-compile-resolution.md)). Neighbour templates (e.g. `C_, _C`) are not the only YAML representation.

Illustrative YAML:

```yaml
env:
  context: "#_"
  position:
    adjacent_to: C
  dialect: northern

env:
  position:
    adjacent_to:
      - N
      - V
    medial: true
  dialect:
    - west
    - gascon
```

Supersedes paused [ticket 122](../../.scratch/rule-index/issues/122-grill-proximity-conditions-yaml.md) top-level `position` map plus opaque env strings for schema shape. Supersedes rule-level `applicability` from [ticket 123](../../.scratch/rule-index/issues/123-grill-applicability-dialect-sporadic-conditions-yaml.md) for dialect (dialect lives on `IndexContext` only). Corpus inventory lists in those tickets remain input to normalisation and compile work.

## Considered Options

- **Opaque strings only in YAML (previous)** — simple for compile; proximity and dialect stay in prose, manual mappings, or regex extractors.
- **Structured `IndexContext` in YAML + compile-time string projection (chosen)** — applier-neutral conditioning without ASCA syntax in the index; compile boundary unchanged in spirit ([ADR-0014](0014-per-field-asca-compile.md)).
- **Parse-time expansion to neighbour templates in YAML** — rejected for v1; keeps YAML relation-shaped and defers template expansion to compile/resolver.

## Consequences

- Schema docs and `CONTEXT.md` describe `env` / `exception` as `str` **or** `IndexContext` during migration; existing corpus rows may keep string form until regen.
- Loader and compile accept both shapes during transition where implemented ([142](142-implement-indexrule-pydantic-and-yaml-schema.md), [144](144-implement-indexcontext-compile-resolution.md)).
- Terminology: YAML key **`position`** on `IndexContext`, not a separate top-level `position: {env?, exception?}` map from ticket 122.
