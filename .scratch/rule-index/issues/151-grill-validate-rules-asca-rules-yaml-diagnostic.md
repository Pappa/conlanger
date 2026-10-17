Type: grilling
Status: resolved
Blocked by: 148

# Grill: `validate_rules` compile diagnostic `diagnostics/compile/asca_rules.yml`

Spawned from wayfinder session 2026-10-17. Owner input: after validation, emit a **debug/monitoring** artifact with compiled ASCA syntax per rule (not a new SoT).

## Question

Specify the **`diagnostics/compile/asca_rules.yml`** contract: path, lifecycle (always on `validate_rules` vs flag), ordering, and per-rule payload when compile yields alternatives, skipped rules, or partial field blame.

## Proposed shape (owner draft — lock or amend)

```yaml
sections:
- section: Afro-Asiatic
  index: 6
  rules:
  - rule_id: Proto-Omotic-dz-ʃ-tʃ
    rule: dz ʃ tʃ > ʒ F F
```

Clarify:

- **`rule` string** — full `SoundChangeRule.__str__()` / `.rsca` line, per-stage lines for multi-stage index rules, or one row per compile-expanded pair?
- **`index`** — section number from parsed YAML (type, stability across regen).
- **Skipped** (`status: skipped`) and **section skipped** — omit, include with sentinel, or separate file?
- **Failed compile** — omit rule, include last good string, or error stub?
- **Relation to** `diagnostics/inventory/` CSVs and [103 split](103-split-create-index-and-validate-rules.md) (parse diagnostics under `diagnostics/parse/` only today).

## Depends on

[148](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) — diagnostic strings are **ASCA compile output**; grill confirms that is the intended reader audience.

## Deliverable

Locked YAML schema + operator doc blurb; implementation can be a follow-on **task** ticket.

## Answer

**Resolved 2026-10-17** (owner grill). Compile-stage **debug/monitoring** artifact — **not** SoT ([148](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md)). Implementation: ~~[159](159-task-write-compile-asca-rules-yml.md)~~ **resolved**. Validation stability: ~~[158](158-task-inventory-validate-all-compile-targets.md)~~ **resolved**. Steady-state pipeline: [160](160-grill-split-compile-rules-and-compiled-yaml-pipeline.md) → ~~[161](161-task-split-compile-rules-and-validate-compiled-yaml.md)~~ **resolved** (2026-10-17).

### Purpose and lifecycle

| Topic | Policy |
| --- | --- |
| Audience | Operators / agents inspecting **ASCA compile output** after validate ([ADR-0013](../../docs/adr/0013-parse-compile-validate.md)). |
| Path | `diagnostics/compile/asca_rules.yml` (parallel to `diagnostics/parse/` and `diagnostics/inventory/`). |
| When | Default **on** every `validate_rules` run; **`--no-write-compiled-rules`** (or equivalent) to skip (smoke / `--limit`). |
| Coverage | Emit compiled lines for **every** index rule whether compile validation passes or fails. |

### Top-level shape

No run metadata (`generated_at`, `source_yaml`). Root is **`sections:`** with the **same section objects** as cleaned index YAML (`section`, `index`, `rules`).

```yaml
sections:
- section: North Frisian Lenition
  index: 17.7.2.1.15
  rules:
  - rule_id: North-Frisian-Lenition-p-t-k
    valid: true
    rule: p t k > f s x
```

(`rule` values are compiled ASCA field-join strings — no leading tab; active `.rsca` lines add `\t` separately.)

### Per-rule fields

| Field | When | Value |
| --- | --- | --- |
| `rule_id` | always | Same as cleaned index. |
| `valid` | compile attempted | `true` only if **every** nested compile target for that index rule validates; otherwise `false` (see shapes below). |
| `rule` | **single-form** success | One compiled ASCA line (**string**). Mutually exclusive with `alternatives` / `steps`. |
| `alternatives` | optional-output fan-out | List of `{rule, valid}` — one entry per `alt_idx` branch. |
| `steps` | multi-stage chain | List of `{rule, valid}` — one entry per `expand_chained_index_rule` step. |
| `status` | skipped / sporadic compile skip | `skipped` (config hold-out) or compile-skipped sporadic/dialect sample — per current `SoundChangeRule.__str__()` (`#\t…`). |
| `compile_error` | `format_error` / no series | Message; `valid: false`; omit `rule` / `alternatives` / `steps`. |

**Amended 2026-10-17:** a flat `rule: [string, …]` cannot record which branches pass compile validation. Use **single-form** vs **multi-form** shapes instead.

#### Single-form (one compiled ASCA line)

One compile target: single-stage rule with no optional-output fan-out.

```yaml
- rule_id: North-Frisian-Lenition-p-t-k
  valid: true
  rule: p t k > f s x
```

#### Multi-form — optional-output alternatives

When compile emits multiple **alternative** branches (inventory `alt_idx` fan-out). **No** top-level `rule` key.

```yaml
- rule_id: North-Frisian-Lenition-p-t-k
  valid: false
  alternatives:
  - rule: x > y / _
    valid: true
  - rule: x > y / bad rule
    valid: false
```

Top-level **`valid`** = logical **AND** of each alternative’s `valid` (`true` only if all alternatives validate).

#### Multi-form — adjacent `stages` chain

When compile expands to multiple **steps** (no optional-output fan-out on that index rule). **No** top-level `rule` key.

```yaml
- rule_id: Proto-Omotic-dz-ʃ-tʃ
  valid: true
  steps:
  - rule: dz > ʃ
    valid: true
  - rule: ʃ > tʃ
    valid: true
```

Top-level **`valid`** = **AND** of each step’s `valid`. Order matches compile step order; env/exception repeat per step when compile propagates them.

Today’s compile model does not combine chain multi-step with optional-output fan-out on the same index rule; if it ever does, extend with a follow-on grill.

### Skipped and errors

| Case | YAML |
| --- | --- |
| Section `status: skipped` | Omit section (inventory bypass). |
| Rule `status: skipped` | Include row: `status: skipped`, `rule: "#\t{raw}"` (exact compiler comment line). |
| Sporadic/dialect sampled out | Include row matching compiler comment-line behaviour (`#\t` + compiled fields). |
| Compile failure before series | `valid: false`, `compile_error`, no `rule`. |

Pass/fail taxonomy and clustering remain in **`diagnostics/inventory/`**; no per-field blame in this file (`--field-isolation` unchanged).

### Ordering

Same order as parsed YAML: `sections` order, `rules` order within section. `index` is a **string** (matches inventory `section_index`).

### Follow-on tasks

- ~~[159](159-task-write-compile-asca-rules-yml.md)~~ — writer + doc blurb (**resolved**); v1 split → ~~[161](161-task-split-compile-rules-and-validate-compiled-yaml.md)~~ **resolved**.
- [158](158-task-inventory-validate-all-compile-targets.md) — deterministic validation for all compile-expanded targets (owner: alternative `ok` flip-flop).
