from dataclasses import dataclass, field
import random
from conlanger.tools import SyllableStructure


@dataclass
class Phoneme:
    token: str
    nucleus: bool = False

    def __str__(self):
        return self.token


@dataclass
class Syllable:
    phonemes: list[Phoneme]

    def __str__(self):
        return "".join([str(p) for p in self.phonemes])


@dataclass
class Word:
    syllables: list[Syllable]

    def __str__(self):
        return "".join([str(p) for p in self.syllables])


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

    def create_syllable(self) -> Syllable:
        syllable = []
        for c in self._syllable_structure:
            if not c.optional or (c.optional and random.random() < self._probability):
                syllable.append(
                    Phoneme(
                        random.choice(self._phonemes[c.type]),
                        nucleus=c.optional is False,
                    )
                )

        return Syllable(syllable)

    def create_word(self) -> Word:
        return Word(
            [
                self.create_syllable()
                for _ in range(random.randint(1, self._max_syllables))
            ]
        )
