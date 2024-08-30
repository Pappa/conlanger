class Lexicon:

    def __init__(
        self, syllable_structure: str, phonemes=None, word_list=None, weirdness=0.5
    ) -> None:
        self._allowed_phoneme_types = ("C", "V", "G", "N")
        self._syllable_structure = self._parse_syllable_structure(syllable_structure)
        self._phonemes = phonemes
        self._weirdness = weirdness
        self._word_list = word_list

    def _parse_syllable_structure(self, structure: str):
        syllable_structure = []
        optional = False

        if len(structure) == 0:
            raise ValueError("Invalid syllable structure")

        for c in list(structure):
            if c == "(":
                optional = True
            elif c == ")":
                if not optional:
                    raise ValueError("Invalid syllable structure")
                optional = False
            elif c in self._allowed_phoneme_types:
                syllable_structure.append({"type": c, "optional": optional})
            else:
                raise ValueError("Invalid syllable structure")

        return syllable_structure
