Type: epic-duck:plan
Status: in-progress

## Destination

A **cleaned rule index** (applier-neutral YAML source of truth) derived from **Index Diachronica HTML**, where **index rules** **compile** to valid ASCA — with **historical fidelity** and a scalable correction workflow.

## Notes

- **Agent entry:** [GLOSSARY.md](../../GLOSSARY.md), [docs/SYSTEM.md](../../docs/SYSTEM.md), ADRs under `docs/adr/` (especially parse → compile → validate).
- **Migration policy (plan 0001):** [0006](../items/0006-decision-wayfinder-ticket-migration-policy.md) — closed decisions are **`epic-duck:decision`** tickets with **`## Answer`**; this plan **Decisions so far** indexes them (one line + link). **≤25** indexed outcomes; spikes deferred to [0007](../items/0007-decision-wayfinder-spike-migration-policy.md).

## Decisions so far

- [Valid ASCA rule strings](0015-decision-valid-asca-rule-strings.md): `input > output [/env] [|exception]`; validate via ASCA parse pipeline.
- [YAML SoT shape](0016-decision-yaml-sot-shape.md): `abbreviations` + `sections`; uniform **`stages`** spine ([ADR-0011](../../docs/adr/0011-index-rule-stages.md)).
- [Historical fidelity vs validity](0017-decision-historical-fidelity-vs-validity.md): fidelity-first edits; cluster correction passes ([ADR-0010](../../docs/adr/0010-historical-fidelity-class-first-status.md)).
- [Abbreviations and class letters](0018-decision-abbreviations-and-class-letters.md): features at ingest; **`group_mappings`** at compile—not `.alias` `-l`.
- [Extract-only ingest](0019-decision-extract-only-ingest.md): applier-neutral YAML from HTML; parse-time surface norm bounds.
- [Validation inventory](0020-decision-validation-inventory.md): `create_index` + `validate_rules`; CSV splits and ok changelog.
- [Parse-time correction cluster](0021-decision-parse-time-correction-cluster.md): standing parse correction recipe before compile.
- [Series and section mappings](0022-decision-series-and-section-mappings.md): parse expansion; **`section_mappings`** / **`skip_sections`** config.
- [Optional outputs and nested sets](0023-decision-optional-outputs-nested-sets.md): alt idx, flatten nested sets, IO optional hold-outs.
- [Compile segment transforms](0024-decision-compile-segment-transforms.md): grouping, IPA, tone, clicks, etc. at compile.
- [Env and prose conditions](0025-decision-env-and-prose-conditions.md): IndexContext-first; Family A `! Host =`; open Family B in decision **0009** and task **0010**.
- [IndexRule / IndexContext model](0026-decision-indexrule-indexcontext-model.md): typed parse lifecycle ([ADR-0016](../../docs/adr/0016-parse-pipeline-order-and-raw-semantics.md), [ADR-0017](../../docs/adr/0017-structured-env-exception-indexcontext.md)).
- [Parse / compile package hygiene](0027-decision-parse-compile-package-hygiene.md): import seams; compile vs validate split; `asca_rules.yml`; position.in.
- [Inventory ok semantics](0028-decision-inventory-ok-semantics.md): `FAILED` / `OK` / `SKIPPED`; validate all targets.
- [Agent documentation](0029-decision-agent-documentation.md): GLOSSARY + SYSTEM + implement-closure; plan indexes decisions.

## Not yet specified

- Cutover policy for `.scratch/rule-index/` vs `.backlog/` for **new** tickets after migration.

## Out of scope

- Generative conlang modeling and PHOIBLE/WALS pipelines (separate feature plans **0004** and **0005**).

## Decisions

| Decision | Overview | Status |
|----------|----------|--------|
| [0015-decision-valid-asca-rule-strings.md](0015-decision-valid-asca-rule-strings.md) | Valid ASCA rule string shape and validation. | resolved |
| [0016-decision-yaml-sot-shape.md](0016-decision-yaml-sot-shape.md) | YAML SoT schema and **stages** spine. | resolved |
| [0017-decision-historical-fidelity-vs-validity.md](0017-decision-historical-fidelity-vs-validity.md) | Fidelity vs validity and correction workflow. | resolved |
| [0018-decision-abbreviations-and-class-letters.md](0018-decision-abbreviations-and-class-letters.md) | Abbreviations, features, class letters at compile. | resolved |
| [0019-decision-extract-only-ingest.md](0019-decision-extract-only-ingest.md) | Minimal HTML→YAML ingest bounds. | resolved |
| [0020-decision-validation-inventory.md](0020-decision-validation-inventory.md) | Full-index inventory and tracking. | resolved |
| [0021-decision-parse-time-correction-cluster.md](0021-decision-parse-time-correction-cluster.md) | Parse-time correction-pass cluster. | resolved |
| [0022-decision-series-and-section-mappings.md](0022-decision-series-and-section-mappings.md) | Series and **section_mappings** policy. | resolved |
| [0023-decision-optional-outputs-nested-sets.md](0023-decision-optional-outputs-nested-sets.md) | Optional outputs and nested sets. | resolved |
| [0024-decision-compile-segment-transforms.md](0024-decision-compile-segment-transforms.md) | Compile-time segment transforms. | resolved |
| [0025-decision-env-and-prose-conditions.md](0025-decision-env-and-prose-conditions.md) | Env, prose, identity exceptions (Family A). | resolved |
| [0026-decision-indexrule-indexcontext-model.md](0026-decision-indexrule-indexcontext-model.md) | IndexRule / IndexContext model. | resolved |
| [0027-decision-parse-compile-package-hygiene.md](0027-decision-parse-compile-package-hygiene.md) | Package seams and operator split (2026). | resolved |
| [0028-decision-inventory-ok-semantics.md](0028-decision-inventory-ok-semantics.md) | Inventory **ok** enum and validate targets. | resolved |
| [0029-decision-agent-documentation.md](0029-decision-agent-documentation.md) | Agent doc entry and closure. | resolved |
| [0009-decision-index-identity-exception-env-splice.md](0009-decision-index-identity-exception-env-splice.md) | `! Host =` env-slot exception compile policy (Family B). | in-progress |
| [0011-decision-asca-grouping-insertion.md](0011-decision-asca-grouping-insertion.md) | Grouping letters on insertion rules. | ready |
| [0013-decision-section-mappings-feature-matrices.md](0013-decision-section-mappings-feature-matrices.md) | **section_mappings** feature matrices and YAML compile. | ready |
| [0014-decision-composed-chain-path-inventory-policy.md](0014-decision-composed-chain-path-inventory-policy.md) | Composed chain path inventory policy. | ready |

## Tasks

| Task | Overview | Status |
|------|----------|--------|
| [0008-task-execute-wayfinder-rule-index-migration.md](0008-task-execute-wayfinder-rule-index-migration.md) | First migration pass: merged **Decisions so far** and open tasks on **0003**. | resolved |
| [0010-task-index-identity-exception-residuals.md](0010-task-index-identity-exception-residuals.md) | Compile fix for identity exception residuals after **0009**. | ready |
| [0012-task-correction-pass-asca-grouping-insertion.md](0012-task-correction-pass-asca-grouping-insertion.md) | Correction pass: grouping on insertion rules after **0011**. | needs-detail |

## Spikes

| Spike | Overview | Status |
|-------|----------|--------|
| | | |
