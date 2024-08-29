import pkgutil
import numpy as np


class SyllableStructure():
    def __init__(self):
        data = pkgutil.get_data(__name__, "../data/syllable_structure.csv")
        self.structures, counts = np.unique(
            np.array([line.split(",") for line in data.decode("utf-8").split("\n")[0:-1]])[1:, 1], 
            return_counts=True)
        self.probabilities = counts / counts.sum()

    def pick(self, weirdness=0.5):
        x = np.min([1.0, np.max([0.0, weirdness])])
        prob = self.probabilities.copy()
        prob[np.random.rand(*prob.shape) < x] += x
        prob /= prob.sum()
        return np.random.choice(self.structures, p=prob)

