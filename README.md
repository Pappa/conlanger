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

Language prediction notebook: [predict_languages.ipynb](./notebooks/predict_languages.ipynb)

Overall, it's difficult because a small number of languages have many training examples while the majority have only 1 or 2. Also, the number of classes is very high relative to the number of training samples (approx 80%). The model tends to juts pick languages with the most samples in the training data. However, it does perform better than random chance and better than just picking one of the 5 most common languages in the training set.

In order to generate synthetic data (ie. new languages), I'll likely need to limit the number of training examples per langage to a small number. Otherwise, the GAN will likely just copy the most common languages in the training set.

