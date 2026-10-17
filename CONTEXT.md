# Conlanger

Automatic and assisted conlang tooling: phoneme inventories, morphology/grammar parameters, and diachronic sound-change pipelines.

## Start here (agents)

1. **[GLOSSARY.md](GLOSSARY.md)** — domain vocabulary (use these terms in issues, docs, and tests).
2. **[docs/SYSTEM.md](docs/SYSTEM.md)** — system map; rule index pipeline is **parse → compile → validate**.
3. **[docs/DEV.md](docs/DEV.md)** — pytest, ruff, ASCA fork install.
4. **Rule index effort** — [.scratch/rule-index/spec.md](.scratch/rule-index/spec.md). The wayfinder [.scratch/rule-index/map.md](.scratch/rule-index/map.md) is a **decision index**, not a glossary or implementation spec.

For cleaned-index YAML shape and SoT policy, read ADRs [0011](docs/adr/0011-index-rule-stages.md) ( **`stages`** spine), [0013](docs/adr/0013-parse-compile-validate.md) (three stages), [0016](docs/adr/0016-parse-pipeline-order-and-raw-semantics.md) (**raw** semantics), [0017](docs/adr/0017-structured-env-exception-indexcontext.md) (**IndexContext**).

## Documentation

- [Project overview](docs/CONLANGER.md) — notebook narrative and generative pipeline background
- [System map](docs/SYSTEM.md)
- [Index Diachronica parse](docs/system/index-diachronica-parser.md)
- [Applier compile](docs/system/sound-change-applier.md)
- [Validate](docs/system/validate.md) — inventory, correction loop, compile validation
- [Architectural decisions](docs/adr/)
- [Agent domain docs](docs/agents/domain.md)
