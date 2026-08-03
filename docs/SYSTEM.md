# System map

End-to-end view of the Conlanger pipeline: what each stage does, where it lives today, and what it should produce. Product arc is locked in [ADR-0007](./adr/0007-generative-conlang-pipeline.md).

Most stages still live in **Jupyter notebooks** for exploration and convenience. The target shape is an **automated pipeline** in the `conlanger` package that runs all steps and emits constructed-language artifacts (grammar document, audio, evolved lexicon, and related outputs).

## Pipeline stages

| Stage | Current implementation | Target artifacts |
| --- | --- | --- |
| **Data preparation** | [prepare_phoible_data.ipynb](../notebooks/prepare_phoible_data.ipynb), [prepare_wals_data.ipynb](../notebooks/prepare_wals_data.ipynb) | `notebooks/data/language_phonemes.npz`, `notebooks/data/language_parameters.npz`; later, automated ingest (see [ticket](../.scratch/data-processing-pipeline/issues/01-automate-phoible-wals-prep.md)) |
| **Phoneme inventory generation** | [phoneme_gan.ipynb](../notebooks/phoneme_gan.ipynb); [WGANGP](../src/conlanger/models/WGANGP.py) | GAN-generated inventories; ~100 bundled **preset inventories** in the package ([ADR-0008](./adr/0008-gan-inventories-and-bundled-presets.md), [ticket](../.scratch/phoneme-inventories/issues/01-bundle-100-pregenerated-inventories.md)) |
| **Morphology / grammar parameters** | [wals_parameters_gan.ipynb](../notebooks/wals_parameters_gan.ipynb) | Generated WALS-like parameter sets for grammar/morphology modelling |
| **Lexicon generation** | [word_list.ipynb](../notebooks/word_list.ipynb), [generate_lexicon.ipynb](../notebooks/generate_lexicon.ipynb); [Lexicon](../src/conlanger/tools/Lexicon.py), [SyllableStructure](../src/conlanger/tools/SyllableStructure.py) | Proto-language root lexicon from inventory + phonotactics ([ADR-0009](./adr/0009-lexicon-generate-then-evolve.md)) |
| **Rule corpus (Index Diachronica)** | [IndexDiachronicaParser](../src/conlanger/tools/IndexDiachronicaParser.py), [asca_validator](../src/conlanger/tools/asca_validator.py), [SoundChangeRule](../src/conlanger/tools/SoundChangeRule.py); work under `.scratch/cleaned-rule-corpus/` | Applier-neutral **rule corpus** YAML compiled to ASCA (Brassica later); see [ADRs 0001–0006](./adr/), [0010](./adr/0010-historical-fidelity-class-first-status.md) |
| **Sound-change evolution** | [apply_sound_changes.ipynb](../notebooks/apply_sound_changes.ipynb) (partial); applier integration in package | Ordered **sound-change sequences** applied to lexicon (and related language state) across historical steps |
| **Generative rule sequences** | Not started | Model-proposed sound-change sequences from the rule corpus ([Future Work in CONLANGER.md](./CONLANGER.md#future-work), [ticket](../.scratch/sound-change-sequences/issues/01-generative-sound-change-sequences.md)) |
| **Outputs** | Not started | Translations at chosen historical periods; formal grammar document (HTML/PDF); sample audio (WAV) |

## Exploratory / out of pipeline

| Work | Location | Notes |
| --- | --- | --- |
| Language prediction from phonemes | [predict_languages.ipynb](../notebooks/predict_languages.ipynb) | Sanity check before GAN work; not part of the product pipeline |

## Notebook → package

Notebooks remain the fastest place to experiment. As a stage stabilises, its logic should move into `src/conlanger/` with tests under `tests/`, and the pipeline should invoke package code rather than notebook cells. ADR-0007 explicitly treats the PHOIBLE/WALS prep notebooks as **temporary manual process**, not the long-term data platform.

## Related docs

- [CONLANGER.md](./CONLANGER.md) — narrative background and notebook walkthrough
- [CONTEXT.md](../CONTEXT.md) — domain glossary
- [docs/adr/](./adr/) — architectural decisions
