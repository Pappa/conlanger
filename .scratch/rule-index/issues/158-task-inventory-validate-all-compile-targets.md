Type: task
Status: ready-for-agent
Blocked by: None

# Task: deterministic validation for all compile-expanded targets

Spawned from [Grill: `validate_rules` compile diagnostic `diagnostics/compile/asca_rules.yml`](151-grill-validate-rules-asca-rules-yaml-diagnostic.md) (resolved 2026-10-17). Owner report: inventory **`ok`** / compiled `rule` column can **flip-flop across regen** when optional-output **alternatives** exist (and chain multi-step coverage may be incomplete).

## Question

Make per-**index rule** compile validation **stable and complete** across every compile-expanded target. Each branch must expose its own pass/fail for `asca_rules.yml` **`alternatives[].valid`** / **`steps[].valid`** (top-level `valid` = AND of children).

## Scope

| Gap | Today (`index_inventory.py`) | Target |
| --- | --- | --- |
| Optional outputs | Fan-out validates each `alt_idx`, but `SoundChangeRule` construction may still **RNG-pick** one branch for non-inventory paths; changelog joins on `(source, alt_idx)` — confirm no row churn from ordering or partial compile | All alternatives validated; no stochastic compile choice affecting inventory |
| Multi-stage `stages` chains | `DiachronicSeries` emits multiple `SoundChangeRule` steps; inventory `rule` column stores **`rules[0]` only** while `validate_asca` runs the **full** mini-series | Explicit policy: validate **every step** (or document single-series validate is intentional); `rule` column / YAML `valid` align |
| Sporadic / dialect sampling | `rng` may skip sporadic application across runs | Inventory uses fixed seed or validates both apply/skip paths per policy |

## Acceptance

- Documented policy in `docs/system/validate.md` (what “one index rule ok” means for chains + alts).
- Regen inventory twice on unchanged YAML + config: **no `ok` flips** on rules with alternatives (unless `--reset-changelog` / intentional seed change).
- Tests lock behaviour for at least one alternative fan-out rule and one multi-stage chain.

## Out of scope

- Writing `diagnostics/compile/asca_rules.yml` → [159](159-task-write-compile-asca-rules-yml.md).
