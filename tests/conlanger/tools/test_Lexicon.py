import pytest
from conlanger.tools import Lexicon


@pytest.mark.parametrize(
    "structure",
    [("(C)V(C)"), ("(C)(G)V(C)"), ("(C)(C)V(C)(C)(C)")],
)
def test_Lexicon_syllable_structure(structure):
    try:
        Lexicon(syllable_structure=structure)
    except ValueError:
        pytest.fail("Unexpected ValueError")


@pytest.mark.parametrize(
    "structure",
    [(""), ("C)(G)V(C)"), ("(C(G)V(C)"), ("(A)(C)V(C)")],
)
def test_Lexicon_syllable_structure_errors(structure):
    with pytest.raises(ValueError, match="Invalid syllable structure"):
        Lexicon(syllable_structure=structure)
