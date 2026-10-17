Type: grilling
Status: resolved
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
| **Docs / ADR** | **Required additions/changes** in same PR as code: amend ADR-0013 (+ ADR-0003 if needed), new/amended ADR for compiled `asca_rules.yml`; refresh SYSTEM.md, validate/applier/parser/DEV docs; grep `docs/` for stale two-command workflow. See Answer § ADRs and docs; checklist in [161](161-task-split-compile-rules-and-validate-compiled-yaml.md). |
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

## Answer

**Resolved 2026-10-17** (owner grill; initial proposal + **grill round 1** confirmations below). Compile output moves to a dedicated **`compile_rules`** command; **`validate_rules`** is validation + inventory only. Supersedes **103** steady-state “compile in validate” and **151**/**159** use of `valid` on compiled YAML. Implementation: ~~[Task: `compile_rules` script and validation-only `validate_rules`](161-task-split-compile-rules-and-validate-compiled-yaml.md)~~ **resolved** (2026-10-17).

### Owner-confirmed (grill round 1)

| # | Decision |
| --- | --- |
| Q1 | **`validate_rules` never reads index YAML** in steady state — no `--yaml-in` on validate; compiled file only. |
| Q2 | **`asca_rules.yml` is committed** in git when regenerated (same class as `diagnostics/inventory/` CSVs: operational, diffable, not hand-edited). |
| Q3 | Each target carries **`rule` (string) and `series` (parts)**; tests assert compiled line matches deserialised `SoundChangeRule` / `validate_asca` input. |
| Q4 | **No index fingerprint / hash in v1**; stale compile is operator error — run `compile_rules` before `validate_rules`; document in ADR + validate doc. |
| Q5 | **New ADR** for compiled artifact (role, path, `schema_version` v1, not SoT) — not only a patch to ADR-0013. |

### Operator workflow

| Command | Loads | Requires ASCA | Writes |
| --- | --- | --- | --- |
| `create_index` | HTML | no | `index_diachronica.yml`, parse diagnostics |
| `compile_rules` | index YAML | no | `asca_rules.yml` |
| `validate_rules` | `asca_rules.yml` | yes | inventory under `diagnostics/inventory/` |

```bash
uv run create_index && uv run compile_rules && uv run validate_rules
```

- **Parse-only:** `create_index`
- **Compile-only** (index unchanged): `compile_rules`
- **Validate-only** (re-run probes / inventory): `validate_rules`

### File role and path

| Topic | Policy |
| --- | --- |
| Path | `diagnostics/compile/asca_rules.yml` (`DEFAULT_COMPILED_YAML` beside existing `DEFAULT_COMPILE_DIR`). |
| Role | **Compile-stage artifact** — full compiled rule set for inspect + validate; **not** applier-neutral SoT ([148](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md)). Index YAML remains SoT for Index-shaped fields. |
| Git | **Regenerated** each `compile_rules` run; **tracked in git** like inventory CSVs (diffable in PRs; not hand-edited). |

### YAML schema (v1)

- Root: `schema_version: 1`, `sections:` mirroring index section headers (`index`, `section`, `rules`).
- Omit entire sections with `status: skipped` (unchanged from 151).
- **No `valid` anywhere** — pass/fail only in inventory CSVs ([152](152-grill-inventory-ok-column-string-enum.md)).

**Per index rule**

| Shape | Fields |
| --- | --- |
| Compile OK (one or more ASCA targets) | `rule_id`, `source` (copied from index), `targets: [...]` |
| Rule skipped | `rule_id`, `source`, `status: skipped`, `rule` (`#\t` + raw per `SoundChangeRule.__str__`) |
| Sporadic compile skip | `status: compile_skipped`, `rule` (compiled comment line) |
| Compile failure | `rule_id`, `source`, `compile_error` (message); no `targets` |

**Each `targets[]` entry** (replaces separate `alternatives` / `steps` trees with `valid`):

| Field | Value |
| --- | --- |
| `step_idx` | `null` or int (chain step; same semantics as inventory `step_idx`) |
| `alt_idx` | `null` or int (optional-output branch; same as inventory `alt_idx`) |
| `rule` | Single compiled ASCA line string (human inspection; matches inventory `rule` column) |
| `series` | `{parts: [...]}` — serialised `DiachronicSeries` mini-series for this target (`RuleTitle` + `SoundChangeRule`), round-trip via `DiachronicSeries.from_parts` for `validate_asca` |

`SoundChangeRule` serialisation: Pydantic `model_dump` / `model_validate` (exclude `compiler_config`, `rng`; optional fixed `seed` only if needed for sporadic re-compile — validate path does not re-roll sporadic). Field isolation deserialises the `SoundChangeRule` part from `series.parts`, not a second compile from index.

#### Example (single target)

```yaml
schema_version: 1
sections:
- section: North Frisian Lenition
  index: 17.7.2.1.15
  rules:
  - rule_id: North-Frisian-Lenition-p-t-k
    source: index_diachronica.html:…
    targets:
    - step_idx: null
      alt_idx: null
      rule: p t k > f s x
      series:
        parts:
        - type: title
          index: 17.7.2.1.15
          section: North Frisian Lenition#North-Frisian-Lenition-p-t-k
        - type: sound_change_rule
          input: …
          output: …
          env: null
          exception: null
```

**Encoding:** Pydantic-friendly part dicts with a `type` discriminator (or equivalent) chosen in 161 — must round-trip `DiachronicSeries.from_parts`. **`rule` must stay consistent** with the `SoundChangeRule` in `series.parts` (enforced by tests).

#### Example (alternatives — two targets, same rule_id)

```yaml
  - rule_id: example-optional-output
    source: …
    targets:
    - step_idx: null
      alt_idx: 0
      rule: a > b
      series: {parts: […]}
    - step_idx: null
      alt_idx: 1
      rule: a > c
      series: {parts: […]}
```

### Inventory data flow (after split)

```mermaid
flowchart LR
  IDX[index_diachronica.yml]
  CR[compile_rules]
  ASCA_Y[asca_rules.yml]
  VR[validate_rules]
  INV[inventory CSVs]

  IDX --> CR --> ASCA_Y --> VR --> INV
```

- **`validate_rules` does not read index YAML** (no `--yaml-in`); `source` and section identity come from compiled YAML envelopes only.
- **No compile freshness metadata in v1** — no hash of `index_diachronica.yml`; operators run `compile_rules` before `validate_rules` after index changes.
- **`matched_correction_rule_ids`** unchanged: `ParserConfig.corrections` + `rule_id` from validation rows.
- **Field isolation:** `--field-isolation` uses deserialised `SoundChangeRule` per target (`validate_asca_part` on compiled fields); no `CompilerConfig` on validate path.

### Code seams

| Module | Change |
| --- | --- |
| `index_inventory.py` | Split **compile target resolution** vs **validate from targets**; add `iter_compiled_inventory_bundles(compiled_doc, …)`. |
| `compiled_rules_yaml.py` | Emit/read v1 from compile targets; remove `valid` / `ValidationRow` coupling. |
| `validate_rules.py` | Read compiled YAML, inventory only. |
| `compile_rules.py` | New script. |
| [150](150-grill-parse-compile-module-seams.md) | Moving `_resolve_inventory_targets` toward `compile/` is in-scope for 161 if it clarifies imports; not blocked on 150 resolution. |

### Flags

| Script | Flags |
| --- | --- |
| `compile_rules` | `--yaml-in`, `--compiled-out` |
| `validate_rules` | `--compiled-in`, `--inventory-dir`, `--probe-words`, `--field-isolation`, `--use-asca-fork`, `--reset-changelog`, `--limit` |

Remove from `validate_rules`: `--no-write-compiled-rules`, `--compile-dir` (write), default compile-on-validate behaviour.

### Effort

**One task** ([161](161-task-split-compile-rules-and-validate-compiled-yaml.md)): medium — mostly extraction and IO refactor; inventory logic reused. No change to compile transforms or CSV column schema.

### ADRs and docs

Implementation **must** update project ADRs and docs in the same change set as the scripts (not deferred). Minimum:

- **Amend** [ADR-0013](../../../docs/adr/0013-parse-compile-validate.md) (three operator commands; compile artifact on disk).
- **Amend** [ADR-0003](../../../docs/adr/0003-validate-after-applier-compile.md) if it still implies validate compiles from index YAML.
- **Add** a new ADR for compiled `asca_rules.yml` (not SoT, `schema_version` v1, git-tracked artifact, vs [ADR-0002](../../../docs/adr/0002-applier-neutral-yaml-rule-index.md)); amend [103](103-split-create-index-and-validate-rules.md) consequence via that ADR or 0013 cross-link.
- **Refresh** [docs/SYSTEM.md](../../../docs/SYSTEM.md), [validate.md](../../../docs/system/validate.md), [sound-change-applier.md](../../../docs/system/sound-change-applier.md), [DEV.md](../../../docs/DEV.md), and parser doc cross-links; grep `docs/` for stale `create_index && validate_rules` / in-memory compile wording.

Checklist detail: [161 ADRs and docs](161-task-split-compile-rules-and-validate-compiled-yaml.md#adrs-and-docs-required--same-pr-as-code).
