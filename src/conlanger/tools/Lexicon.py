from dataclasses import dataclass, field
import random
from conlanger.tools import SyllableStructure


@dataclass
class Phoneme:
    token: str


@dataclass
class Syllable:
    phonemes: list[Phoneme]


@dataclass
class Word:
    syllables: list[Syllable]


class Lexicon:
    def __init__(
        self,
        syllable_structure: str,
        consonants=None,
        vowels=None,
        glides=None,
        nasals=None,
        word_list=None,
        style=None,
        probability=0.5,
        seed=None,
        max_syllables=3,
    ) -> None:
        random.seed(seed)
        self._phonemes = {"C": consonants, "V": vowels, "G": glides, "N": nasals}
        self._syllable_structure = self._parse_syllable_structure(syllable_structure)
        self._word_list = word_list
        self._style = style
        self._probability = probability
        self._max_syllables = max_syllables

    def _parse_syllable_structure(self, structure: str) -> SyllableStructure:
        try:
            return SyllableStructure(structure)
        except ValueError as e:
            raise ValueError("Invalid syllable structure") from e

    def create_syllable(self) -> str:
        syllable = ""
        for c in self._syllable_structure:
            if not c.optional or (c.optional and random.random() < self._probability):
                syllable += random.choice(self._phonemes[c.type])

        return syllable

    def create_word(self) -> str:
        return "".join(
            [
                self.create_syllable()
                for _ in range(random.randint(1, self._max_syllables))
            ]
        )
