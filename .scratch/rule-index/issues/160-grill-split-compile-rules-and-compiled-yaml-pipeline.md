Type: grilling
Status: needs-grilling
Blocked by: None

# Grill: split `compile_rules` vs `validate_rules` and compiled `asca_rules.yml` contract

Owner proposal (2026-10-17) after [Task: write `diagnostics/compile/asca_rules.yml`](159-task-write-compile-asca-rules-yml.md) and [Task: inventory validate all compile targets](158-task-inventory-validate-all-compile-targets.md) landed.

## Question

How should the **operator pipeline** expose parse → compile → validate as **three commands**, with **`asca_rules.yml`** as the on-disk compile output (not a validation mirror), and **`validate_rules`** validation-only from that file?

Target steady state:

```bash
uv run create_index && uv run compile_rules && uv run validate_rules
```

This **reopens** parts of [Split `create_index` and `validate_rules`](103-split-create-index-and-validate-rules.md) (compile was in-memory inside `validate_rules`; no compiled artifact on disk) and reframes [Grill: `validate_rules` compile diagnostic `asca_rules.yml`](151-grill-validate-rules-asca-rules-yaml-diagnostic.md) / **159** (diagnostic YAML with per-branch `valid` flags).

## Owner direction (to confirm or amend)

1. **`compile_rules`** — load applier-neutral `index_diachronica.yml`, run the full compile path (`DiachronicSeries` / `SoundChangeRule`), write **complete** compiled rules to `asca_rules.yml`.
2. **`validate_rules`** — load `asca_rules.yml` only (no re-compile from index YAML); run existing inventory steps (ASCA `validate` / `validate_asca`, CSV splits, changelog, summary, optional field isolation, error clusters).
3. **Drop `valid`** from `asca_rules.yml`; pass/fail lives in inventory CSVs only ([152](152-grill-inventory-ok-column-string-enum.md) / [157](157-task-inventory-ok-column-string-enum.md)).
4. **Schema** — `asca_rules.yml` must round-trip through a **`DiachronicSeries` (or equivalent) YAML model**, not only `{rule, valid}` / `alternatives` / `steps` diagnostic strings from 151.

## Decisions to lock

| Topic | Options / notes |
| --- | --- |
| **File role** | Pipeline artifact vs retained under `diagnostics/compile/` vs `data/asca/asca_rules.yml` (or other). Committed in repo or generated-only? |
| **YAML shape** | Full `sections` mirror with compiled field payloads per index rule vs serialised `DiachronicSeries.parts` per section vs hybrid (index metadata + compiled targets). How are **alternatives**, **chain steps**, **skipped** (`#\t` lines), and **compile errors** represented without `valid`? |
| **Serialisation API** | Pydantic `model_dump` / custom `read_compiled_index` + `write_compiled_index`; what is required for `DiachronicSeries.from_parts` or constructor parity with today’s `_mini_section` + compile path? |
| **Inventory inputs** | Today `iter_index_rule_inventory_bundles` compiles then validates in one pass. After split: validate from compiled YAML only — which columns still need **index** fields (`source`, `raw`, section `index`, correction-id matching)? Dual-read index + compiled, or embed metadata in compiled YAML? |
| **Field isolation** | Does `--field-isolation` still need compile-time `targets` from `SoundChangeRule`, or can blame run from compiled field strings on disk? |
| **`compiled_rules_yaml.py`** | Reuse/refactor vs replace; relationship to [150](150-grill-parse-compile-module-seams.md) compile package boundaries. |
| **Flags / defaults** | `--yaml-in` on `compile_rules`; `--compiled-yaml-in` on `validate_rules`; drop `--no-write-compiled-rules` / move compile-dir defaults to `pipeline_defaults.py`. |
| **Docs / ADR** | [ADR-0013](../../../docs/adr/0013-parse-compile-validate.md), `docs/system/validate.md`, map runtime note — three-command steady state. |
| **Effort** | Rough slice list for implementation ticket(s): new script + pyproject entry, extract compile loop from `validate_rules`, new IO + schema tests, inventory refactor, doc/test grep. |

## Non-goals (unless grill expands scope)

- Changing compile transforms or correction-pass logic.
- Replacing inventory CSV schema or ok enum.
- Making `asca_rules.yml` the applier-neutral SoT ([148](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md)) — index YAML remains SoT for Index-shaped fields.

## Deliverable

Resolution comment with: chosen paths, YAML schema sketch (one example section + one alternatives rule), inventory data-flow diagram, and whether follow-on work is **one task** or **compile task + validate task**. Link implementation ticket(s) from the answer.

## Related

- [103 split create_index / validate_rules](103-split-create-index-and-validate-rules.md)
- [151 grill compile diagnostic YAML](151-grill-validate-rules-asca-rules-yaml-diagnostic.md) · [159 write YAML](159-task-write-compile-asca-rules-yml.md) · [158 validate all targets](158-task-inventory-validate-all-compile-targets.md)
- [150 parse vs compile seams](150-grill-parse-compile-module-seams.md)
- [91 three-stage pipeline docs](91-three-stage-pipeline-docs.md)
