import pytest

from conlanger.tools.compile.asca.apostrophes import normalize_typographic_apostrophes
from conlanger.tools.compile.asca.ejectives import normalize_asca_ejective_marks
from conlanger.tools.compile.asca.ellipsis import (
    normalize_asca_optional_grouping_ellipsis,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("_(C…)", "_(C,0)"),
        ("o(C…)_(C…)#", "o(C,0)_(C,0)#"),
        ("_(C…)i", "_(C,0)i"),
        ("_(C...)", "_(C,0)"),
        ("_(C..)", "_(C,0)"),
        ("_(V…)", "_(V,0)"),
        ("_(%…)", "_(%,0)"),
        ("_(S…)", "_(S,0)"),
        ("_C(C…)i#", "_C(C,0)i#"),
        ("e > i / _(C…)i(C…)#", "e > i / _(C,0)i(C,0)#"),
        ("V_(VC…)", "V_(VC,0)"),
        ("ə(C…?)_", "ə(C,0)_"),
        ("_C(…C){a,e}", "_C(..)C{a,e}"),
        ("_V(…V)", "_V(..)V"),
        ("a", "a"),
        ("", ""),
        ("[+hi](C…)", "[+hi](C,0)"),
    ],
)
def test_normalize_asca_optional_grouping_ellipsis(text, expected):
    assert normalize_asca_optional_grouping_ellipsis(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{O:[+delrel],O\u2019}", "{O:[+delrel],O\u02bc}"),
        ("C\u2019 > C", "C\u02bc > C"),
        ("\u2019p \u2019t", "p\u02bc t\u02bc"),
        ("p(\u2019) m", "p(\u02bc) m"),
        (
            "ts ts:[+cg] > {\u03b8,s} \u03b8\u2019",
            "ts ts:[+cg] > {\u03b8,s} \u03b8\u02bc",
        ),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_typographic_apostrophes(text, expected):
    assert normalize_typographic_apostrophes(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ts:[+long]ʼ", "ts:[+long,+cg]"),
        ("tʃ:[+long]ʼ > tʃ:[+long]", "tʃ:[+long,+cg] > tʃ:[+long]"),
        ("dʒ > {tʃ:[+long]ʼ,dʒ}", "dʒ > {tʃ:[+long,+cg],dʒ}"),
        ("{ts:[+long]ʼ,z}", "{ts:[+long,+cg],z}"),
        ("{t,ts}ʼ", "{t:[+cg],ts:[+cg]}"),
        ("dʼ > tʼ", "d:[+cg] > t:[+cg]"),
        ("tʃʼ > tsʼ", "tʃ:[+cg] > ts:[+cg]"),
        ("ts ts:[+long] tsʼ", "ts ts:[+long] ts:[+cg]"),
        ("ts:[+cg]ʼ", "ts:[+cg]"),
        ("t:brokenʼ", "t:broken:[+cg]"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_ejective_marks(text, expected):
    assert normalize_asca_ejective_marks(text) == expected


def test_normalize_asca_ejective_marks_skips_blank_set_members():
    assert normalize_asca_ejective_marks("{t,,ts}ʼ") == "{t:[+cg],ts:[+cg]}"


def test_normalize_asca_ejective_marks_adds_cg_to_set_members_with_features():
    assert normalize_asca_ejective_marks("{ts:[+long]}ʼ") == "{ts:[+long,+cg]}"


def test_normalize_asca_ejective_marks_repairs_malformed_set_member_features():
    assert normalize_asca_ejective_marks("{t:broken}ʼ") == "{t:broken:[+cg]}"
