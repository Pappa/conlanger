import pytest
from conlanger.tools import SyllableStructures, SyllableStructure, SyllableToken


@pytest.mark.parametrize(
    "weirdness, structure",
    [(0.1, "(C)V(C)"), (0.5, "(C)(G)V(C)"), (1.0, "(C)(C)V(C)(C)(C)")],
)
def test_SyllableStructures(weirdness, structure):
    ss = SyllableStructures(seed=0)
    assert ss.pick(weirdness=weirdness) == structure


@pytest.mark.parametrize(
    "structure, optionals",
    [
        ("(C)V(C)", (True, False, True)),
        ("(C)(G)V(C)", (True, True, False, True)),
        ("(C)(C)V(C)(C)(C)", (True, True, False, True, True, True)),
    ],
)
def test_SyllableStructure(structure, optionals):
    ss = SyllableStructure(structure)
    assert str(ss) == ss.structure == structure
    assert repr(ss) == f"SyllableStructure(structure='{structure}')"
    assert len(ss) == len(optionals)
    for idx, token in enumerate(ss):
        assert token.optional == optionals[idx]


@pytest.mark.parametrize(
    "token, optional, expected",
    [
        ("C", True, "(C)"),
        ("C", False, "C"),
    ],
)
def test_SyllableToken(token, optional, expected):
    syllable_token = SyllableToken(type=token, optional=optional)
    assert str(syllable_token) == expected
