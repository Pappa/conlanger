"""Tests for Index breve vowel notation → ASCA compile transform (ticket 84)."""

import pytest

from conlanger.compile.tools.asca.breve_marks import normalize_asca_breve_marks


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("iə > j̆ / _C%", "iə > j / _C%"),
        ("ɨə > ɨ̆ / _C%", "ɨə > ɨ / _C%"),
        ("ɨ̆ i̯o > u ə", "ɨ i̯o > u ə"),
        ("ɨ̆ > a / _K", "ɨ > a / _K"),
        ("ɨ̆ə > ɨ̆ / _C%", "ɨə > ɨ / _C%"),
        ("ɛ iɛ > e:[+long] j̆", "ɛ iɛ > e:[+long] j"),
        ("∅ > ə̆ / _{n,r}", "∅ > ə:[-long] / _{n,r}"),
        (
            "ɑ ə ʊ > {æ̆,ă} æ̆ ŏ",
            "ɑ ə ʊ > {æ:[-long],a:[-long]} æ:[-long] o:[-long]",
        ),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_breve_marks(text, expected):
    assert normalize_asca_breve_marks(text) == expected
