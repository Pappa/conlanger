Type: epic-duck:plan
Status: in-progress

## Destination

A **cleaned rule index** (applier-neutral YAML source of truth) derived from **Index Diachronica HTML**, where **index rules** **compile** to valid ASCA — with **historical fidelity** and a scalable correction workflow.

## Notes

- **Agent entry:** [GLOSSARY.md](../../GLOSSARY.md), [docs/SYSTEM.md](../../docs/SYSTEM.md), ADRs under `docs/adr/` (especially parse → compile → validate).

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
- [Env and prose conditions](0025-decision-env-and-prose-conditions.md): IndexContext-first; Family A `! Host =`.
- [IndexRule / IndexContext model](0026-decision-indexrule-indexcontext-model.md): typed parse lifecycle ([ADR-0016](../../docs/adr/0016-parse-pipeline-order-and-raw-semantics.md), [ADR-0017](../../docs/adr/0017-structured-env-exception-indexcontext.md)).
- [Parse / compile package hygiene](0027-decision-parse-compile-package-hygiene.md): import seams; compile vs validate split; `asca_rules.yml`; position.in.
- [Inventory ok semantics](0028-decision-inventory-ok-semantics.md): `FAILED` / `OK` / `SKIPPED`; validate all targets.
- [Agent documentation](0029-decision-agent-documentation.md): GLOSSARY + SYSTEM + backlog closure checklist; plan indexes decisions.

## Not yet specified

- _(empty)_

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
| [0011-decision-asca-grouping-insertion.md](0011-decision-asca-grouping-insertion.md) | Grouping letters on insertion rules. | ready |
| [0013-decision-section-mappings-feature-matrices.md](0013-decision-section-mappings-feature-matrices.md) | **section_mappings** feature matrices and YAML compile. | ready |
| [0014-decision-composed-chain-path-inventory-policy.md](0014-decision-composed-chain-path-inventory-policy.md) | Composed chain path inventory policy. | ready |

## Tasks

| Task | Overview | Status |
|------|----------|--------|
| [0012-task-correction-pass-asca-grouping-insertion.md](0012-task-correction-pass-asca-grouping-insertion.md) | Correction pass: grouping on insertion rules after **0011**. | needs-detail |

## Spikes

| Spike | Overview | Status |
|-------|----------|--------|
| [0032-spike-asca-rule-validity.md](0032-spike-asca-rule-validity.md) | ASCA rule string validity checklist and parse pipeline (0.10.2). | resolved |
| [0033-spike-positional-slots-and-identity-subscripts.md](0033-spike-positional-slots-and-identity-subscripts.md) | Index positional/identity subscripts → ASCA reference syntax. | resolved |
| [0034-spike-subscript-notation-index-asca-brassica.md](0034-spike-subscript-notation-index-asca-brassica.md) | Index subscript uses vs ASCA and Brassica surface syntax. | resolved |
| [0035-spike-asca-khoisan-click-representation.md](0035-spike-asca-khoisan-click-representation.md) | ASCA representation of Khoisan click segments. | resolved |
| [0036-spike-asca-class-letter-mappings.md](0036-spike-asca-class-letter-mappings.md) | Index class letters → ASCA group_mappings. | resolved |
| [0037-spike-asca-ejective-notation.md](0037-spike-asca-ejective-notation.md) | Index post-matrix ejective marks vs ASCA `[+cg]` / diacritic rules. | resolved |
| [0038-spike-index-feature-matrices-to-asca-targets.md](0038-spike-index-feature-matrices-to-asca-targets.md) | feature_mappings.csv schema and Index matrix → ASCA targets. | resolved |
| [0039-spike-index-syllable-position-u-hash.md](0039-spike-index-syllable-position-u-hash.md) | Index `#U` / `U#` syllable position → ASCA env structures. | resolved |
| [0040-spike-inter-segment-whitespace-phoneme-boundaries.md](0040-spike-inter-segment-whitespace-phoneme-boundaries.md) | Inter-segment whitespace and phoneme boundaries (ASCA/Brassica). | resolved |
| [0041-spike-io-optionals-asca-and-convention.md](0041-spike-io-optionals-asca-and-convention.md) | Index I/O optionals vs ASCA structures and convention. | resolved |
| [0042-spike-breve-vowel-notation.md](0042-spike-breve-vowel-notation.md) | Index breve vowel notation (`̆`) → ASCA representation. | resolved |
| [0043-spike-field-isolation-compile-validation.md](0043-spike-field-isolation-compile-validation.md) | Field-isolation compile validation (go-with-limits). | resolved |
| [0044-spike-asca-native-per-field-validation.md](0044-spike-asca-native-per-field-validation.md) | Native ASCA per-field validation fork effort sizing. | resolved |