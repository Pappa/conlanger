"""Tests for Index prose gloss detection and stripping."""

import pytest

from conlanger.utils.gloss import (
    extract_embedded_quoted_gloss_from_field,
    extract_field_wrapped_quoted_gloss_from_field,
    extract_leading_quoted_gloss_from_field,
    extract_semicolon_prose_from_field,
    extract_trailing_gloss_from_field,
    extract_trailing_paren_glosses_from_field,
    extract_trailing_quoted_gloss_from_field,
    extract_uncertainty_qualifier_from_field,
    field_has_uncertainty_qualifier,
    is_gloss_only_rule,
    is_quoted_prose_paragraph,
    paren_inner_is_gloss,
    strip_embedded_quoted_gloss_from_field,
    strip_trailing_gloss_from_field,
    strip_trailing_paren_glosses_from_field,
    strip_trailing_quoted_gloss_from_field,
    strip_uncertainty_qualifier_from_field,
)


@pytest.mark.parametrize(
    ("inner", "expected"),
    [
        ("", True),
        ("   ", True),
        ("https://example.com", True),
        ("www.example.com", True),
        ("foo; bar", True),
        ("p → q", True),
        ("a > b", True),
        ("NB: see citation", True),
        ("NB more notes", True),
        ("Note: residual", True),
        ("note residual", True),
        ("short only", True),
        ("foo, bar", True),
        ("the cat", True),
        ("Albanian", True),
        ("xyz", True),
        ("C…C", False),
        ("C...C", False),
        ("?", False),
        ("ː", False),
        ("kʷ", False),
        ("@", False),
    ],
)
def test_paren_inner_is_gloss_classifies_prose_vs_phonology(inner, expected):
    assert paren_inner_is_gloss(inner) is expected


@pytest.mark.parametrize(
    ("text", "expected_cleaned", "expected_captures"),
    [
        ("", "", []),
        ('V / _# "when stressed"', "V / _#", ['"when stressed"']),
        ('p "?"', 'p "?"', []),
        (
            'p "first gloss" "second gloss"',
            "p",
            ['"second gloss"', '"first gloss"'],
        ),
    ],
)
def test_extract_trailing_quoted_gloss_from_field(
    text, expected_cleaned, expected_captures
):
    cleaned, captures = extract_trailing_quoted_gloss_from_field(text)
    assert cleaned == expected_cleaned
    assert captures == expected_captures


def test_strip_trailing_quoted_gloss_from_field_drops_prose():
    assert strip_trailing_quoted_gloss_from_field('V / _# "when stressed"') == "V / _#"


@pytest.mark.parametrize(
    ("text", "expected_cleaned", "expected_captures"),
    [
        ("", "", []),
        ('"something like /ʒ/"', "", ['"something like /ʒ/"']),
        ('"LIKE"', "", ['"LIKE"']),
        ('"?"', '"?"', []),
    ],
)
def test_extract_field_wrapped_quoted_gloss_from_field(
    text, expected_cleaned, expected_captures
):
    cleaned, captures = extract_field_wrapped_quoted_gloss_from_field(text)
    assert cleaned == expected_cleaned
    assert captures == expected_captures


@pytest.mark.parametrize(
    ("text", "expected_cleaned", "expected_captures"),
    [
        ("", "", []),
        (
            "“when another sibilant is in the word nearby” and leftover",
            "and leftover",
            ["“when another sibilant is in the word nearby”"],
        ),
        ("“short” leftover", "“short” leftover", []),
    ],
)
def test_extract_leading_quoted_gloss_from_field(
    text, expected_cleaned, expected_captures
):
    cleaned, captures = extract_leading_quoted_gloss_from_field(text)
    assert cleaned == expected_cleaned
    assert captures == expected_captures


@pytest.mark.parametrize(
    ("text", "expected_cleaned", "expected_captures"),
    [
        ("", "", []),
        ('V, "short only", _C#', "V_C#", [', "short only",']),
        ('V, "...", _C#', 'V, "...", _C#', []),
        ('p → q "not sure of conditions', "p → q", ['"not sure of conditions']),
        ('foo " x', "foo x", ['"']),
        ('z > d / $_OO"', "z > d / $_OO", ['"']),
    ],
)
def test_extract_embedded_quoted_gloss_from_field(
    text, expected_cleaned, expected_captures
):
    cleaned, captures = extract_embedded_quoted_gloss_from_field(text)
    assert cleaned == expected_cleaned
    assert captures == expected_captures


def test_strip_embedded_quoted_gloss_from_field_drops_prose():
    assert strip_embedded_quoted_gloss_from_field('V, "short only", _C#') == "V_C#"


@pytest.mark.parametrize(
    ("text", "expected_cleaned", "expected_captures"),
    [
        ("", "", []),
        ("_CVC# (short only)", "_CVC#", ["(short only)"]),
        ("k(ʼ)", "k(ʼ)", []),
    ],
)
def test_extract_trailing_paren_glosses_from_field(
    text, expected_cleaned, expected_captures
):
    cleaned, captures = extract_trailing_paren_glosses_from_field(text)
    assert cleaned == expected_cleaned
    assert captures == expected_captures


def test_strip_trailing_paren_glosses_from_field_drops_prose():
    assert strip_trailing_paren_glosses_from_field("_CVC# (short only)") == "_CVC#"


