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

    def __iter__(self):
        yield from self.phonemes

    def __len__(self):
        return len(self.phonemes)

    def __str__(self):
        return "".join(list(map(str, self.phonemes)))


@dataclass
class Word:
    syllables: list[Syllable]

    def __str__(self):
        return "".join(list(map(str, self.syllables)))


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
        self._lexicon = []

    def _parse_syllable_structure(self, structure: str) -> SyllableStructure:
        try:
            return SyllableStructure(structure)
        except ValueError as e:
            raise ValueError("Invalid syllable structure") from e

    def create_syllable(self) -> Syllable:
        phonemes = []
        for c in self._syllable_structure:
            if not c.optional or (c.optional and random.random() < self._probability):
                phonemes.append(
                    Phoneme(
                        random.choice(self._phonemes[c.type]),
                        nucleus=not c.optional,
                    )
                )

        return Syllable(phonemes)

    def create_word(self) -> Word:
        return Word(
            [
                self.create_syllable()
                for _ in range(random.randint(1, self._max_syllables))
            ]
        )

    def create(self, word_list=False, count=0):
        if word_list:
            self._word_list = word_list

        word_count = max(len(self._word_list), count)

        if word_count == 0:
            raise ValueError("No word list or count provided")
        self._lexicon = [self.create_word() for _ in range(word_count)]
        return self

    def __iter__(self):
        yield from self._lexicon

    def __len__(self):
        return len(self._lexicon)

    def __str__(self):
        return ",".join(list(map(str, self._lexicon)))
