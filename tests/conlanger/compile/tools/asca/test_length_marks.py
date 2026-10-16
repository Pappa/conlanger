"""Compile-time Index length mark → ASCA ``:[+long]`` (tickets 15, 25, 79)."""

import pytest

from conlanger.compile.tools.asca.length_marks import normalize_asca_length_marks


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("aː", "a:[+long]"),
        ("Vː", "V:[+long]"),
        ("tsː", "ts:[+long]"),
        ("pˑ", "p:[+long]"),
        ("tsˑ", "ts:[+long]"),
        ("VNC > VːC[+voiced]", "VNC > V:[+long]C[+voiced]"),
        ("tʷː", "tʷ:[+long]"),
        ("æː", "æ:[+long]"),
        ("{e,ɤ}ː", "{e,ɤ}:[+long]"),
        ("C_C{ː,C}V", "C_C{V:[+long],C}V"),
        ("s:[+long]ː", "s:[+long]"),
        ("0ː", "0:[+long]"),
        ("C=0 V0 > 0ː", "C=0 V0 > 0:[+long]"),
        ("V:[+stress]ː[tone: 51]", "V:[+stress, +long][tone: 51]"),
        ("V:[+stress]ː[-falling tone]", "V:[+stress, +long][-falling tone]"),
        (
            "S:[- voice]ː S:[+ voice]ː → hS S:[- voice]ː",
            "S:[- voice, +long] S:[+ voice, +long] → hS S:[- voice, +long]",
        ),
        ("Vː[tone: 51]", "V:[+long][tone: 51]"),
        ("%ː", "%:[+long]"),
        ("V:[+stress] > V:[+stress]ː", "V:[+stress] > V:[+stress, +long]"),
        ("P[- voice]ː", "P[- voice, +long]"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_length_marks(text, expected):
    assert normalize_asca_length_marks(text) == expected


def test_normalize_asca_length_marks_leaves_parenthesized_to_optional_length_pass():
    """Bare ``(ː)`` is expanded in ``optional_length`` before this pass runs."""
    from conlanger.compile.tools.asca.optional_length import (
        expand_optional_length_in_text,
    )

    assert normalize_asca_length_marks("V3(ː)ʔ") == "V3(ː)ʔ"
    assert expand_optional_length_in_text("V3(ː)ʔ") == "{V3ʔ,V3:[+long]ʔ}"
    assert normalize_asca_length_marks("1:[+stress] ː2") == "1:[+stress] ː2"
    assert (
        normalize_asca_length_marks(
            "{V:[+stress](C)(C)V:[+long],Vː:[+stress](C)(C)V:[+long]}"
        )
        == "{V:[+stress](C)(C)V:[+long],Vː:[+stress](C)(C)V:[+long]}"
    )
