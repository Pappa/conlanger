"""Tests for editorial slash gloss and prose residue compile transforms (ticket 115)."""

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.editorial_slash_gloss import (
    expand_set_vowel_alternation_slashes,
    normalize_editorial_slash_gloss_residue,
    peel_unclosed_paren_prose,
    strip_editorial_slash_glosses,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{a/e}", "{a,e}"),
        ("{e/a}", "{e,a}"),
        ("{a/e,e/a}", "{a,e,e,a}"),
        ("{a/e,e/a} {j̃,ẽ}", "{a,e,e,a} {j̃,ẽ}"),
        ("_{o,u/y}", "_{o,u,y}"),
        ("C[+voice]/V", "C[+voice]/V"),
    ],
)
def test_expand_set_vowel_alternation_slashes(text, expected):
    assert expand_set_vowel_alternation_slashes(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("if /j/ resulted", "if j resulted"),
        ("dropped after /i/", "dropped after i"),
        ("Original z (/ts/?)", "Original z"),
        (
            "V_ (if /j/ resulted, it dropped after /i/",
            "V_ (if j resulted, it dropped after i",
        ),
    ],
)
def test_strip_editorial_slash_glosses(text, expected):
    assert strip_editorial_slash_glosses(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("V_ (if j resulted, it dropped after i", "V_"),
        ("_n{C,#} (Souletin", "_n{C,#}"),
        ("a_ (usually", "a_"),
        ("V:[+stress]$_(C)(C)V(C)# (", "V:[+stress]$_(C)(C)V(C)#"),
        ("n_ (this is admittedly a bit conjectural", "n_"),
        ("_{C,#} (not sure how this plays in", "_{C,#}"),
    ],
)
def test_peel_unclosed_paren_prose(text, expected):
    assert peel_unclosed_paren_prose(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{a/e} {e/a}", "{a,e} {e,a}"),
        ("ɡ > j / V_ (if /j/ resulted, it dropped after /i/", "ɡ > j / V_"),
        ("_{o,u/y}", "_{o,u,y}"),
        ("Original z (/ts/?)", "Original z"),
    ],
)
def test_normalize_editorial_slash_gloss_residue(text, expected):
    assert normalize_editorial_slash_gloss_residue(text) == expected


@pytest.mark.parametrize(
    ("inp", "out", "env"),
    [
        ("{a/e} {e/a} {j̃,ẽ}", "e a ẽ", None),
        ("{a/e}", "e", None),
        ("{a/e,e/a} {j̃,ẽ}", "a ẽ", None),
        ("ɡ", "{k,j}", "V_ (if /j/ resulted, it dropped after /i/"),
        ("ɡ", "ɡ", "_{o,u/y}"),
        ("Original z (/ts/?)", "dj", None),
        ("o", "u", "_n{C,#} (Souletin"),
        ("i", "∅", "a_ (usually"),
        ("V", "∅", "V:[+stress]$_(C)(C)V(C)# ("),
        ("n̩", "e", "n_ (this is admittedly a bit conjectural"),
        ("iC", "i", "_{C,#} (not sure how this plays in"),
    ],
)
def test_editorial_slash_inventory_representatives_validate(inp, out, env):
    rule: dict[str, object] = {"stages": [inp, out]}
    if env is not None:
        rule["env"] = env
    section = {"index": "18.3.1", "section": "editorial-slash", "rules": [rule]}
    validate_asca(DiachronicSeries(section, "asca"))


def test_compile_pipeline_applies_editorial_slash_normalization():
    compiled = compile_asca_rule_fields(
        "{a/e} {e/a}",
        "e a",
        "V_ (if /j/ resulted, it dropped after /i/",
    )
    assert compiled == "{a,e} {e,a} > e a / V_"
