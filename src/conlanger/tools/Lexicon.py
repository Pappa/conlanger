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
        weirdness=0.5,
        seed=None
    ) -> None:
        self._phonemes = {
            "C": consonants, "V": vowels, "G": glides, "N": nasals
        }
        self._syllable_structure = self._parse_syllable_structure(syllable_structure)
        self._word_list = word_list
        self._style = style
        self._weirdness = weirdness
        random.seed(seed)


    def _parse_syllable_structure(self, structure: str) -> list[dict]:
        types = "".join(self._phonemes.keys())
        matches = re.findall(r"\([{0}]\)|[{0}]".format(types), structure)

        if len(matches) == 0 or "".join(matches) != structure:
            raise ValueError("Invalid syllable structure")
        
        return [{"type": re.search(r"[{0}]".format(types), c)[0], "optional": len(c) > 1} for c in matches]
    
    def create_syllable(self) -> str:
        syllable = ""
        for c in self._syllable_structure:
            if c.optional and random.random() < self._weirdness:
                pass

