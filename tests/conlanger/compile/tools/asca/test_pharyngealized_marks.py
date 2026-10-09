import pytest

from conlanger.tools.compile.asca.pharyngealized_marks import (
    normalize_asca_pharyngealized_marks,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tˤ", "t:[-atr,+rtr]"),
        ("qˤʷ", "qʷ:[-atr,+rtr]"),
        ("Cˤ", "C:[-atr,+rtr]"),
        ("θˤ kˤ", "θ:[-atr,+rtr] k:[-atr,+rtr]"),
        ("ts:[+long]ˤ", "ts:[+long,-atr,+rtr]"),
        ("{t,ts}ˤ", "{t:[-atr,+rtr],ts:[-atr,+rtr]}"),
        ("tˤ > s", "t:[-atr,+rtr] > s"),
        ("Cˤ > C / {#,V}_V", "C:[-atr,+rtr] > C / {#,V}_V"),
        ("i > a / Cˤ_{q,ɣ,ʕ}", "i > a / C:[-atr,+rtr]_{q,ɣ,ʕ}"),
        ("a:[+long] > a / {Cˤ,w}_#", "a:[+long] > a / {C:[-atr,+rtr],w}_#"),
        ("ts:[-atr,+rtr]ˤ", "ts:[-atr,+rtr]"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_pharyngealized_marks(text, expected):
    assert normalize_asca_pharyngealized_marks(text) == expected


def test_normalize_asca_pharyngealized_marks_skips_blank_set_members():
    assert (
        normalize_asca_pharyngealized_marks("{t,,ts}ˤ")
        == "{t:[-atr,+rtr],ts:[-atr,+rtr]}"
    )


def test_normalize_asca_pharyngealized_marks_adds_features_to_set_members_with_features():
    assert (
        normalize_asca_pharyngealized_marks("{ts:[+long]}ˤ") == "{ts:[+long,-atr,+rtr]}"
    )


def test_normalize_asca_pharyngealized_marks_repairs_malformed_set_member_features():
    assert (
        normalize_asca_pharyngealized_marks("{t:broken}ˤ") == "{t:broken:[-atr,+rtr]}"
    )


def test_normalize_asca_pharyngealized_marks_leaves_bracket_matrices_unchanged():
    assert normalize_asca_pharyngealized_marks("C[+pharyngeal]ˤ") == "C[+pharyngeal]ˤ"
