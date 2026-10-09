import pytest

from conlanger.ingest.models.index_models import IndexRule
from conlanger.ingest.utils.prose_position_env import (
    apply_prose_position_env_conditions,
    normalize_bare_prose_position_env,
    strip_trailing_position_qualifiers,
)


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        pytest.param(
            {"env": "adjacent to {S,s,l̥}"},
            {
                "env": "{S,s,l̥}_, _{S,s,l̥}",
                "comment": "adjacent to {S,s,l̥}",
            },
            id="adjacent to set",
        ),
        pytest.param(
            {"env": "_ʔ#, in monosyllables"},
            {
                "env": "_ʔ#",
                "comment": "in monosyllables",
            },
            id="in monosyllables",  # is this correct?
        ),
        pytest.param(
            {"env": "final syllables"},
            {
                "env": "U#",
                "comment": "final syllables",
            },
            id="final syllables",  # is this correct?
        ),
        pytest.param(
            {
                "env": "final syllables",
                "exception": "#U",
            },
            {
                "env": "final syllables",
                "exception": "#U",
            },
            id="deferred when exception is present",  # is this correct?
        ),
        pytest.param(
            {
                "env": "_(C)#, in monosyllables",
                "exception": "#U",
            },
            {
                "env": "_(C)#",
                "exception": "#U",
                "comment": "in monosyllables",
            },
            id="strips qualifier with exception",
        ),
    ],
)
def test_apply_prose_position_env_conditions(input, expected):
    args = {
        "raw": "x",
        "source": "t",
    }
    rule = IndexRule(**args, **input)
    result = apply_prose_position_env_conditions(rule)
    assert result.to_index_dict() == {**expected, **args, "stages": []}


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_captures"),
    [
        ("final syllables", "U#", ["final syllables"]),
        ("in final syllables", "U#", ["in final syllables"]),
        ("syllable-finally", "U#", ["syllable-finally"]),
        ("syllable-final", "U#", ["syllable-final"]),
        ("adjacent to {S,s,l̥}", "{S,s,l̥}_, _{S,s,l̥}", ["adjacent to {S,s,l̥}"]),
        ("adjacent to {P,t}", "{P,t}_, _{P,t}", ["adjacent to {P,t}"]),
        (
            "adjacent to V[+nasal]",
            "V[+nasal]_, _V[+nasal]",
            ["adjacent to V[+nasal]"],
        ),
        ("unstressed syllables", "%[-stress]", ["unstressed syllables"]),
        (
            "accented or stressed monosyllables",
            "#_[+stress]",
            ["accented or stressed monosyllables"],
        ),
        (
            "in accented or stressed monosyllables",
            "#_[+stress]",
            ["in accented or stressed monosyllables"],
        ),
        ("typically near *u", "_,u", ["typically near *u"]),
        (
            "between two vowels of unlike nasality",
            "V_V",
            ["between two vowels of unlike nasality"],
        ),
        ("not universal?", "_", ["not universal?"]),
        ("monosyllables", "#_#", ["monosyllables"]),
        ("_k", "_k", []),
    ],
)
def test_normalize_bare_prose_position_env(text, expected_env, expected_captures):
    env, captures, flags = normalize_bare_prose_position_env(text)
    assert env == expected_env
    assert captures == expected_captures
    if text == "not universal?":
        assert flags == {"sporadic": True}
    else:
        assert flags == {}


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_captures"),
    [
        ("j_#, in monosyllables", "j_#", ["in monosyllables"]),
        ("_#, in polysyllables", "_#", ["in polysyllables"]),
        ("#_, in nouns", "#_", ["in nouns"]),
        ("_ʔ#, in monosyllables", "_ʔ#", ["in monosyllables"]),
    ],
)
def test_strip_trailing_position_qualifiers(text, expected_env, expected_captures):
    env, captures = strip_trailing_position_qualifiers(text)
    assert env == expected_env
    assert captures == expected_captures
