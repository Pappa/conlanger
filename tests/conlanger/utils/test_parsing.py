from pathlib import Path

import pandas as pd
import pytest
from lxml import html

from conlanger.utils.parsing import (
    build_stages_from_spine,
    extract_missing_arrow_rule_parts,
    extract_rule_parts,
    finalize_stages_shape,
    normalize_sub_tags,
    parse_section_heading,
    split_env_exception,
    split_input_output,
    split_output_rest,
    split_post_arrow,
    strip_leading_index_list_marker,
)
from conlanger.utils.symbols import normalize_symbols

_SAMPLED_RULES_CSV = (
    Path(__file__).resolve().parents[2] / "fixtures" / "sound_change_rules.csv"
)


def _extract_rule_parts_for_test(normalized: str):
    parts = extract_rule_parts(normalized)
    if parts is None:
        return extract_missing_arrow_rule_parts(normalized)
    return parts


def _load_sampled_html_rules() -> list[tuple]:
    df = pd.read_csv(_SAMPLED_RULES_CSV, dtype=str, keep_default_na=False)
    if "kind" in df.columns:
        df = df[df["kind"].isin(["", "html_extract"])]
    cases: list[tuple] = []
    for row in df.itertuples(index=False):
        if row.expect_none == "True":
            expected = None
        else:
            normalized = normalize_symbols(strip_leading_index_list_marker(row.raw))
            expected = _extract_rule_parts_for_test(normalized)
        cases.append((row.id, row.raw, expected))
    return cases


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


def test_finalize_stages_shape_preserves_existing_skipped_status():
    assert finalize_stages_shape({"stages": ["a"], "status": "skipped"}) == {
        "stages": ["a"],
        "status": "skipped",
    }


def test_finalize_stages_shape_keeps_short_spine():
    assert finalize_stages_shape({"stages": ["a"], "env": "_#"}) == {
        "env": "_#",
        "stages": ["a"],
    }


def test_finalize_stages_shape_keeps_valid_spine():
    assert finalize_stages_shape({"stages": ["a", " ", "b"]}) == {"stages": ["a", "b"]}


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


def test_extract_rule_parts_strips_leading_list_marker():
    assert extract_rule_parts("— j w → i u / #_CV") == {
        "stages": ["j w", "i u"],
        "env": "#_CV",
    }


def test_extract_rule_parts_splits_chain_into_stages():
    assert extract_rule_parts("dʒ → tʃ → ʃ") == {
        "stages": ["dʒ", "tʃ", "ʃ"],
    }


def test_extract_rule_parts_with_symbol_normalization():
    raw = "a → b / _$%oː"
    assert extract_rule_parts(normalize_symbols(raw)) == {
        "stages": ["a", "b"],
        "env": "_$$oː",
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


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            "w → ∅ / _# ! k(ː)_",
            {"stages": ["w", "∅"], "env": "_#", "exception": "k(ː)_"},
        ),
        (
            "s → ʃ / !V_",
            {"stages": ["s", "ʃ"], "exception": "V_"},
        ),
        ("ɬ → l", {"stages": ["ɬ", "l"]}),
        ("no arrow here", {"stages": ["no arrow here"]}),
        (
            "ʔ → ∅/ _#",
            {"stages": ["ʔ", "∅"], "env": "_#"},
        ),
        (
            "{i,u} → ∅/ _# ! V[-long]C_#",
            {
                "stages": ["{i,u}", "∅"],
                "env": "_#",
                "exception": "V[-long]C_#",
            },
        ),
        (
            "ə → ∅ VC_CV",
            {"stages": ["ə", "∅ VC_CV"]},
        ),
        (
            "χ → h #_",
            {"stages": ["χ", "h #_"]},
        ),
        (
            "∅ → dz → î_V",
            {"stages": ["∅", "dz", "î_V"]},
        ),
        (
            "rt → š (Alex Fink says that the realization of /š/ “is unclear”)",
            {
                "stages": [
                    "rt",
                    "š (Alex Fink says that the realization of /š/ “is unclear”)",
                ]
            },
        ),
        ("r…r → r…∅", {"stages": ["r…r", "r…∅"]}),
    ],
)
def test_extract_rule_parts(raw, expected):
    assert _extract_rule_parts_for_test(raw) == expected


_SAMPLED_HTML_RULE_CASES = _load_sampled_html_rules()


@pytest.mark.parametrize(
    ("case_id", "raw", "expected"),
    _SAMPLED_HTML_RULE_CASES,
    ids=[case_id for case_id, _, _ in _SAMPLED_HTML_RULE_CASES],
)
def test_extract_rule_parts_sampled_html_rules(case_id, raw, expected):
    assert extract_rule_parts(normalize_symbols(raw)) == expected, case_id
