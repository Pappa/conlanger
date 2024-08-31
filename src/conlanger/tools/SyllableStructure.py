from dataclasses import dataclass, field
import re
import numpy as np
from conlanger.data import SYLLABLE_STRUCTURE

ALL_STRUCTURES = np.array(SYLLABLE_STRUCTURE)


class SyllableStructures:
    def __init__(self, seed=None) -> None:
        np.random.seed(seed)
        self._languages = ALL_STRUCTURES[:, 0]
        self._structures = ALL_STRUCTURES[:, 1]
        self._unique_structures, counts = np.unique(
            self._structures,
            return_counts=True,
        )
        self._probabilities = counts / counts.sum()

    def pick(self, weirdness=0.5):
        x = min(1, max(0, weirdness))
        prob = self._probabilities.copy()
        prob[np.random.rand(*prob.shape) < x] += x
        prob /= prob.sum()
        return np.random.choice(self._unique_structures, p=prob)


@dataclass
class SyllableToken:
    type: str
    optional: bool = False
    valid_types: str = "CVGN"

    def __post_init__(self):
        if self.type not in self.valid_types:
            raise ValueError(f"Invalid type: {self.type}")

    def __str__(self):
        return f"({self.type})" if self.optional else self.type


@dataclass
class SyllableStructure:
    structure: str
    tokens: list[SyllableToken] = field(init=False, repr=False)

    def __post_init__(self):
        self.tokens = self._parse_structure(self.structure)

    def _parse_structure(self, structure: str) -> list[SyllableToken]:
        types = "".join(sorted([x for x in structure if x.isalpha()]))
        matches = re.findall(r"\([{0}]\)|[{0}]".format(types), structure)

        if len(matches) == 0 or "".join(matches) != structure:
            raise ValueError("Invalid syllable structure")

        return [
            SyllableToken(
                type=re.search(r"[{0}]".format(types), c)[0], optional=len(c) > 1
            )
            for c in matches
        ]

    def __iter__(self):
        yield from self.tokens

    def __len__(self):
        return len(self.tokens)

    def __str__(self):
        return "".join([str(t) for t in self.tokens])
