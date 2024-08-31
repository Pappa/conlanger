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


@pytest.mark.parametrize(
    "structure, consonants, vowels, glides, nasals, expected",
    [
        (
            "(C)V(C)(G)(N)",
            ["b", "d", "k", "l", "p"],
            ["i", "u", "ə"],
            ["j", "w", "ɹ"],
            ["m", "n", "ŋ"],
            "upw",
        ),
        ("(C)V(C)", ["k", "l", "p"], ["i", "ə"], ["w"], ["ŋ"], "əp"),
    ],
)
def test_Lexicon_create_syllable(
    structure, consonants, vowels, glides, nasals, expected
):
    lex = Lexicon(
        syllable_structure=structure,
        consonants=consonants,
        vowels=vowels,
        glides=glides,
        nasals=nasals,
        seed=0,
    )
    syllable = lex.create_syllable()

    assert str(syllable) == expected


@pytest.mark.parametrize(
    "structure, consonants, vowels, glides, nasals, max_syllables, expected",
    [
        (
            "(C)V(C)(G)(N)",
            ["b", "d", "k", "l", "p"],
            ["i", "u", "ə"],
            ["j", "w", "ɹ"],
            ["m", "n", "ŋ"],
            2,
            "upwdəd",
        ),
        ("(C)V(C)", ["k", "l", "p"], ["i", "ə"], ["w"], ["ŋ"], 3, "əplək"),
    ],
)
def test_Lexicon_create_word(
    structure, consonants, vowels, glides, nasals, max_syllables, expected
):
    lex = Lexicon(
        syllable_structure=structure,
        consonants=consonants,
        vowels=vowels,
        glides=glides,
        nasals=nasals,
        seed=0,
        max_syllables=max_syllables,
    )
    word = lex.create_word()

    assert str(word) == expected
