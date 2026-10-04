import pytest
from lxml import html

from conlanger.utils.parsing import (
    build_stages_from_spine,
    extract_missing_arrow_rule_parts,
    normalize_sub_tags,
    parse_section_heading,
    split_env_exception,
    split_input_output,
    split_output_rest,
    split_post_arrow,
    strip_leading_index_list_marker,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("dz ʃ tʃ → ʒ s₁ s₂", ("dz ʃ tʃ", "ʒ s₁ s₂")),
        ("t → ∅ / _s#", ("t", "∅ / _s#")),
        ("w → ∅ / #C_V, except _i(ː)", ("w", "∅ / #C_V, except _i(ː)")),
        ("dʒ → tʃ → ʃ", ("dʒ", "tʃ → ʃ")),
        ("a →ə / _#", ("a", "ə / _#")),
        ("∅→ n / #_iN", ("∅", "n / #_iN")),
        ("no arrow here", None),
    ],
)
def test_split_input_output(raw, expected):
    assert split_input_output(raw) == expected


@pytest.mark.parametrize(
    "post_arrow, expected",
    [
        ("ʒ s₁ s₂", ("ʒ s₁ s₂", None)),
        ("∅ / _s#", ("∅", "_s#")),
        ("∅ / #C_V", ("∅", "#C_V")),
        ("tʃ → ʃ", ("tʃ → ʃ", None)),
        ("a / b / c", ("a", "b / c")),
        ("∅/ _#", ("∅", "_#")),
        ("p/ #_C[+sibilant]", ("p", "#_C[+sibilant]")),
        (
            "š (Alex Fink says that the realization of /š/ “is unclear”)",
            ("š (Alex Fink says that the realization of /š/ “is unclear”)", None),
        ),
        ("h #_", ("h #_", None)),
        ("∅ VC_CV", ("∅ VC_CV", None)),
        ("c& _", ("c& _", None)),
        ("ej (əw)", ("ej (əw)", None)),
        ("({C,#}Vː)∅", ("({C,#}Vː)∅", None)),
        ("∅ /{a,E}_", ("∅", "{a,E}_")),
        ("p /#_C[+sibilant]", ("p", "#_C[+sibilant]")),
    ],
)
def test_split_output_rest(post_arrow, expected):
    assert split_output_rest(post_arrow) == expected


@pytest.mark.parametrize(
    "rest, expected",
    [
        ("_s#", ("_s#", None)),
        ("!V_", (None, "V_")),
        ("! V_", (None, "V_")),
        ("_# ! k(ː)_", ("_#", "k(ː)_")),
        ("#C_V, except _i(ː)", ("#C_V", "_i(ː)")),
        ("except in several words", (None, "in several words")),
        ("_V(…V) except in #U", ("_V(…V)", "in #U")),
        ("_əNS / #_", ("_əNS", "#_")),
        ("", (None, None)),
        ("    ", (None, None)),
    ],
)
def test_split_env_exception(rest, expected):
    assert split_env_exception(rest) == expected


@pytest.mark.parametrize(
    "heading, expected",
    [
        ("1.0 Proto-IndoEuropean to Klingon", ("1.0", "Proto-IndoEuropean to Klingon")),
        ("Title only", ("", "Title only")),
    ],
)
def test_parse_section_heading_without_index(heading, expected):
    assert parse_section_heading(heading) == expected


@pytest.mark.parametrize(
    "html_text, expected",
    [
        ("<p>before<sub>2</sub>after</p>", "before₂after"),
        ("<p>before<sub>2</sub></p>", "before₂"),
    ],
)
def test_normalize_sub_tags(html_text, expected):
    el = html.fragment_fromstring(html_text)
    assert normalize_sub_tags(el).text == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("— j w → i u / #_CV", "j w → i u / #_CV"),
        ("— aː → oː", "aː → oː"),
        ("— {o,u}(ː) → iː", "{o,u}(ː) → iː"),
        ("j w → i u", "j w → i u"),
        ("", ""),
    ],
)
def test_strip_leading_index_list_marker(text, expected):
    assert strip_leading_index_list_marker(text) == expected


def test_build_stages_from_spine_splits_remaining_arrows():
    assert build_stages_from_spine("dʒ", "tʃ → ʃ") == ["dʒ", "tʃ", "ʃ"]


def test_extract_missing_arrow_rule_parts():
    assert extract_missing_arrow_rule_parts("no arrow here") == {
        "stages": ["no arrow here"]
    }
    assert extract_missing_arrow_rule_parts("a to b / _#") == {
        "stages": ["a to b"],
        "env": "_#",
    }
    assert extract_missing_arrow_rule_parts("a to b / _# ! V_") == {
        "stages": ["a to b"],
        "env": "_#",
        "exception": "V_",
    }


@pytest.mark.parametrize(
    "post_arrow, expected",
    [
        ("ʒ s₁ s₂", ("ʒ s₁ s₂", None, None)),
        ("∅ / _s#", ("∅", "_s#", None)),
        ("ʃ / !V_", ("ʃ", None, "V_")),
        ("∅ / _# ! k(ː)_", ("∅", "_#", "k(ː)_")),
        ("∅ / #C_V, except _i(ː)", ("∅", "#C_V", "_i(ː)")),
        ("ʔ / except in several words", ("ʔ", None, "in several words")),
        (
            "ou øy ei, except in certain endings",
            ("ou øy ei", None, "in certain endings"),
        ),
        ("{∅,h} / _əNS / #_", ("{∅,h}", "_əNS", "#_")),
        ("∅/ _# ! V[-long]C_#", ("∅", "_#", "V[-long]C_#")),
    ],
)
def test_split_post_arrow(post_arrow, expected):
    assert split_post_arrow(post_arrow) == expected
