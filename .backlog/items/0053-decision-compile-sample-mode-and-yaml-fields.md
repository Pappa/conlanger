Type: epic-duck:decision
Status: needs-detail
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: How compile selects single-path vs validate fan-out, and v4 structured fields in `asca_rules.yml`.
Blocked by:

## Question

How should **`compile_rules`** support both **stochastic single-path** compile (pipeline / ML) and **validate/diagnostics fan-out**, and what **on-disk rule shape** should `asca_rules.yml` use for decomposed ASCA fields?

## Settled so far (conversation; not final **Answer**)

- **One compile pipeline** — no separate ML export script or CSV artifact; YAML only ([0054](0054-task-compile-rules-sample-mode-v4-schema.md) implements after this decision).
- **[0055](0055-task-compiler-config-merge-and-seed.md)** first — `CompilerConfig` precedence (class defaults ← YAML ← CLI scalars) and optional **`seed`** (including `seed: 0` on committed asca config for reproducible validate compile).
- **Asca validate config unchanged** — keep [`config/compile/asca/compiler_config.yml`](../../config/compile/asca/compiler_config.yml) as the validate/diagnostics profile (`sample_sporadic` / `sample_dialect` false per operator intent).
- **Pipeline profile** — add [`config/pipeline/compiler_config.yml`](../../config/pipeline/compiler_config.yml) (path TBD in implementation) for standard pipeline compile; may omit keys that should fall through to **class defaults** once [0055](0055-task-compiler-config-merge-and-seed.md) lands.
- **v4 schema** — each target carries **`input`**, **`output`**, **`env`**, **`exception`** (compiled ASCA) plus joined **`rule`**; **`alternatives`** as objects, not bare strings; `validate_rules` reads v3 strings during transition.

## Open questions

1. **Mode switch** — Prefer **no `--sample` CLI** if behaviour is fully expressed by **which compiler config** is loaded (asca vs pipeline) plus new fields such as **`enumerate_compile_targets`** (name TBD) on `CompilerConfig`. Is a **`--compiler-config`** path on `compile_rules` enough, or is a dedicated flag still needed?
2. **Optional fan-out** — Pipeline mode must stop **`resolve_inventory_targets`** from expanding full `part.alternatives` (today enumeration ignores stochastic `randrange` picks). Exact mechanism tied to (1).
3. **Sporadic / dialect** — With asca config (`sample_*: false`): always apply, no `compile_skipped`. With pipeline config (`sample_*: true` via defaults or explicit YAML): 50% apply / `compile_skipped` when skipped. Confirm no third path.
4. **Operator docs** — Wording for validate: `compile_rules` with asca config vs pipeline default — pending (1).

**Superseded draft:** an earlier ticket revision proposed **`--sample`** / **`--seed` on the CLI**; that is **not decided**. Remove from docs and **0054** acceptance criteria until this decision closes.

## Answer

_(Pending.)_

## Comments

- Fan-out today: `_enumerate_composed_chain_paths` in [`inventory_targets.py`](../../src/conlanger/tools/inventory_targets.py).
- Inventory-error filtering for ML remains out of scope.