# System map

End-to-end view of the Conlanger pipeline: what each stage does, where it lives today, and what it should produce. Product arc is locked in [ADR-0007](./adr/0007-generative-conlang-pipeline.md).

Most stages still live in **Jupyter notebooks** for exploration and convenience. The target shape is an **automated pipeline** in the `conlanger` package that runs all steps and emits constructed-language artifacts (grammar document, audio, evolved lexicon, and related outputs).

## Pipeline stages

Sound-change rule index processing — parse → compile → validate:

| Stage | Doc | Operator command |
| --- | --- | --- |
| Index Diachronica parse | [index-diachronica-parser.md](./system/index-diachronica-parser.md) | `uv run create_index` |
| Applier compile | [sound-change-applier.md](./system/sound-change-applier.md) | (in-memory inside `validate_rules`) |
| Validate | [validate.md](./system/validate.md) | `uv run validate_rules` |

## Pipeline stages (legacy)

| Stage | Current implementation | Target artifacts |
| --- | --- | --- |
| **Data preparation** | [01_01_prepare_phoible_data.ipynb](../notebooks/01_01_prepare_phoible_data.ipynb), [01_02_prepare_wals_data.ipynb](../notebooks/01_02_prepare_wals_data.ipynb) | `notebooks/data/language_phonemes.npz`, `notebooks/data/language_parameters.npz`; later, automated ingest (see [ticket](../.scratch/data-processing-pipeline/issues/01-automate-phoible-wals-prep.md)) |
| **Phoneme inventory generation** | [02_01_phoneme_gan.ipynb](../notebooks/02_01_phoneme_gan.ipynb); [WGANGP](../src/conlanger/models/WGANGP.py) | GAN-generated inventories; ~100 bundled **preset inventories** in the package [ADR-0008](./adr/0008-gan-inventories-and-bundled-presets.md) |
| **Morphology / grammar parameters** | [02_02_wals_parameters_gan.ipynb](../notebooks/02_02_wals_parameters_gan.ipynb) | Generated WALS-like parameter sets for grammar/morphology modelling |
| **Lexicon generation** | [03_01_word_list.ipynb](../notebooks/03_01_word_list.ipynb), [03_02_generate_lexicon.ipynb](../notebooks/03_02_generate_lexicon.ipynb); [Lexicon](../src/conlanger/tools/Lexicon.py), [SyllableStructure](../src/conlanger/tools/SyllableStructure.py) | Proto-language root lexicon from inventory + phonotactics ([ADR-0009](./adr/0009-lexicon-generate-then-evolve.md)) |
| **Rule index (Index Diachronica)** | [IndexDiachronicaParser](../src/conlanger/tools/parsers.py), [asca_validator](../src/conlanger/tools/asca_validator.py), [DiachronicSeries](../src/conlanger/tools/rules.py); work under `.scratch/cleaned-rule-index/` | Applier-neutral **rule index** YAML compiled to ASCA (Brassica later); see [Pipeline stages (new)](#pipeline-stages-new), [ADRs 0001–0006](./adr/), [0010](./adr/0010-historical-fidelity-class-first-status.md) |
| **Sound-change evolution** | [05_01_apply_sound_changes.ipynb](../notebooks/05_01_apply_sound_changes.ipynb) (partial); applier integration in package | Ordered **sound-change sequences** applied to lexicon (and related language state) across historical steps |
| **Generative rule sequences** | Not started | Model-proposed sound-change sequences from the rule index ([Future Work in CONLANGER.md](./CONLANGER.md#future-work), [ticket](../.scratch/sound-change-sequences/issues/01-generative-sound-change-sequences.md)) |
| **Outputs** | Not started | Translations at chosen historical periods; formal grammar document (HTML/PDF); sample audio (WAV) |

## Related docs

- [CONLANGER.md](./CONLANGER.md) — narrative background and notebook walkthrough
- [CONTEXT.md](../CONTEXT.md) — domain glossary
- [docs/adr/](./adr/) — architectural decisions
