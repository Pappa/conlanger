Type: epic-duck:plan
Status: in-progress

## Destination

A **cleaned rule index** (applier-neutral YAML source of truth) derived from **Index Diachronica HTML**, where **index rules** **compile** to valid ASCA — with **historical fidelity** and a scalable correction workflow.

## Notes

- **Agent entry:** [GLOSSARY.md](../../GLOSSARY.md), [docs/SYSTEM.md](../../docs/SYSTEM.md), ADRs under `docs/adr/` (especially parse → compile → validate).
- **Migration policy (plan 0001):** [0006](../items/0006-decision-wayfinder-ticket-migration-policy.md) — merged summaries live on this plan and child tasks only; **Decisions so far** entries are self-contained (no links into the legacy wayfinder tree). **≤25** indexed outcomes; spikes deferred to [0007](../items/0007-decision-wayfinder-spike-migration-policy.md).

## Decisions so far

- **Valid ASCA rule strings:** A rule string is `input > output [/env] [|exception]` with non-empty input/output (including `*`, `∅`, metathesis); env uses a single `_` focus and `#` only env-peripheral. Prefer ASCA `ParsedRules::try_from` for validation ([docs/system/sound-change-applier.md](../../docs/system/sound-change-applier.md)).
- **YAML SoT shape:** Top-level `abbreviations` and `sections`; each rule carries a uniform **`stages`** list plus `raw`, `source`, and optional metadata ([ADR-0011](../../docs/adr/0011-index-rule-stages.md)). Index Diachronica HTML is ingest source; cleaned YAML is the working SoT.
- **Historical fidelity vs validity:** Prefer edits that preserve attested Index meaning; separate **rule status** / hold-outs from compile validation failures; run correction passes by failure cluster ([ADR-0010](../../docs/adr/0010-historical-fidelity-class-first-status.md)).
- **Abbreviations and class letters:** Normalize feature matrices at ingest; expand DiachronicSeries and class letters at **compile** via `group_mappings`. ASCA `.alias` (`-l`) is for word (de)romanisation only—not a substitute for compile-time class-letter expansion.
- **Extract-only ingest:** `IndexDiachronicaParser` emits applier-neutral YAML with parse-time surface normalisation (arrows, glosses, chain split, sporadic flags); do not push ASCA-only surface into SoT unless applier-agnostic.
- **Validation inventory:** Regenerate YAML, run `uv run create_index && uv run validate_rules`; keep per-rule CSV, summary, success/error splits, and ok-flip changelog for correction prioritisation ([docs/system/validate.md](../../docs/system/validate.md)).
- **Parse-time correction cluster:** Standing recipe: typographic cleanup, chain expansion, gloss/stress/sporadic handling, smart quotes, editorial slashes—applied at parse before compile ([docs/system/index-diachronica-parser.md](../../docs/system/index-diachronica-parser.md)).
- **Series and section mappings:** Expand correspondence-series indices at parse when section maps exist; retire CSV `series_mappings`; use `parser_config` **section_mappings** and **skip_sections** for heavy/deferred families.
- **Optional outputs and nested sets:** Support optional stage outputs (alt idx) and parse-time flattening of nested context/I/O sets where fidelity allows; cartesian IO optionals and human-review hold-outs documented when attested forms cannot compile mechanically.
- **Compile-time segment transforms:** Pipeline applies group mappings, length and ejective normalisation, parenthetical/meta expansion, superscripts, IPA letter mappings, tone matrices, Khoisan click defaults, and related segment fixes at **compile**, not in SoT YAML literals.
- **Env and prose conditions:** Prose env phrases, double-slash env, parallel `∅` outputs, syllable `#U` tails, and env-bound **`! Host =`** identity exclusions (Family A compile substitution) are handled via structured **IndexContext** where possible ([ADR-0017](../../docs/adr/0017-structured-env-exception-indexcontext.md)).
- **IndexRule / IndexContext model:** Typed parse lifecycle (`IndexRule`), normalisation passes, and compile resolution from structured env/exception—not ASCA env literals stored in applier-neutral fields ([ADR-0016](../../docs/adr/0016-parse-pipeline-order-and-raw-semantics.md)).
- **Parse / compile package hygiene (2026):** Enforce ingest vs compile import boundaries; reorder env pipeline; split operator **compile_rules** vs **validate_rules** on compiled YAML; emit monitoring `asca_rules.yml`; compile **position.in** relation projection.
- **Inventory and ok semantics:** Inventory **`ok`** uses `FAILED` / `OK` / `SKIPPED`; validate all compile targets; optional per-field blame; forked ASCA `validate` wired for compile checks.
- **Agent documentation:** Domain terms in [GLOSSARY.md](../../GLOSSARY.md); pipeline table in [docs/SYSTEM.md](../../docs/SYSTEM.md); closure via [implement-closure.md](../../docs/agents/implement-closure.md) and `uv run check`—this backlog plan indexes decisions, not legacy map **Notes**.

## Not yet specified

- Cutover policy for `.scratch/rule-index/` vs `.backlog/` for **new** tickets after migration.

## Out of scope

- Generative conlang modeling and PHOIBLE/WALS pipelines (separate feature plans **0004** and **0005**).

## Decisions

| Decision | Overview | Status |
|----------|----------|--------|
| | | |

## Tasks

| Task | Overview | Status |
|------|----------|--------|
| [0008-task-execute-wayfinder-rule-index-migration.md](0008-task-execute-wayfinder-rule-index-migration.md) | First migration pass: merged **Decisions so far** and open tasks on **0003**. | resolved |
| [0009-task-grill-index-identity-exception-env-splice.md](0009-task-grill-index-identity-exception-env-splice.md) | Grill: `! Host =` env-slot exception compile policy. | in-progress |
| [0010-task-index-identity-exception-residuals.md](0010-task-index-identity-exception-residuals.md) | Compile fix for identity exception residuals after **0009**. | ready |
| [0011-task-grill-asca-grouping-insertion.md](0011-task-grill-asca-grouping-insertion.md) | Grill: grouping letters on insertion rules. | needs-detail |
| [0012-task-correction-pass-asca-grouping-insertion.md](0012-task-correction-pass-asca-grouping-insertion.md) | Correction pass: grouping on insertion rules after **0011**. | needs-detail |
| [0013-task-grill-section-mappings-feature-matrices.md](0013-task-grill-section-mappings-feature-matrices.md) | Grill: section_mappings feature matrices and YAML compile. | needs-detail |
| [0014-task-grill-composed-chain-path-inventory-policy.md](0014-task-grill-composed-chain-path-inventory-policy.md) | Grill: composed chain path inventory policy. | needs-detail |

## Spikes

| Spike | Overview | Status |
|-------|----------|--------|
| | | |
