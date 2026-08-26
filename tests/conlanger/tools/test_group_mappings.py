import pytest

from conlanger.tools.compile.asca.group_mappings import (
    apply_asca_group_mappings_to_string,
    asca_group_mappings_dict,
    expand_grouping_letter,
)


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("VR", "V[+son,-syll]"),
        ("#_VR", "#_V[+son,-syll]"),
        ("{V,R}", "{V,[+son,-syll]}"),
        ("V_R", "V_[+son,-syll]"),
        ("{Z,C[-voice],r}", "{[+cont],C[-voice],r}"),
        ("#_V{Z,C[-voice],r}", "#_V{[+cont],C[-voice],r}"),
        ("VCH", "VC[-place]"),
        ("E_", "V:[+front]_"),
        ("{j,E}", "{j,V:[+front]}"),
        ("{R,h}", "{[+son,-syll],h}"),
        ("O_ in #U (not universal)", "O_ in #% (not universal)"),
        ("U[+long]", "%[+long]"),
        ("_V[+high +ATR]", "_V[+high +ATR]"),
        ("V[+high +ATR]", "V[+high +ATR]"),
        ("a", "a"),
        ("", ""),
        (
            "Kʷ > K",
            "C:[-front,+back,+hi,-lo,+round] > C:[-front,+back,+hi,-lo]",
        ),
        (
            "Kʷ > K / _V[+round]",
            "C:[-front,+back,+hi,-lo,+round] > C:[-front,+back,+hi,-lo] / _V[+round]",
        ),
        ("Kʷy > ɕ", "C:[-front,+back,+hi,-lo,+round]y > ɕ"),
        (
            "i > ə / {P,K(ʷ),s}_",
            "i > ə / {C:[+labial],C:[-front,+back,+hi,-lo,+round],C:[-front,+back,+hi,-lo],s}_",
        ),
        ("Cʷ > C", "C:[+round] > C"),
        ("Kr > k", "C:[-front,+back,+hi,-lo]r > k"),
        ("rK > k", "rK > k"),
        ("Kw > k", "C:[-front,+back,+hi,-lo]w > k"),
        ("Sʷ", "C:[+labial]"),
        ("X > y", "X > y"),
        ("S > P", "P > C:[+labial]"),
        ("K(ʷ) > k", "{C:[-front,+back,+hi,-lo,+round],C:[-front,+back,+hi,-lo]} > k"),
        ("Qʷ > k", "{C:[-front,+back,-hi,-lo,+round],[+click,+round]} > k"),
        ("e > a / _R", "e > a / _[+son,-syll]"),
        ("e > a / _Ra", "e > a / _[+son,-syll]a"),
        ("SR", "P[+son,-syll]"),
        ("VOR > VːR", "VO[+son,-syll] > Vː[+son,-syll]"),
    ],
)
def test_apply_asca_group_mappings_to_string(input, expected, fx_sample_group_mappings):
    assert (
        apply_asca_group_mappings_to_string(input, fx_sample_group_mappings) == expected
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Tʃ > P:[-voice]P",
            "P:[-voice]ʃ > C:[+labial]:[-voice]C:[+labial]",
        ),
        (
            "{Tʃ,Tʃʷ} > P:[-voice]P",
            "{P:[-voice]ʃ,P:[-voice]ʃʷ} > C:[+labial]:[-voice]C:[+labial]",
        ),
        (
            "C:[+front,+hi,-lo] > Tʃ",
            "C:[+front,+hi,-lo] > P:[-voice]ʃ",
        ),
        (
            "P:[-voice]P Tʃ Tʃʷ C:[-front,+back,+hi,-lo] > P:[-voice][-place] P:[-voice]P Tʂ Tʃ",
            (
                "C:[+labial]:[-voice]C:[+labial] P:[-voice]ʃ P:[-voice]ʃʷ C:[-front,+back,+hi,-lo] > "
                "C:[+labial]:[-voice][-place] C:[+labial]:[-voice]C:[+labial] P:[-voice]ʂ P:[-voice]ʃ"
            ),
        ),
    ],
)
def test_apply_asca_group_mappings_class_letter_before_ipa_tail(text, expected):
    mappings = asca_group_mappings_dict()
    assert apply_asca_group_mappings_to_string(text, mappings) == expected


def test_asca_group_mappings_dict_loads_package_csv():
    mappings = asca_group_mappings_dict()
    assert mappings["R"] == "[+son,-syll]"
    assert mappings["Z"] == "[+cont]"


def test_expand_grouping_letter_leaves_unmapped_non_native_letters():
    assert (
        expand_grouping_letter("X", {"K": "C:[-front,+back,+hi,-lo]"}, labial=False)
        == "X"
    )
    assert (
        expand_grouping_letter("X", {"K": "C:[-front,+back,+hi,-lo]"}, labial=True)
        == "X"
    )