@pytest.mark.parametrize(
    ("text", "expected_cleaned", "expected_captures"),
    [
        ("p → q", "p → q", []),
        (
            "depending on the environment; again, the article is unclear",
            "depending on the environment",
            ["again, the article is unclear"],
        ),
        ("p → q; _#", "p → q; _#", []),
    ],
)
def test_extract_semicolon_prose_from_field(text, expected_cleaned, expected_captures):
    cleaned, captures = extract_semicolon_prose_from_field(text)
    assert cleaned == expected_cleaned
    assert captures == expected_captures


@pytest.mark.parametrize(
    ("text", "expected_cleaned"),
    [
        ("", ""),
        ("_# (except as below)", "_#"),
        ("k(ʼ)", "k(ʼ)"),
        ("(?)", "(?)"),
        ("C(…C)", "C(…C)"),
        ("_{f,s}", "_{f,s}"),
        ("_# when unstressed", "_# when unstressed"),
        (
            "p (some Polynesian languages, such as Levei and Drehet)",
            "p",
        ),
        (
            "f (Common Celtic; I'm not sure of the conditions)",
            "f",
        ),
        (
            "s̩ f̩ (Ōgami) (http://amritas.com/101023.htm#10192359)",
            "s̩ f̩",
        ),
        (
            'ɔa "(except NV:[+front] of the Faroes > a:[+long])"',
            "ɔa",
        ),
        ("tʃ {ɡ,q} (ɡ is more common)", "tʃ {ɡ,q}"),
        (
            "depending on the environment; again, the article is unclear",
            "depending on the environment",
        ),
        (
            "“when another sibilant is in the word nearby” and (word-finally?) when",
            "and (word-finally?) when",
        ),
        (
            (
                "{a,ə} / _{x,h} “in the odd-numbered of any sequence of one or more "
                "short-vowel open syllables”"
            ),
            "{a,ə} / _{x,h}",
        ),
        ("z > d / $_OO “", "z > d / $_OO"),
    ],
)
def test_strip_trailing_gloss_from_field(text, expected_cleaned):
    assert strip_trailing_gloss_from_field(text) == expected_cleaned


def test_extract_trailing_gloss_from_field_returns_captures():
    cleaned, captures = extract_trailing_gloss_from_field("_# (except as below)")
    assert cleaned == "_#"
    assert captures == ["(except as below)"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "\u201cThe PIE rules for the voicing of s \u2192 z, as in [nizdos]\u201d",
            True,
        ),
        ("a \u2192 e / _C", False),
        ('"?"', False),
    ],
)
def test_is_quoted_prose_paragraph(text, expected):
    assert is_quoted_prose_paragraph(text) is expected


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        ({"stages": [], "comment": "editorial"}, True),
        ({"stages": ["p"], "comment": "editorial"}, True),
        ({"stages": ["p", "h"], "comment": "editorial"}, False),
        ({"stages": [], "comment": ""}, False),
        ({"stages": ["p", "h"]}, False),
    ],
)
def test_is_gloss_only_rule(parts, expected):
    assert is_gloss_only_rule(parts) is expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", False),
        ("a", False),
        ("h (sporadic)", True),
    ],
)
def test_field_has_uncertainty_qualifier(text, expected):
    assert field_has_uncertainty_qualifier(text) is expected


@pytest.mark.parametrize(
    ("text", "expected_cleaned", "expected_captures"),
    [
        ("", "", []),
        ("sometimes", "", ["sometimes"]),
        ("occasionally", "", ["occasionally"]),
        ("sporadic, usually {#,V[+front]}_", "{#,V[+front]}_", ["sporadic, usually"]),
        ("h (sometimes uncertain)", "h", ["(sometimes uncertain)"]),
        ("h sometimes", "h", ["sometimes"]),
        ('h "sometimes"', "h", ['"sometimes"']),
        ("∅ (occasionally?)", "∅", ["(occasionally?)"]),
        ("_i, occasionally", "_i", [", occasionally"]),
        (
            'r "in Hieroglyphic Luwian, occasionally"',
            "r",
            ['"in Hieroglyphic Luwian, occasionally"'],
        ),
        ("sometimes in the environment", "sometimes in the environment", []),
    ],
)
def test_extract_uncertainty_qualifier_from_field(
    text, expected_cleaned, expected_captures
):
    cleaned, captures = extract_uncertainty_qualifier_from_field(text)
    assert cleaned == expected_cleaned
    assert captures == expected_captures


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("h (sporadic)", "h"),
        ("_{f,s} (sporadic)", "_{f,s}"),
        ("sporadic, usually {#,V[+front]}_", "{#,V[+front]}_"),
        ("sometimes", ""),
        ('∅ "(sporadic)"', "∅"),
        ("ɛ (sometimes)", "ɛ"),
        ("_# (sporadic?)", "_#"),
        ("∅ (occasionally?)", "∅"),
        ("occasionally", ""),
        ("_i, occasionally", "_i"),
        ("_C (occasionally blocked)", "_C"),
        ("a", "a"),
    ],
)
def test_strip_uncertainty_qualifier_from_field(text, expected):
    assert strip_uncertainty_qualifier_from_field(text) == expected
