# Compiled `asca_rules.yml` (compile-stage artifact)

The operator pipeline exposes compile as its own stage. **`compile_rules`** reads the applier-neutral index YAML, resolves every rule to ASCA compile targets, and writes **`diagnostics/compile/asca_rules.yml`**. **`validate_rules`** reads that file only — it does not re-compile from the index.

## Considered options

- **Compile inside `validate_rules` only (previous steady state, ticket 103)** — one command, no on-disk compile artifact; hard to diff compile output or re-run validation without re-compiling.
- **Dedicated compile command + git-tracked YAML (chosen)** — three commands (`create_index` → `compile_rules` → `validate_rules`); compile output is diffable like inventory CSVs.

## Consequences

- **Not source of truth:** Index YAML remains SoT for Index-shaped fields ([ADR-0002](0002-applier-neutral-yaml-rule-index.md)). Compiled YAML is operational output for inspect + validate.
- **Path:** `diagnostics/compile/asca_rules.yml` (`DEFAULT_COMPILED_YAML` in `pipeline_defaults.py`).
- **Schema:** `schema_version: 3` — see [compile-rules.md](../system/compile-rules.md). Each compiled rule stores `rule`, `alternatives`, or `steps`. Correlated optional paths through a chain (e.g. Balinese `r → {r,h} → {∅,h}`) use `alternatives` of `{steps: […]}` branches, not independent per-stage alternative blocks. `validate_rules` validates those lines directly. v2 `targets[]` and v1 `series` remain readable for transition. No index fingerprint; operators re-run `compile_rules` after index changes before `validate_rules`.
- **Inventory:** Pass/fail stays in `diagnostics/inventory/` CSVs only — no `valid` flags on compiled YAML (grill 160).
- **Regeneration:** `uv run compile_rules` overwrites the file; commit regenerated YAML in PRs that change parse/compile behaviour (same policy as inventory outputs).
