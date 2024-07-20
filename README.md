# conlanger

An experiment in automatic Conlang creation. I am a novice Conlanger so this may go nowhere. :D

## Data Preperation

Language [phoneme data](https://raw.githubusercontent.com/phoible/dev/v2.0/data/phoible.csv) was gathered from [phoible.org](https://phoible.org/) and compiled into a 3d numpy array. Only phonemes that could be fit into pre-prepared IPA grids were used: plumonic consonants, non-plumonic consonants and vowels. Phoneme length is indicated:

- 1.0 standard
- 2.0 long

Currently all language dialects available via [phoible.org](https://phoible.org/) are included, but this may bias the results.

Data preperation notebook: [generate_language.ipynb](./notebooks/generate_language.ipynb)

Language phonemes npy file: [language_phonemes.npy](./notebooks/data/language_phonemes.npy)

## Language prediction

Before using a GAN to generate phoneme collections for new languages, I wanted to ensure that it was possible to predict languages by their phonemes.

[Language prediction notebook](./notebooks/predict_languages.ipynb)

