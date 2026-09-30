import pytest

from conlanger.utils.symbols import normalize_stress_marks, normalize_symbols


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#_", "#_"),
        ("∅", "∅"),
        ("_$%oː", "_$$oː"),
        ("$am_w", "$am_w"),
        ("in #”U", "in #U:[+stress]"),
    ],
)
def test_normalize_symbols(text, expected):
    assert normalize_symbols(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("”V → ə", "V:[+stress] → ə"),
        ("k → ɡ / ”V_", "k → ɡ / V:[+stress]_"),
        ("V → ∅ / C”V", "V → ∅ / CV:[+stress]"),
        ("V → i / C”iC_", "V → i / Ci:[+stress]C_"),
        (
            "V:[+stress]ʕ ʕV:[+stress] → aa:[+stress] a”a",
            "V:[+stress]ʕ ʕV:[+stress] → aa:[+stress] aa:[+stress]",
        ),
        ("p k → f ɣ / V_V // ”ə_V", "p k → f ɣ / V_V // ə:[+stress]_V"),
        ("”{i,e}V → jV:[+stress]", "{i:[+stress],e:[+stress]}V → jV:[+stress]"),
        ("au → a / _$”u", "au → a / _$u:[+stress]"),
        ("kʷ → kw / #_”a", "kʷ → kw / #_a:[+stress]"),
        (
            "V → V:[+stress] / _C*”{i,e}V",
            "V → V:[+stress] / _C*{i:[+stress],e:[+stress]}V",
        ),
        ("Ve:[+stress] → ”Vi", "Ve:[+stress] → Vi:[+stress]"),
        ("e → i:[+long] / ”_$ɪ:[+long]#", "e → i:[+long] / _$ɪ:[+stress,+long]#"),
        ("ɛ ɔ → e o / _(”u)#", "ɛ ɔ → e o / _(u:[+stress])#"),
        (
            "{V:[+stress](C)CaCV,VC:[+stress](C)CaCV} → {V”(C)CaCV,VC”(C)CaCV} / _#",
            "{V:[+stress](C)CaCV,VC:[+stress](C)CaCV} → {V:[+stress](C)CaCV,VC:[+stress](C)CaCV} / _#",
        ),
        ('k → ts / “After some syllables"', 'k → ts / “After some syllables"'),
    ],
)
def test_normalize_stress_marks(text, expected):
    assert normalize_stress_marks(text) == expected
