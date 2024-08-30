import numpy as np
from conlanger.data import SYLLABLE_STRUCTURE


class SyllableStructure:
    def __init__(self, seed=None):
        np.random.seed(seed)
        self._structures, counts = np.unique(
            np.array(SYLLABLE_STRUCTURE)[:, 1],
            return_counts=True,
        )
        self._probabilities = counts / counts.sum()

    def pick(self, weirdness=0.5):
        x = np.min([1.0, np.max([0.0, weirdness])])
        prob = self._probabilities.copy()
        prob[np.random.rand(*prob.shape) < x] += x
        prob /= prob.sum()
        return np.random.choice(self._structures, p=prob)
