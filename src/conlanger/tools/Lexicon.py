import re
import random

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
        max_syllables=3
    ) -> None:
        random.seed(seed)
        self._phonemes = {
            "C": consonants, "V": vowels, "G": glides, "N": nasals
        }
        self._syllable_structure = self._parse_syllable_structure(syllable_structure)
        self._word_list = word_list
        self._style = style
        self._probability = probability
        self._max_syllables = max_syllables


    def _parse_syllable_structure(self, structure: str) -> list[dict]:
        types = "".join(self._phonemes.keys())
        matches = re.findall(r"\([{0}]\)|[{0}]".format(types), structure)

        if len(matches) == 0 or "".join(matches) != structure:
            raise ValueError("Invalid syllable structure")
        
        return [{"type": re.search(r"[{0}]".format(types), c)[0], "optional": len(c) > 1} for c in matches]
    
    def create_syllable(self) -> str:
        syllable = ""
        for c in self._syllable_structure:
            if not c["optional"] or (c["optional"] and random.random() < self._probability):
                syllable += random.choice(self._phonemes[c["type"]])

        return syllable
    
    def create_word(self) -> str:
        return "".join([self.create_syllable() for _ in range(random.randint(1, self._max_syllables))])
