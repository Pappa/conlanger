Type: task
Status: resolved
Blocked by: None

# Task: write `diagnostics/compile/asca_rules.yml` from `validate_rules`

Spawned from [Grill: `validate_rules` compile diagnostic `diagnostics/compile/asca_rules.yml`](151-grill-validate-rules-asca-rules-yaml-diagnostic.md) (resolved 2026-10-17).

## Question

Implement the compile diagnostic YAML contract locked in grill **151** and wire it into `uv run validate_rules`.

## Contract (from 151)

- **Path:** `diagnostics/compile/asca_rules.yml` (default; override via flag e.g. `--compile-dir` / `--no-write-compiled-rules` to skip).
- **Lifecycle:** written on every successful `validate_rules` run (default **on**), independent of pass/fail; same compile pass as inventory.
- **Top-level:** `sections:` only — mirror `index_diachronica.yml` section shape (`section`, `index`, `rules`).
- **Per index rule:** `rule_id`, top-level `valid: true|false` (**AND** of all nested targets).
  - **Single-form:** `rule: <string>` (one compiled line).
  - **Multi-form alternatives:** `alternatives: [{rule, valid}, …]` (optional-output fan-out); no top-level `rule`.
  - **Multi-form chain:** `steps: [{rule, valid}, …]` (adjacent `stages` steps); no top-level `rule`.
- **Skipped rule:** `status: skipped`, `rule` = exact `str(SoundChangeRule)` (`#\t` + body); omit `valid` or document SKIPPED handling consistently with inventory.
- **Compile error:** `valid: false`, `compile_error: <message>`, no `rule` lines.
- **Section `status: skipped`:** omit entire section from YAML.
- **Sporadic compile skip:** `status: compile_skipped` (or equivalent), `rule` = `#\t` + compiled fields per compiler.
- **Not in file:** `generated_at`, `source_yaml`, per-field blame (stay in `field_isolation/`).

## Acceptance

- [x] `uv run validate_rules` writes YAML; `--no-write-compiled-rules` skips it.
- [x] Blurb in `docs/system/validate.md` under default paths table.
- [x] Tests: smoke write + one `steps` block + one `alternatives` block (per-branch `valid`) + skipped rule line shape.

## Answer

**Resolved 2026-10-17** (151 contract: `valid` on compiled YAML branches, validate-time write). Steady-state operator pipeline and v1 `targets` + `series` schema (no `valid` on disk): **[160](160-grill-split-compile-rules-and-compiled-yaml-pipeline.md)** / ~~**[161](161-task-split-compile-rules-and-validate-compiled-yaml.md)**~~ **resolved** (2026-10-17) — `compile_rules` writes `diagnostics/compile/asca_rules.yml`; `validate_rules` reads compiled YAML only.

## Related

- Validation stability for `valid` semantics: [158](158-task-inventory-validate-all-compile-targets.md).
