import pytest
from conlanger.tools import Lexicon


@pytest.mark.parametrize(
    "weirdness, structure",
    [(0.1, "(C)V(C)"), (0.5, "(C)(G)V(C)"), (1.0, "(C)(C)V(C)(C)(C)")],
)
def test_Lexicon(weirdness, structure):
    try:
        Lexicon(syllable_structure=structure)
    except ValueError:
        pytest.fail("Unexpected ValueError") @ pytest.mark.parametrize(
            "weirdness, structure",
            [(0.1, "(C)V(C)"), (0.5, "(C)(G)V(C)"), (1.0, "(C)(G)V(N)")],
        )


@pytest.mark.parametrize(
    "weirdness, structure",
    [(0.1, ""), (0.5, "C)(G)V(C)"), (1.0, "(A)(C)V(C)")],
)
def test_Lexicon_errors(weirdness, structure):
    with pytest.raises(ValueError, match="Invalid syllable structure"):
        Lexicon(syllable_structure=structure)
