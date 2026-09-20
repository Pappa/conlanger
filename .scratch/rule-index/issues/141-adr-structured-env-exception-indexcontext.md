Type: task
Status: ready-for-agent
Blocked by: None

# ADR: structured `env` / `exception` (`IndexContext` YAML)

## Question

Document the applier-neutral YAML shape for rule-level **environment** and **exception** after [139](139-grill-parse-indexrule-model-and-surface-normalization.md).

## Answer (spec for ADR author)

Each of `env` and `exception` is either **absent** or an **`IndexContext`** object:

| Key | Type | Role |
| --- | --- | --- |
| `context` | `str` (optional) | Structural / target Index string (`#_`, `V_C`, `C`, `{S,s,l̥}`, …) when not carried solely under `position` keys |
| `position` | `object` (optional) | Open map: any property name; each value is **`bool` \| `str` \| `list[str]`** (three equally valid forms) |
| `dialect` | **`bool` \| `str` \| `list[str]`** (optional) | Dialect / region scope for this field; inclusive on `env`, exclusive on `exception` by field placement (no extra flag on the type) |

**Examples**

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

**Compile (option A from 139):** YAML stays structured; **compile-time** (or a dedicated resolver step at `SoundChangeRule` construction) projects `position` / `dialect` + `context` to ASCA env/exception **strings**. No neighbour templates baked into YAML as the only representation.

**Supersedes** paused [122](122-grill-proximity-conditions-yaml.md) top-level `position` map + opaque env strings. **Supersedes** rule-level `applicability` from open [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) for dialect (dialect lives on `IndexContext` only).

Amend corpus-rule schema docs ([03 yaml schema](../03-yaml-schema-rule-index.md), `CONTEXT.md` glossary).

## Outcomes

- [ ] ADR committed
- [ ] Glossary + schema ticket/doc updated
- [ ] Migration note: rules with string `env`/`exception` until regen (loader accepts both during transition if needed)

## Related

- [139](139-grill-parse-indexrule-model-and-surface-normalization.md)
- [144 compile resolver](144-implement-indexcontext-compile-resolution.md)
