Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: How compile selects single-path vs validate fan-out, and v4 structured fields in `asca_rules.yml`.
Blocked by:

## Question

How should **`compile_rules`** support both **stochastic single-path** compile (pipeline / ML) and **validate/diagnostics fan-out**, and what **on-disk rule shape** should `asca_rules.yml` use for decomposed ASCA fields?

## Answer

### One pipeline

`compile_rules` → `iter_compiled_index_rules` → `DiachronicSeries` / `SoundChangeRule` (rename from legacy “bundle” names in [0054](0054-task-compile-rules-sample-mode-v4-schema.md)). No separate ML export or CSV. Output remains [`asca_rules.yml`](../../diagnostics/compile/asca_rules.yml) with **`schema_version: 4`** (decomposed fields — see below).

### No default YAML

- If **`--compiler-config`** is **omitted**, **do not load** any compiler YAML. Build config from **`CompilerConfig()`** Pydantic defaults only (plus any CLI scalar overrides per [0055](0055-task-compiler-config-merge-and-seed.md)).
- **Validate** and **pipeline** profiles both require an **explicit** `--compiler-config <path>` when file-backed settings are wanted.
- There is **no** `--sample` flag.

### `sample_alternatives` (replaces fan-out / `--sample` idea)

Add **`sample_alternatives: bool`** on `CompilerConfig` (CLI-overridable when [0055](0055-task-compiler-config-merge-and-seed.md) scalar merge applies).

| Value | Meaning |
|-------|---------|
| **`true`** | Stochastic **single path**: respect `randrange` picks; do **not** expand full `part.alternatives` in `resolve_inventory_targets`. |
| **`false`** | **Validate fan-out**: enumerate optional branches and composed chain paths (current `resolve_inventory_targets` behaviour). |

- **Pydantic default:** **`true`** (bare `compile_rules` = pipeline-style single path).
- **Validate profile** ([`config/compile/asca/compiler_config.yml`](../../config/compile/asca/compiler_config.yml)): set **`sample_alternatives: false`** so inventory keeps one row per expanded target.  
  _(Q1 named `true` for this file; fan-out requires **`false`** here.)_

### Sporadic and dialect (Q4)

Independent of `sample_alternatives`:

| Knob | Validate YAML (`sample_*: false`) | Pipeline (defaults or pipeline YAML) |
|------|-----------------------------------|--------------------------------------|
| **Sporadic / dialect prose on index rules** | Rules **always apply** (normal compiled line; no random skip). | **`sample_sporadic` / `sample_dialect` true** (class defaults when omitted): 50% apply, 50% skip. |
| **When skipped** | N/A | `compile_skipped` in YAML with `#\t…` line ([`compiled_rule_entry`](../../src/conlanger/tools/compiled_rules_yaml.py)). |

Fan-out vs single-path is **`sample_alternatives`**; whether sporadic rules randomly drop out is **`sample_sporadic` / `sample_dialect`**.

### Config files

| File | Role |
|------|------|
| [`config/compile/asca/compiler_config.yml`](../../config/compile/asca/compiler_config.yml) | Validate/diagnostics: `sample_alternatives: false`, `sample_sporadic: false`, `sample_dialect: false`, `seed: 0`, full **`position_templates`** and **`series_mappings`** (and existing keys). |
| [`config/pipeline/compiler_config.yml`](../../config/pipeline/compiler_config.yml) | Pipeline/ML: **duplicate** `position_templates`, `series_mappings`, and sidecar layout (e.g. `group_mappings.yml` beside each file per current loader); omit `sample_*` to use class defaults (**true**); `sample_alternatives: true` or omit. |

No shared-mapping loader indirection for now — **duplicate** mapping sections in both YAML trees ([0054](0054-task-compile-rules-sample-mode-v4-schema.md)).

### Operators

```bash
# Pipeline-style (defaults only, no YAML)
uv run compile_rules

# Pipeline-style (explicit file)
uv run compile_rules --compiler-config config/pipeline/compiler_config.yml

# Validate inventory path
uv run compile_rules --compiler-config config/compile/asca/compiler_config.yml
uv run validate_rules
```

Document in [compile-rules.md](../../docs/system/compile-rules.md) and [validate.md](../../docs/system/validate.md).

### v4 rule shape

Each compile target includes **`input`**, **`output`**, **`env`**, **`exception`** (compiled ASCA strings) and joined **`rule`**. **`alternatives`** is a list of **objects** with the same fields (not bare strings). `steps` / correlated branches follow the same object model. **`validate_rules`** accepts **v3** string rows during transition.

## Comments

- Implements fan-out toggle in `resolve_inventory_targets` when `sample_alternatives` is false.
- ML / inventory-error CSV filtering remains out of scope.