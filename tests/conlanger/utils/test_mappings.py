"""Unit tests for parse-time mapping helpers in ``conlanger.utils.mappings``."""

from __future__ import annotations

import pytest

from conlanger.utils.mappings import (
    FeatureMapping,
    ManualMapping,
    ManualMappingHit,
    ParserConfig,
    apply_feature_mappings,
    apply_ipa_mappings,
    apply_manual_mappings,
    apply_section_mappings,
    normalize_feature_matrices_in_field,
    normalize_ipa_in_field,
)
from tests.fixtures.minimal_mappings import (
    minimal_feature_mappings,
    minimal_ipa_mappings,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("", "", id="empty-text"),
        pytest.param("plain", "plain", id="empty-mappings-no-op"),
        pytest.param("C[+voiced]", "C[+voice]", id="rename-voiced"),
        pytest.param("N[-voiced]", "N[-voice]", id="rename-unvoiced"),
        pytest.param("C[+ sibilant]", "C[+strident]", id="rename-sibilant"),
        pytest.param("u[+short]", "u[-long]", id="rename-invert-short-u"),
        pytest.param("V[-short]", "V[+long]", id="rename-invert-short-v"),
        pytest.param("S[- glottalized]", "S[+place]", id="rename-polarity-glottalized"),
        pytest.param("V[+glottalized]", "V[-place]", id="rename-polarity-plus"),
        pytest.param(
            "_CV[+close-mid](C)#",
            "_CV[-hi,-lo,+tense](C)#",
            id="bundle-close-mid",
        ),
        pytest.param(
            "_CV[+open-mid](C)#",
            "_CV[-hi,-lo,-tense](C)#",
            id="bundle-open-mid",
        ),
        pytest.param("V[-open]", "V[-lo]", id="rename-open"),
        pytest.param("V[-closed]", "V[-hi]", id="rename-closed"),
        pytest.param(
            "C:[+dental]", "C:[+cor,+anterior,+dist]", id="bundle-dental-colon"
        ),
        pytest.param(
            "_C[+dental]", "_C[+cor,+anterior,+dist]", id="bundle-dental-bracket"
        ),
        pytest.param("C:[+alveolar]", "C:[+cor,+anterior,-dist]", id="bundle-alveolar"),
        pytest.param("O:[+palatal]", "O:[+cor,+dist]", id="bundle-palatal-o"),
        pytest.param("_C[+palatal]", "_C[+cor,+dist]", id="bundle-palatal-c"),
        pytest.param("C:[+velar]", "C:[-fr,+bk,+hi,-lo]", id="bundle-velar"),
        pytest.param(
            "C[+velar]_C[+velar]",
            "C[-fr,+bk,+hi,-lo]_C[-fr,+bk,+hi,-lo]",
            id="bundle-velar-twice",
        ),
        pytest.param("Cʷ:[+uvular]", "Cʷ:[-fr,+bk,-hi,-lo]", id="bundle-uvular"),
        pytest.param("short u", "short u", id="no-bracket-unchanged"),
        pytest.param("V[+high tone]", "V[tone: 5]", id="tone-high"),
        pytest.param("V[+low tone]", "V[tone: 1]", id="tone-low"),
        pytest.param("V[+ falling tone]", "V[tone: 51]", id="tone-falling"),
        pytest.param(
            "V:[+long][+low falling tone]",
            "V:[+long][tone: 21]",
            id="tone-low-falling-in-matrix",
        ),
        pytest.param("aː[+high rising tone]", "aː[tone: 35]", id="tone-high-rising"),
        pytest.param("V[+ low tone]", "V[tone: 1]", id="tone-low-spaced"),
        pytest.param("V[+ high tone]", "V[tone: 5]", id="tone-high-spaced"),
        pytest.param("V[- tone]", "V[- tone]", id="tone-negative-polarity-unchanged"),
        pytest.param(
            "V:[-falling tone]", "V:[-falling tone]", id="tone-minus-in-colon-matrix"
        ),
        pytest.param(
            "V:[+stress][-long -falling tone]",
            "V:[+stress][-long -falling tone]",
            id="tone-unmapped-name-unchanged",
        ),
    ],
)
def test_normalize_feature_matrices_in_field(text, expected):
    mappings = minimal_feature_mappings() if text != "plain" else {}
    assert normalize_feature_matrices_in_field(text, mappings) == expected


def test_normalize_feature_matrices_in_field_unknown_kind_unchanged():
    mappings = {
        "weird": FeatureMapping("weird", "unknown_kind", "x", confidence="high"),
    }
    assert normalize_feature_matrices_in_field("C[+weird]", mappings) == "C[+weird]"


@pytest.mark.parametrize(
    ("parts", "mappings", "expected"),
    [
        pytest.param(
            {"stages": ["C[+voiced]", "C[+voice]"]},
            {},
            {"stages": ["C[+voiced]", "C[+voice]"]},
            id="noop-empty-mappings",
        ),
        pytest.param(
            {"stages": ["C[+voiced]", "C[+voice]"]},
            {"voiced": FeatureMapping("voiced", "rename", "voice", confidence="high")},
            {"stages": ["C[+voice]", "C[+voice]"]},
            id="stages",
        ),
        pytest.param(
            {"env": "C[+voiced]_", "exception": "N[-voiced]"},
            {"voiced": FeatureMapping("voiced", "rename", "voice", confidence="high")},
            {"env": "C[+voice]_", "exception": "N[-voice]"},
            id="env-and-exception",
        ),
        pytest.param(
            {"env": "plain"},
            minimal_feature_mappings(),
            {"env": "plain"},
            id="env-with-full-fixture",
        ),
        pytest.param(
            {"exception": "C[+voiced]"},
            {"voiced": FeatureMapping("voiced", "rename", "voice", confidence="high")},
            {"exception": "C[+voice]"},
            id="exception-only-no-stages",
        ),
    ],
)
def test_apply_feature_mappings(parts, mappings, expected):
    assert apply_feature_mappings(parts, mappings) == expected


