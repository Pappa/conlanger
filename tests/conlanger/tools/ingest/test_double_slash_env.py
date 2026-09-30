import pytest

from conlanger.tools.ingest.double_slash_env import (
    apply_double_slash_env_conditions,
    normalize_prose_env_head,
    normalize_prose_exception_or_env_tail,
    split_embedded_double_slash,
)


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        (
            {
                "exception": "adjacent to C",
            },
            {
                "exception": "C_, _C",
                "comment": "adjacent to C",
            },
        ),
        (
            {
                "env": "#_e",
                "exception": "Logudorese",
            },
            {
                "env": "#_e",
                "comment": "Logudorese",
            },
        ),
        (
            {
                "env": "odd syllables",
                "exception": "_{w,j,H}",
            },
            {
                "env": "_",
                "exception": "_{w,j,H}",
                "comment": "odd syllables",
            },
        ),
        (
            {
                "env": "∅",
                "exception": "_#",
            },
            {
                "exception": "_#",
            },
        ),
        (
            {
                "exception": "onset of U[+stress]",
            },
            {
                "exception": "#_U[+stress]",
                "comment": "onset of U[+stress]",
            },
        ),
        (
            {
                "env": "#_",
                "exception": "before an identical vowel",
            },
            {
                "env": "#_",
                "exception": "V_V",
                "comment": "before an identical vowel",
            },
        ),
        (
            {
                "env": "maybe",
                "exception": "_#?",
            },
            {
                "env": "_",
                "exception": "_#",
                "comment": "maybe; ?",
                "sporadic": True,
            },
        ),
        (
            {
                "env": "odd syllables // _{w,j,H}",
            },
            {
                "env": "_",
                "comment": "odd syllables",
            },
        ),
        (
            {
                "env": "#_e // extra gloss",
                "exception": "_{w,j,H}",
            },
            {
                "env": "#_e",
                "exception": "_{w,j,H}",
                "comment": "extra gloss",
            },
        ),
        (
            {
                "exception": "_# (sporadic)",
            },
            {
                "exception": "_#",
                "comment": "(sporadic)",
                "sporadic": True,
            },
        ),
    ],
)
def test_apply_double_slash_env_conditions(parts, expected):
    assert apply_double_slash_env_conditions(parts) == expected


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_captures"),
    [
        ("{a,ɛ}_, typically", "{a,ɛ}_", ["typically"]),
        ("%[-stress]", "_ %[-stress]", ["%[-stress]"]),
        ("unstressed syllables", "_ %[-stress]", ["unstressed syllables"]),
        ("", "", []),
    ],
)
def test_normalize_prose_env_head(text, expected_env, expected_captures):
    env, captures, flags = normalize_prose_env_head(text)
    assert env == expected_env
    assert captures == expected_captures
    assert flags == {}


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_captures"),
    [
        ("adjacent to ŋ", "ŋ_, _ŋ", ["adjacent to ŋ"]),
        ("adjacent to S", "S_, _S", ["adjacent to S"]),
        ("adjacent to C[+voice]", "C[+voice]_, _C[+voice]", ["adjacent to C[+voice]"]),
        ("Logudorese", "", ["Logudorese"]),
        ("onset of U[+stress]", "#_U[+stress]", ["onset of U[+stress]"]),
        ("in onset of %[+stress]", "#_%[+stress]", ["in onset of %[+stress]"]),
        ("penult", "%_", ["penult"]),
        ("final syllables", "U#", ["final syllables"]),
        (
            "#% with the following conditions",
            "#% with the following conditions",
            ["#% with the following conditions"],
        ),
        ("_k, short only)", "_k", ["short only"]),
        ("%[-stress]", "_ %[-stress]", ["%[-stress]"]),
        ("", "", []),
    ],
)
def test_normalize_prose_exception_or_env_tail(text, expected_env, expected_captures):
    env, captures, flags = normalize_prose_exception_or_env_tail(text)
    assert env == expected_env
    assert captures == expected_captures
    assert flags == {}


@pytest.mark.parametrize(
    ("text", "expected_head", "expected_tail"),
    [
        ("odd syllables // _{w,j,H}", "odd syllables", "_{w,j,H}"),
        ("#_e", "#_e", None),
    ],
)
def test_split_embedded_double_slash(text, expected_head, expected_tail):
    assert split_embedded_double_slash(text) == (expected_head, expected_tail)