@pytest.mark.parametrize(
    ("text", "mappings", "expected"),
    [
        pytest.param("Š", {}, "Š", id="no-mappings"),
        pytest.param("", {"Š": "ʃ"}, "", id="empty-text"),
        pytest.param("TŠ", {"Š": "ʃ"}, "Tʃ", id="longest-key-first"),
        pytest.param("Š", {"Š": "ʃ"}, "ʃ", id="single-char"),
        pytest.param(
            "oı̃ > wɛ̃",
            minimal_ipa_mappings(),
            "oj\u0303 > wɛ\u0303",
            id="near-miss-o-tilde",
        ),
        pytest.param(
            "VnV > ṽlṽ",
            minimal_ipa_mappings(),
            "VnV > v\u0303lv\u0303",
            id="near-miss-v-tilde",
        ),
        pytest.param(
            "iC uC > i û / _{C,#}",
            minimal_ipa_mappings(),
            "iC uC > i u / _{C,#}",
            id="near-miss-raised-u",
        ),
        pytest.param(
            "Ṽ > V",
            minimal_ipa_mappings(),
            "v\u0303 > V",
            id="near-miss-capital-v-tilde",
        ),
    ],
)
def test_normalize_ipa_in_field(text, mappings, expected):
    assert normalize_ipa_in_field(text, mappings) == expected


@pytest.mark.parametrize(
    ("parts", "mappings", "expected"),
    [
        pytest.param(
            {"stages": ["Š", "TS"]},
            {},
            {"stages": ["Š", "TS"]},
            id="noop-empty-mappings",
        ),
        pytest.param(
            {"stages": ["TŠ", "TS"], "env": "_{Š}", "exception": "Š_"},
            {"Š": "ʃ"},
            {"stages": ["Tʃ", "TS"], "env": "_{ʃ}", "exception": "ʃ_"},
            id="stages-env-exception",
        ),
        pytest.param(
            {"env": "x"},
            {"x": "y"},
            {"env": "y"},
            id="env-only",
        ),
    ],
)
def test_apply_ipa_mappings(parts, mappings, expected):
    assert apply_ipa_mappings(parts, mappings) == expected


@pytest.mark.parametrize(
    ("text", "section_index", "sections", "expected"),
    [
        pytest.param(
            "*DZ → z",
            "1.0",
            {"1.0": {"*D": "D", "*DZ": "dz"}},
            "dz → z",
            id="longest-from-first",
        ),
        pytest.param(
            "plain", "", {"1.0": {"*D": "D"}}, "plain", id="empty-section-index"
        ),
        pytest.param("plain", "9.9", {}, "plain", id="no-section-row"),
        pytest.param(
            "no token", "1.0", {"1.0": {"*D": "D"}}, "no token", id="token-absent"
        ),
        pytest.param("", "1.0", {"1.0": {"*D": "D"}}, "", id="empty-text"),
        pytest.param(
            "token",
            "1.0",
            {"1.0": {"": "X", "token": "T"}},
            "T",
            id="skips-empty-from-key",
        ),
    ],
)
def test_apply_section_mappings(text, section_index, sections, expected):
    config = ParserConfig(
        ipa_mappings_confidence=frozenset({"high"}),
        section_mappings_sections=sections,
    )
    assert apply_section_mappings(text, section_index, config) == expected


@pytest.mark.parametrize(
    ("text", "mappings", "expected_text", "expected_hits"),
    [
        pytest.param(
            "a → b / _C",
            [ManualMapping(from_text="zzz", to_text="Q", reason="")],
            "a → b / _C",
            [],
            id="miss-unchanged",
        ),
        pytest.param(
            "a → b",
            [ManualMapping(from_text="a → b", to_text="x → y", reason="")],
            "x → y",
            [ManualMappingHit(from_text="a → b", to_text="x → y")],
            id="literal-hit",
        ),
        pytest.param(
            "",
            [ManualMapping(from_text="a", to_text="b", reason="")],
            "",
            [],
            id="empty-text",
        ),
        pytest.param("x", [], "x", [], id="empty-mapping-list"),
        pytest.param(
            "foo123",
            [ManualMapping(from_text="123", to_text="N", reason="", use_regex=True)],
            "fooN",
            [ManualMappingHit(from_text="123", to_text="N")],
            id="regex-hit",
        ),
        pytest.param(
            "keep",
            [ManualMapping(from_text="", to_text="X", reason="")],
            "keep",
            [],
            id="skips-empty-from-text",
        ),
    ],
)
def test_apply_manual_mappings(text, mappings, expected_text, expected_hits):
    working, hits = apply_manual_mappings(text, mappings)
    assert working == expected_text
    assert hits == expected_hits
