import shutil
from pathlib import Path

import pandas as pd
import pytest
from helpers import default_index_parser
from lxml import html

from conlanger.appliers.asca import validate_asca
from conlanger.scripts.config_loaders import load_parser_config
from conlanger.tools.ingest import (
    write_rule_comment_phrase_summary,
)
from conlanger.tools.ingest.double_slash_env import (
    apply_double_slash_env_conditions,
    normalize_prose_env_head,
    normalize_prose_exception_or_env_tail,
    split_embedded_double_slash,
)
from conlanger.tools.ingest.parser import parse_rule_element
from conlanger.tools.ingest.prose_position_env import (
    apply_prose_position_env_conditions,
    normalize_bare_prose_position_env,
    strip_trailing_position_qualifiers,
)
from conlanger.tools.ingest.section_policy import (
    is_catch_all_else_env,
    resolve_catch_all_else_rules,
)
from conlanger.tools.ingest.transforms import (
    MEDIAL_BOUNDARY_EXCEPTION,
    apply_medial_env_conditions,
    apply_sporadic_qualifier,
    apply_stress_conditions,
    apply_trailing_glosses,
    join_rule_comment,
    normalize_medial_env_field,
    normalize_stress_conditions,
    split_field_semicolon_comment,
    split_line_semicolon_comment,
)
from conlanger.tools.rules import DiachronicSeries
from conlanger.utils.file_io import write_manual_mappings_matched_csv
from conlanger.utils.mappings import (
    FeatureMapping,
    IpaMapping,
    ManualMapping,
    ParserConfig,
    apply_feature_mappings,
    apply_ipa_mappings,
    apply_manual_mappings,
    apply_section_mappings,
    normalize_feature_matrices_in_field,
    normalize_ipa_in_field,
)
from conlanger.utils.parsing import (
    build_stages_from_spine,
    extract_missing_arrow_rule_parts,
    extract_rule_parts,
    extract_text_with_subs,
    finalize_stages_shape,
    normalize_html_sub_tags,
    parse_section_heading,
    split_env_exception,
    split_input_output,
    split_output_rest,
    split_post_arrow,
    strip_leading_index_list_marker,
)
from conlanger.utils.symbols import normalize_stress_marks, normalize_symbols
from tests.fixtures.minimal_mappings import (
    minimal_compiler_config,
    minimal_feature_mappings,
    minimal_ipa_mappings,
)


def _html_fragment(html_snippet: str):
    """Parse HTML fragment after pre-lxml ``<sub>`` normalisation."""
    return html.fragment_fromstring(
        normalize_html_sub_tags(html_snippet),
        create_parent=False,
    )


def _parse_rule_element(el, *, source_file: str, section_index: str = ""):
    """Parse one rule element with package-default injected tables."""
    return parse_rule_element(
        el,
        source_file=source_file,
        section_index=section_index,
        parser=default_index_parser(),
    )


_SAMPLED_RULES_CSV = (
    Path(__file__).resolve().parents[3] / "fixtures" / "sound_change_rules.csv"
)

_INDEX_DIACHRONICA_HTML = """\
<!doctype html>
<html>{head}<body>
<section id="{section_id}">
{section_body}
</section>
</body></html>
"""


def _write_index_diachronica_html(
    path: Path,
    *,
    section_id: str,
    section_body: str,
    charset: bool = False,
) -> None:
    head = '<head><meta charset="utf-8"></head>' if charset else ""
    path.write_text(
        _INDEX_DIACHRONICA_HTML.format(
            head=head,
            section_id=section_id,
            section_body=section_body,
        ),
        encoding="utf-8",
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
    ],
)
def test_split_env_exception(rest, expected):
    assert split_env_exception(rest) == expected


def test_split_env_exception_empty_rest():
    assert split_env_exception("") == (None, None)
    assert split_env_exception("   ") == (None, None)


def test_parse_section_heading_without_index():
    assert parse_section_heading("Intro only") == ("", "Intro only")


def test_extract_text_with_subs_tail_after_sub():
    el = _html_fragment("<p>before<sub>2</sub>after</p>")
    assert extract_text_with_subs(el) == "before₂after"


def test_extract_text_with_subs_no_tail_after_sub():
    el = _html_fragment("<p>before<sub>2</sub></p>")
    assert extract_text_with_subs(el) == "before₂"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#_", "#_"),
        ("∅", "∅"),
        ("_$%oː", "_$$oː"),
        ("$am_w", "$am_w"),
        ("in #”U", "in #U:[+stress]"),
        ("s “(for many speakers)”", "s “(for many speakers)”"),
        ("", ""),
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


def test_parse_rule_element_keeps_chain_without_env():
    el = html.fragment_fromstring(
        '<p class="schg">dʒ → tʃ → ʃ</p>', create_parent=False
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert len(rules) == 1
    assert rules[0] == {
        "stages": ["dʒ", "tʃ", "ʃ"],
        "raw": "dʒ → tʃ → ʃ",
        "source": rules[0]["source"],
    }


def test_parse_rule_element_keeps_chain_with_env():
    el = html.fragment_fromstring(
        '<p class="schg">{θ,l} → r → l / V_V</p>', create_parent=False
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert len(rules) == 1
    assert rules[0]["stages"] == ["{θ,l}", "r", "l"]
    assert rules[0]["env"] == "V_V"


def test_write_rule_comment_phrase_summary(tmp_path: Path):
    doc = {
        "sections": [
            {
                "rules": [
                    {"comment": "when stressed; sporadic in some dialects"},
                    {"comment": "plain gloss"},
                    {"stages": ["a", "b"]},
                ]
            }
        ]
    }
    out = tmp_path / "comment-summary.md"
    count = write_rule_comment_phrase_summary(doc, out)
    text = out.read_text(encoding="utf-8")
    assert count == 2
    assert "when stressed" in text
    assert "sporadic" in text
    assert "plain gloss" in text


def test_write_rule_comment_phrase_summary_empty_doc(tmp_path: Path):
    out = tmp_path / "comment-summary.md"
    count = write_rule_comment_phrase_summary({"sections": []}, out)
    text = out.read_text(encoding="utf-8")
    assert count == 0
    assert "_(none matched)_" in text


def test_apply_sporadic_qualifier():
    assert apply_sporadic_qualifier({"stages": ["p", "h (sporadic)"]}) == {
        "stages": ["p", "h"],
        "sporadic": True,
        "comment": "(sporadic)",
    }


def test_apply_sporadic_qualifier_unchanged_when_no_marker():
    parts = {"stages": ["a", "e"], "env": "_#"}
    assert apply_sporadic_qualifier(parts) == parts


def test_parse_rule_element_marks_sporadic_and_strips_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">p → h (sporadic)</p>', create_parent=False
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert len(rules) == 1
    assert rules[0]["stages"] == ["p", "h"]
    assert rules[0]["sporadic"] is True
    assert "(sporadic)" in rules[0]["comment"]
    assert rules[0]["raw"] == "p → h (sporadic)"


def test_parse_rule_element_strips_sporadic_env_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">qu → w / _{f,s} (sporadic)</p>', create_parent=False
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_{f,s}"
    assert rules[0]["sporadic"] is True


def test_parse_rule_element_marks_occasionally_sporadic_and_strips_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">l → ∅ (occasionally?)</p>', create_parent=False
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert len(rules) == 1
    assert rules[0]["stages"] == ["l", "∅"]
    assert rules[0]["sporadic"] is True
    assert "(occasionally?)" in rules[0]["comment"]
    assert rules[0]["raw"] == "l → ∅ (occasionally?)"


def test_apply_trailing_glosses():
    assert apply_trailing_glosses(
        {"stages": ["j", "p (some Polynesian languages, such as Levei and Drehet)"]}
    ) == {
        "stages": ["j", "p"],
        "comment": "(some Polynesian languages, such as Levei and Drehet)",
    }


def test_apply_trailing_glosses_strips_field_wrapped_gloss_to_comment():
    assert apply_trailing_glosses({"stages": ["hhy", '"something like /ʒ/"']}) == {
        "stages": ["hhy", ""],
        "comment": '"something like /ʒ/"',
    }


def test_parse_rule_element_keeps_gloss_only_output():
    el = html.fragment_fromstring(
        '<p class="schg">hhy \u2192 \u201csomething like /\u0292/\u201d</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert len(rules) == 1
    assert "status" not in rules[0]
    assert rules[0]["stages"] == ["hhy"]
    assert "something like" in rules[0]["comment"]
    assert rules[0]["raw"] == "hhy \u2192 \u201csomething like /\u0292/\u201d"


def test_parse_rule_element_strips_trailing_glosses():
    el = html.fragment_fromstring(
        '<p class="schg">w → f (Common Celtic, I’m not sure of the conditions)</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"] == ["w", "f"]
    assert "Celtic" in rules[0]["comment"]
    assert "Celtic" in rules[0]["raw"]


def test_apply_trailing_glosses_keeps_unclosed_paren_on_env():
    """Env/exception unclosed parens stay paired for compile-time gloss strip."""
    assert apply_trailing_glosses(
        {
            "stages": ["Vn", "ṽ"],
            "env": "_# (seems to have been reverted in most dialects",
            "exception": "for Souletin)",
        }
    ) == {
        "stages": ["Vn", "ṽ"],
        "env": "_# (seems to have been reverted in most dialects",
        "exception": "for Souletin)",
    }


def test_parse_rule_element_keeps_set_and_matrix_parentheticals():
    el = html.fragment_fromstring(
        '<p class="schg">({C,#}V[-long])ʔ → ({C,#}Vː[+falling tone])∅ / _C</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"] == [
        "({C,#}V[-long])ʔ",
        "({C,#}Vː[tone: 51])∅",
    ]
    assert rules[0]["env"] == "_C"
    assert "comment" not in rules[0]


def test_parse_rule_element_keeps_nested_feature_matrix_optionals():
    el = html.fragment_fromstring(
        '<p class="schg">V[+high +ATR](C(V[+high -ATR])) → '
        "#(C)V[-high +ATR](CV[+high +ATR]) / #J[+dorsal -voiced]_</p>",
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"] == [
        "V[+high +atr](C(V[+high -atr]))",
        "#(C)V[-high +atr](CV[+high +atr])",
    ]


def test_parse_rule_element_strips_unclosed_paren_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">d ɡ → t k (may have been part of a more sweeping merger</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"] == ["d ɡ", "t k"]
    assert "sweeping merger" in rules[0]["comment"]
    assert "sweeping merger" in rules[0]["raw"]


def test_parse_rule_element_strips_env_trailing_glosses():
    el = html.fragment_fromstring(
        '<p class="schg">t → k / _s̩ (Ōgami) (http://example.com)</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_s̩"
    assert "Ōgami" in rules[0]["raw"]


def test_parse_rule_element_strips_embedded_quoted_env_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">z → d / “when another sibilant is in the word nearby” and (word-finally?) when</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "and (word-finally?) when"
    assert "sibilant" in rules[0]["raw"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("_C(C), when stressed", "_C(C) when stressed"),
        ("_$, when stressed", "_$ when stressed"),
        ("_N, when unstressed (?)", "_N when unstressed (?)"),
        ("when unstressed", "_ when unstressed"),
        (
            "when stressed unless primarily stressed",
            "_ when stressed unless primarily stressed",
        ),
        ("_# when unstressed", "_#"),
        ("_#, when unstressed", "_#"),
        ("C_# when unstressed", "C_#"),
        ("in open syllables, when stressed", "_ when stressed"),
        ("short only when unstressed", "_ when unstressed"),
        ("_j when stressed", "_j when stressed"),
        ("l_ when unstressed", "l_ when unstressed"),
        ("_#", "_#"),
    ],
)
def test_normalize_stress_conditions(text, expected):
    cleaned, _ = normalize_stress_conditions(text)
    assert cleaned == expected


def test_apply_stress_conditions():
    assert apply_stress_conditions(
        {"stages": ["a", "e"], "env": "_C(C), when stressed"}
    ) == {"stages": ["a", "e"], "env": "_C(C) when stressed"}


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_medial"),
    [
        ("medial", "_", True),
        ("medially", "_", True),
        ("medially,", "_", True),
        ("  Medial  ", "_", True),
        ("when medial", "_", True),
        ("C[-voice]_n, when medial", "C[-voice]_n", True),
        ("_k, when medial", "_k", True),
        ("_#", "_#", False),
        ("ku_", "ku_", False),
    ],
)
def test_normalize_medial_env_field(text, expected_env, expected_medial):
    env, is_medial = normalize_medial_env_field(text)
    assert env == expected_env
    assert is_medial is expected_medial


def test_apply_medial_env_conditions_bare_medial():
    assert apply_medial_env_conditions({"stages": ["t", "r"], "env": "medially"}) == {
        "stages": ["t", "r"],
        "env": "_",
        "exception": MEDIAL_BOUNDARY_EXCEPTION,
    }


def test_apply_medial_env_conditions_structural_when_medial():
    assert apply_medial_env_conditions(
        {"stages": ["m", "β"], "env": "C[-voice]_n, when medial"}
    ) == {
        "stages": ["m", "β"],
        "env": "C[-voice]_n",
        "exception": MEDIAL_BOUNDARY_EXCEPTION,
    }


def test_apply_medial_env_conditions_deferred_env_and_exception():
    parts = {
        "stages": ["b", "h"],
        "env": "medially,",
        "exception": "{r(ʲ),l(ʲ)}_ or _ɡ",
    }
    assert apply_medial_env_conditions(parts) == parts


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_captures"),
    [
        ("final syllables", "U#", ["final syllables"]),
        ("in final syllables", "U#", ["in final syllables"]),
        ("syllable-finally", "U#", ["syllable-finally"]),
        ("syllable-final", "U#", ["syllable-final"]),
        ("next to {S,s,l̥}", "_,{S,s,l̥}", ["next to {S,s,l̥}"]),
        ("adjacent to {P,t}", "_,{P,t}", ["adjacent to {P,t}"]),
        (
            "adjacent to a nasal vowel",
            "_V[+nasal], V[+nasal]_",
            ["adjacent to a nasal vowel"],
        ),
        ("unstressed syllables", "_ %[-stress]", ["unstressed syllables"]),
        (
            "accented or stressed monosyllables",
            "#_[+stress]",
            ["accented or stressed monosyllables"],
        ),
        (
            "in accented or stressed monosyllables",
            "#_[+stress]",
            ["in accented or stressed monosyllables"],
        ),
        ("typically near *u", "_,u", ["typically near *u"]),
        (
            "between two vowels of unlike nasality",
            "V_V",
            ["between two vowels of unlike nasality"],
        ),
        ("not universal?", "_", ["not universal?"]),
        ("monosyllables", "#_#", ["monosyllables"]),
        ("_k", "_k", []),
    ],
)
def test_normalize_bare_prose_position_env(text, expected_env, expected_captures):
    env, captures, flags = normalize_bare_prose_position_env(text)
    assert env == expected_env
    assert captures == expected_captures
    if text == "not universal?":
        assert flags == {"sporadic": True}
    else:
        assert flags == {}


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_captures"),
    [
        ("j_#, in monosyllables", "j_#", ["in monosyllables"]),
        ("_#, in polysyllables", "_#", ["in polysyllables"]),
        ("#_, in nouns", "#_", ["in nouns"]),
        ("_ʔ#, in monosyllables", "_ʔ#", ["in monosyllables"]),
    ],
)
def test_strip_trailing_position_qualifiers(text, expected_env, expected_captures):
    env, captures = strip_trailing_position_qualifiers(text)
    assert env == expected_env
    assert captures == expected_captures


def test_apply_prose_position_env_conditions_final_syllables():
    assert apply_prose_position_env_conditions(
        {"stages": ["a V", "e"], "env": "final syllables"}
    ) == {
        "stages": ["a V", "e"],
        "env": "U#",
        "comment": "final syllables",
    }


def test_apply_prose_position_env_conditions_next_to_set():
    assert apply_prose_position_env_conditions(
        {"stages": ["C[+voice]", "C[-voice]"], "env": "next to {S,s,l̥}"}
    ) == {
        "stages": ["C[+voice]", "C[-voice]"],
        "env": "_,{S,s,l̥}",
        "comment": "next to {S,s,l̥}",
    }


def test_apply_prose_position_env_conditions_structural_monosyllable_qualifier():
    assert apply_prose_position_env_conditions(
        {"stages": ["ɛ", "e"], "env": "_ʔ#, in monosyllables"}
    ) == {
        "stages": ["ɛ", "e"],
        "env": "_ʔ#",
        "comment": "in monosyllables",
    }


def test_split_embedded_double_slash():
    assert split_embedded_double_slash("odd syllables // _{w,j,H}") == (
        "odd syllables",
        "_{w,j,H}",
    )
    assert split_embedded_double_slash("#_e") == ("#_e", None)


def test_normalize_prose_exception_adjacent_to_another_consonant():
    env, captures, flags = normalize_prose_exception_or_env_tail(
        "adjacent to another consonant"
    )
    assert env == "C_,_C"
    assert captures == ["adjacent to another consonant"]
    assert flags == {}


def test_normalize_prose_exception_adjacent_to_single_segment():
    env, captures, _ = normalize_prose_exception_or_env_tail("adjacent to S")
    assert env == "_,S"
    assert captures == ["adjacent to S"]


def test_normalize_prose_exception_dialect_comment():
    env, captures, _ = normalize_prose_exception_or_env_tail("Logudorese")
    assert env == ""
    assert captures == ["Logudorese"]


def test_normalize_prose_env_head_strips_typically():
    env, captures, _ = normalize_prose_env_head("{a,ɛ}_, typically")
    assert env == "{a,ɛ}_"
    assert captures == ["typically"]


def test_normalize_prose_env_head_bare_percent_feature():
    env, captures, _ = normalize_prose_env_head("%[-stress]")
    assert env == "_ %[-stress]"
    assert captures == ["%[-stress]"]


def test_apply_double_slash_env_conditions_javanese_adjacent():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["b", "w"],
            "exception": "adjacent to another consonant",
        }
    ) == {
        "stages": ["b", "w"],
        "exception": "C_,_C",
        "comment": "adjacent to another consonant",
    }


def test_apply_double_slash_env_conditions_sardinian_dialect():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["r", "ur:[+long]"],
            "env": "#_e",
            "exception": "Logudorese",
        }
    ) == {
        "stages": ["r", "ur:[+long]"],
        "env": "#_e",
        "comment": "Logudorese",
    }


def test_apply_double_slash_env_conditions_menominee_odd_syllables():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["æ", "e"],
            "env": "odd syllables",
            "exception": "_{w,j,H}",
        }
    ) == {
        "stages": ["æ", "e"],
        "env": "_",
        "exception": "_{w,j,H}",
        "comment": "odd syllables",
    }


def test_apply_double_slash_env_conditions_void_env():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["{d,j}", "j"],
            "env": "∅",
            "exception": "_#",
        }
    ) == {
        "stages": ["{d,j}", "j"],
        "exception": "_#",
    }


def test_normalize_prose_exception_onset_of_stress():
    env, captures, _ = normalize_prose_exception_or_env_tail("onset of U[+stress]")
    assert env == "#_U[+stress]"
    assert captures == ["onset of U[+stress]"]


def test_normalize_prose_exception_penult():
    env, captures, _ = normalize_prose_exception_or_env_tail("penult")
    assert env == "%_"
    assert captures == ["penult"]


def test_apply_double_slash_env_conditions_onset_exception():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["ʔ", "∅"],
            "exception": "onset of U[+stress]",
        }
    ) == {
        "stages": ["ʔ", "∅"],
        "exception": "#_U[+stress]",
        "comment": "onset of U[+stress]",
    }


def test_apply_double_slash_env_conditions_before_identical_vowel():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["iC aC uC", "Cj Ca Cw"],
            "env": "#_",
            "exception": "before an identical vowel",
        }
    ) == {
        "stages": ["iC aC uC", "Cj Ca Cw"],
        "env": "#_",
        "exception": "V_V",
        "comment": "before an identical vowel",
    }


def test_apply_double_slash_env_conditions_maybe_strips_question_mark():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["tʃ", "s"],
            "env": "maybe",
            "exception": "_#?",
        }
    ) == {
        "stages": ["tʃ", "s"],
        "env": "_",
        "exception": "_#",
        "comment": "maybe",
        "sporadic": True,
    }


def test_normalize_prose_exception_or_env_tail_empty():
    assert normalize_prose_exception_or_env_tail("") == ("", [], {})


def test_normalize_prose_env_head_empty():
    assert normalize_prose_env_head("") == ("", [], {})


def test_normalize_prose_exception_or_env_tail_prose_position():
    env, captures, flags = normalize_prose_exception_or_env_tail("final syllables")
    assert env == "U#"
    assert captures == ["final syllables"]
    assert flags == {}


def test_normalize_prose_env_head_prose_position():
    env, captures, flags = normalize_prose_env_head("unstressed syllables")
    assert env == "_ %[-stress]"
    assert captures == ["unstressed syllables"]
    assert flags == {}


def test_normalize_prose_exception_in_onset_of_stress():
    env, captures, _ = normalize_prose_exception_or_env_tail("in onset of %[+stress]")
    assert env == "#_%[+stress]"
    assert captures == ["in onset of %[+stress]"]


def test_normalize_prose_exception_complex_prose_passthrough():
    text = "#% with the following conditions"
    env, captures, _ = normalize_prose_exception_or_env_tail(text)
    assert env == text
    assert captures == [text]


def test_normalize_prose_exception_broken_short_only_tail():
    env, captures, _ = normalize_prose_exception_or_env_tail("_k, short only)")
    assert env == "_k"
    assert captures == ["short only"]


def test_normalize_prose_exception_bare_percent_feature():
    env, captures, _ = normalize_prose_exception_or_env_tail("%[-stress]")
    assert env == "_ %[-stress]"
    assert captures == ["%[-stress]"]


def test_apply_double_slash_env_conditions_embedded_tail_splits_env_head():
    result = apply_double_slash_env_conditions(
        {
            "stages": ["æ", "e"],
            "env": "odd syllables // _{w,j,H}",
        }
    )
    assert result == {
        "stages": ["æ", "e"],
        "env": "_",
        "comment": "odd syllables",
    }


def test_apply_double_slash_env_conditions_embedded_tail_appends_comment():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["æ", "e"],
            "env": "#_e // extra gloss",
            "exception": "_{w,j,H}",
        }
    ) == {
        "stages": ["æ", "e"],
        "env": "#_e",
        "exception": "_{w,j,H}",
        "comment": "extra gloss",
    }


def test_apply_double_slash_env_conditions_exception_uncertainty_qualifier():
    assert apply_double_slash_env_conditions(
        {
            "stages": ["t", "d"],
            "exception": "_# (sporadic)",
        }
    ) == {
        "stages": ["t", "d"],
        "exception": "_#",
        "comment": "(sporadic)",
        "sporadic": True,
    }


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_double_slash_adjacent_validate_asca():
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    el = html.fragment_fromstring(
        '<p class="schg">b → w / ! adjacent to another consonant</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["exception"] == "C_,_C"
    section = {
        "index": "10.2.4.1",
        "section": "Proto-Malayo-Javanic to Javanese",
        "rules": rules,
    }
    validate_asca(
        DiachronicSeries(section, compiler_config=minimal_compiler_config()),
        probe_words=probe,
    )


def test_apply_prose_position_env_conditions_deferred_when_exception_present():
    parts = {
        "stages": ["V", "V:[+long]"],
        "env": "final syllables",
        "exception": "#U",
    }
    assert apply_prose_position_env_conditions(parts) == parts


def test_apply_prose_position_env_conditions_strips_qualifier_with_exception():
    assert apply_prose_position_env_conditions(
        {
            "stages": ["V", "V:[+long]"],
            "env": "_(C)#, in monosyllables",
            "exception": "#U",
        }
    ) == {
        "stages": ["V", "V:[+long]"],
        "env": "_(C)#",
        "exception": "#U",
        "comment": "in monosyllables",
    }


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_prose_position_env_validate_asca():
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    el = html.fragment_fromstring(
        '<p class="schg">C[+voice] → C[-voice] / next to {S,s,l̥}</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_,{S,s,l̥}"
    section = {
        "index": "15.2.7",
        "section": "Proto-Eskimo to Siberian Yup’ik",
        "rules": rules,
    }
    validate_asca(
        DiachronicSeries(section, compiler_config=minimal_compiler_config()),
        probe_words=probe,
    )


def test_parse_rule_element_proto_italic_medial_comment_unchanged():
    el = html.fragment_fromstring(
        '<p class="schg">s → z / medial (I\'m assuming between vowels or when *s voiced in PIE)</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_"
    assert rules[0]["exception"] == MEDIAL_BOUNDARY_EXCEPTION
    assert "between vowels" in rules[0]["comment"]
    assert "medial" in rules[0]["raw"]


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_medial_validate_asca():
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    el = html.fragment_fromstring(
        '<p class="schg">t → r / medially</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    section = {"index": "6.2.1.1.2", "section": "Proto-Agaw to Blin", "rules": rules}
    validate_asca(
        DiachronicSeries(section, compiler_config=minimal_compiler_config()),
        probe_words=probe,
    )


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_medial_with_exception_env_normalized():
    el = html.fragment_fromstring(
        '<p class="schg">b → h / medially, ! {r(ʲ),l(ʲ)}_ or _ɡ</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_"
    assert rules[0]["exception"] == "{r(ʲ),l(ʲ)}_ or _ɡ"
    assert "medially" in rules[0]["comment"]


def test_is_catch_all_else_env():
    assert is_catch_all_else_env("else")
    assert is_catch_all_else_env("else?")
    assert is_catch_all_else_env("  else  ")
    assert not is_catch_all_else_env("else (rarely)")
    assert not is_catch_all_else_env("_# else")
    assert not is_catch_all_else_env("if ɑ is elsewhere in the word")


def test_resolve_catch_all_else_empty_rules():
    assert resolve_catch_all_else_rules([]) == []


def test_resolve_catch_all_else_paren_gloss_only_env():
    rules = [
        {"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"},
        {"stages": ["c", "d"], "env": "(else)", "raw": "c → d / (else)"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert "env" not in resolved[1]
    assert resolved[1]["comment"] == "(else)"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_complementary_pair():
    rules = [
        {"stages": ["kʼ", "{χʷ,qʷ}"], "env": "#_", "raw": "kʼ → {χʷ,qʷ} / #_"},
        {"stages": ["kʼ", "q"], "env": "else", "raw": "kʼ → q / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[0]["env"] == "#_"
    assert "exception" not in resolved[0]
    assert "env" not in resolved[1]
    assert resolved[1]["exception"] == "#_"
    assert resolved[1]["raw"] == "kʼ → q / else"


def test_resolve_catch_all_else_gloss_then_resolve():
    rules = [
        {"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"},
        {
            "stages": ["β", "f"],
            "env": "else (rarely)",
            "raw": "β → f / else (rarely)",
        },
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert "env" not in resolved[1]
    assert resolved[1]["exception"] == "#_"
    assert resolved[1]["comment"] == "(rarely)"


def test_resolve_catch_all_else_cascade_uses_immediate_prev_only():
    rules = [
        {"stages": ["a", "x"], "env": "A", "raw": "a → x / A"},
        {"stages": ["b", "y"], "env": "B", "raw": "b → y / B"},
        {"stages": ["c", "z"], "env": "else", "raw": "c → z / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[2]["exception"] == "B"
    assert "env" not in resolved[2]


def test_resolve_catch_all_else_deferred_prev_env_and_exception():
    rules = [
        {
            "stages": ["p", "∅"],
            "env": "C_",
            "exception": "s_",
            "raw": "p → ∅ / C_ ! s_",
        },
        {"stages": ["p", "kʷ"], "env": "else", "raw": "p → kʷ / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "else"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_deferred_prev_neither():
    rules = [
        {"stages": ["a", "ɑː"], "raw": "a → ɑː"},
        {"stages": ["a", "æ"], "env": "else", "raw": "a → æ / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "else"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_deferred_else_after_else():
    rules = [
        {
            "stages": ["aɪ", "ɑeː"],
            "env": "else",
            "comment": "only for some speakers",
            "raw": "aɪ → ɑeː / else (only for some speakers)",
        },
        {
            "stages": ["aɪ", "aː"],
            "env": "else",
            "comment": "only for some speakers",
            "raw": "aɪ → aː / else (only for some speakers)",
        },
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "else"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_leaves_non_catch_all_fragments():
    rules = [
        {"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"},
        {"stages": ["c", "d"], "env": "_# else", "raw": "c → d / _# else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "_# else"
    assert "exception" not in resolved[1]


def test_parser_resolves_catch_all_else_in_section(tmp_path: Path):
    html_path = tmp_path / "else.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Else",
        section_body="""\
<h2>1.0 Test Section</h2>
<p class="schg">kʼ → {χʷ,qʷ} / #_</p>
<p class="schg">kʼ → q / else</p>""",
    )
    rules = default_index_parser().parse(html_path)["sections"][0]["rules"]
    assert rules[0]["env"] == "#_"
    assert "env" not in rules[1]
    assert rules[1]["exception"] == "#_"
    assert rules[1]["raw"] == "kʼ → q / else"


def test_parse_rule_element_normalizes_stress_conditions():
    el = html.fragment_fromstring(
        '<p class="schg">a → i / _C(C), when stressed</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_C(C) when stressed"
    assert ", when stressed" in rules[0]["raw"]


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_stress_conditions_validate_asca():
    cases = [
        '<p class="schg">a → i / _C(C), when stressed</p>',
        '<p class="schg">{u,a,i} → ∅ / _%, when stressed (short only)</p>',
        '<p class="schg">e oj ɛa → i u ɛ / when unstressed</p>',
        '<p class="schg">e → i / l_ when unstressed</p>',
    ]
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    for html_snippet in cases:
        el = html.fragment_fromstring(html_snippet, create_parent=False)
        rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
        section = {
            "index": "47.1",
            "section": "Stress conditions",
            "rules": rules,
        }
        validate_asca(
            DiachronicSeries(section, compiler_config=minimal_compiler_config()),
            probe_words=probe,
        )


def test_extract_rule_parts_with_symbol_normalization():
    raw = "a → b / _$%oː"
    assert extract_rule_parts(normalize_symbols(raw)) == {
        "stages": ["a", "b"],
        "env": "_$$oː",
    }


def test_parser_preserves_class_letters(tmp_path: Path):
    html_path = tmp_path / "mapped.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Mapped",
        section_body="""\
<h2>1.0 Test Section</h2>
<p class="schg">S → a</p>""",
    )
    doc = default_index_parser().parse(html_path)
    assert "abbreviations" not in doc
    assert doc["sections"][0]["rules"][0]["stages"][0] == "S"


def test_parser_skips_section_without_h2(tmp_path: Path):
    html_path = tmp_path / "no_h2.html"
    _write_index_diachronica_html(
        html_path,
        section_id="NoH2",
        section_body='<p class="schg">a → b</p>',
    )
    assert default_index_parser().parse(html_path)["sections"] == []


def test_parser_skips_section_with_empty_name(tmp_path: Path):
    html_path = tmp_path / "empty_name.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Empty",
        section_body="""\
<h2>   </h2>
<p class="schg">a → b</p>""",
    )
    assert default_index_parser().parse(html_path)["sections"] == []


def test_parser_skips_empty_paragraph(tmp_path: Path):
    html_path = tmp_path / "empty_p.html"
    _write_index_diachronica_html(
        html_path,
        section_id="EmptyP",
        section_body="""\
<h2>1.0 Test Section</h2>
<p>   </p>
<p class="schg">a → b</p>""",
    )
    doc = default_index_parser().parse(html_path)
    sec = doc["sections"][0]
    assert sec["rules"][0]["stages"][0] == "a"
    assert "comments" not in sec


def test_parser_citation_only_section(tmp_path: Path):
    html_path = tmp_path / "citation_only.html"
    _write_index_diachronica_html(
        html_path,
        section_id="CitationOnly",
        section_body="""\
<h2>1.0 Test Section</h2>
<p>Only a citation line.</p>""",
    )
    sec = default_index_parser().parse(html_path)["sections"][0]
    assert sec["citation"] == "Only a citation line."
    assert "rules" not in sec


def test_parser_marks_skip_sections_from_config(tmp_path: Path):
    html_path = tmp_path / "skip_section.html"
    config_path = tmp_path / "parser_config.yml"
    config_path.write_text(
        "ipa_mappings:\n  confidence: [high]\n"
        "skip_sections:\n"
        '  - id: "9.9.9"\n'
        '    reason: "test skip"\n',
        encoding="utf-8",
    )
    for name, content in [
        ("ipa_mappings.yml", "{}\n"),
        ("manual_mappings.yml", "[]\n"),
        ("feature_mappings.yml", "{}\n"),
        ("index_diachronica_corrections.yml", "rules: []\n"),
    ]:
        (tmp_path / name).write_text(content, encoding="utf-8")
    _write_index_diachronica_html(
        html_path,
        section_id="SkipMe",
        section_body="""\
<h2>9.9.9 Skipped Section</h2>
<p class="schg">a → b</p>""",
    )
    parser = default_index_parser(
        parser_config=load_parser_config(config_path),
    )
    sec = parser.parse(html_path)["sections"][0]
    assert sec["index"] == "9.9.9"
    assert sec["status"] == "skipped"
    assert sec["rules"][0]["stages"] == ["a", "b"]
    assert "status" not in sec["rules"][0]


def test_parser_unlisted_section_not_marked_skipped(tmp_path: Path):
    html_path = tmp_path / "active_section.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Active",
        section_body="""\
<h2>1.0 Active Section</h2>
<p class="schg">a → b</p>""",
    )
    sec = default_index_parser().parse(html_path)["sections"][0]
    assert "status" not in sec


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


def test_parse_rule_element_with_sub_and_env():
    el = _html_fragment('<p class="schg">ʃ → s<sub>2</sub> / {i,j}_</p>')
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["ʃ", "s₂"]
    assert rule["env"] == "{i,j}_"
    assert rule["raw"] == "ʃ → s₂ / {i,j}_"
    assert rule["source"].startswith("index_diachronica_original.html:")
    assert "status" not in rule


def test_parse_rule_element_with_exception():
    el = html.fragment_fromstring(
        '<p class="schg">w → ∅ / #C_V, except _i(ː)</p>', create_parent=False
    )
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["w", "∅"]
    assert rule["env"] == "#C_V"
    assert rule["exception"] == "_i(ː)"


def test_parse_rule_element_no_env():
    el = html.fragment_fromstring('<p class="schg">ɬ → l</p>', create_parent=False)
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["ɬ", "l"]
    assert "env" not in rule
    assert "exception" not in rule


def test_parse_rule_element_missing_arrow():
    el = html.fragment_fromstring(
        '<p class="schg">a to b no arrow</p>', create_parent=False
    )
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["a to b no arrow"]
    assert "status" not in rule


def test_parse_rule_element_missing_arrow_with_env_exception_comment():
    el = html.fragment_fromstring(
        '<p class="schg">a to b no arrow / _# ! V_ ; editorial note</p>',
        create_parent=False,
    )
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["a to b no arrow"]
    assert rule["env"] == "_#"
    assert rule["exception"] == "V_"
    assert rule["comment"] == "editorial note"
    assert "status" not in rule


def test_parse_rule_element_arrow_without_spaces():
    el = html.fragment_fromstring(
        '<p class="schg">a \u2192\u0259 / _#</p>', create_parent=False
    )
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["a", "ə"]
    assert rule["env"] == "_#"
    assert "status" not in rule


def test_parse_rule_element_bang_exception():
    el = html.fragment_fromstring(
        '<p class="schg">s \u2192 \u0283 / !V_</p>', create_parent=False
    )
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["s", "ʃ"]
    assert "env" not in rule
    assert rule["exception"] == "V_"


def test_parse_rule_element_env_and_bang_exception():
    el = html.fragment_fromstring(
        '<p class="schg">w \u2192 \u2205 / _# ! k(\u02d0)_</p>', create_parent=False
    )
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["w", "∅"]
    assert rule["env"] == "_#"
    assert rule["exception"] == "k(ː)_"


def test_parse_rule_element_except_without_comma():
    el = html.fragment_fromstring(
        '<p class="schg">q \u2192 \u0294 / except in several words</p>',
        create_parent=False,
    )
    rule = _parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["stages"] == ["q", "ʔ"]
    assert "env" not in rule
    assert rule["exception"] == "in several words"


def test_first_p_is_citation_rest_comments(tmp_path: Path):
    html_path = tmp_path / "sample.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Bench",
        charset=True,
        section_body="""\
<h2>6.1.1.1 North Omotic to Bench</h2>
<p><i>Mecislau</i>, from Ehret (1995), Title</p>
<p>NB: Does not include vowel developments.</p>
<p class="schg">x<sub>1</sub> \u2192 k</p>
<p>Interleaved note</p>
<p class="schg">\u026c \u2192 l</p>""",
    )
    doc = default_index_parser().parse(html_path, source_file="sample.html")
    sec = doc["sections"][0]
    assert sec["citation"] == "Mecislau, from Ehret (1995), Title"
    assert [c["raw"] for c in sec["comments"]] == [
        "NB: Does not include vowel developments.",
        "Interleaved note",
    ]
    assert len(sec["rules"]) == 2
    assert sec["rules"][0]["stages"] == ["x₁", "k"]
    assert sec["rules"][0]["raw"] == "x₁ → k"


def test_parse_expands_collective_series_tokens(tmp_path: Path):
    html_path = tmp_path / "collective.html"
    html_path.write_text(
        """<!doctype html>
<html><body>
<section id="Test">
<h2>1.0 Test</h2>
<p class="schg" id="Test-sx">sₓ → ʃ</p>
<p class="schg" id="Test-Hx">{Hₓ,m̩,n̩} → a</p>
</section>
</body></html>""",
        encoding="utf-8",
    )
    doc = default_index_parser().parse(html_path, source_file="collective.html")
    rules = doc["sections"][0]["rules"]
    assert rules[0]["stages"] == ["{s₁,s₂,s₃}", "ʃ"]
    assert rules[0]["raw"] == "sₓ → ʃ"
    assert rules[1]["stages"] == ["{h₁,h₂,h₃,m̩,n̩}", "a"]
    assert rules[1]["raw"] == "{Hₓ,m̩,n̩} → a"


def test_parse_applies_corrections_overlay_by_rule_id(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Blackfoot",
        section_body=(
            "<h2>7.4 Proto-Algonquian to Blackfoot</h2>\n"
            '<p class="schg" id="Blackfoot-nr">nr → s</p>\n'
        ),
        charset=True,
    )
    doc = default_index_parser(
        corrections={"Blackfoot-nr": "nl → s"},
    ).parse(html_path, source_file="index.html")
    rule = doc["sections"][0]["rules"][0]
    assert rule["rule_id"] == "Blackfoot-nr"
    assert rule["raw"] == "nl → s"
    assert rule["stages"] == ["nl", "s"]


def test_normalize_html_sub_tags_skips_nested_markup():
    html_text = "<p>x<sub>1<sub>2</sub></sub></p>"
    assert normalize_html_sub_tags(html_text) == html_text
    assert normalize_html_sub_tags("<p>x<sub>1</sub></p>") == "<p>x₁</p>"


def test_parse_keeps_correspondence_series_indices_literal(tmp_path: Path):
    html_path = tmp_path / "afro.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    doc = default_index_parser().parse(html_path, source_file="afro.html")
    aari = next(sec for sec in doc["sections"] if sec["index"] == "6.1.2.1")
    rule = aari["rules"][0]
    assert rule["stages"] == ["s₁ s₂ s₃", "ʃ z tʃ"]
    assert "s₁" in rule["raw"]
    assert "abbreviations" not in aari


def test_parse_leaves_positional_slots_literal(tmp_path: Path):
    html_path = tmp_path / "positional.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    doc = default_index_parser().parse(html_path, source_file="positional.html")
    chamic = next(sec for sec in doc["sections"] if sec["index"] == "10.2.1")
    rule = chamic["rules"][0]
    assert rule["stages"] == ["C₁C₂", "C₂"]


_HTML_FIXTURE = """\
<!doctype html>
<html><body>
<section id="Aari">
<h2>6.1.2.1 South Omotic to Aari</h2>
<p><i>Mecislau</i>
<p class="schg">s<sub>1</sub> s<sub>2</sub> s<sub>3</sub> → ʃ z tʃ
</section>
<section id="Chamic">
<h2>10.2.1 Proto-Malayo-Polynesian to Proto-Chamic</h2>
<p class="schg">C<sub>1</sub>C<sub>2</sub> → C<sub>2</sub>
</section>
</body></html>
"""


_SAMPLED_HTML_RULE_CASES = _load_sampled_html_rules()


@pytest.mark.parametrize(
    ("case_id", "raw", "expected"),
    _SAMPLED_HTML_RULE_CASES,
    ids=[case_id for case_id, _, _ in _SAMPLED_HTML_RULE_CASES],
)
def test_extract_rule_parts_sampled_html_rules(case_id, raw, expected):
    assert extract_rule_parts(normalize_symbols(raw)) == expected, case_id


def test_parser_normalizes_symbols_and_preserves_raw(tmp_path: Path):
    html_path = tmp_path / "mapped.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Mapped",
        charset=True,
        section_body="""\
<h2>1.0 Test Section</h2>
<p class="schg">a → b / _$%oː</p>""",
    )
    doc = default_index_parser().parse(html_path, source_file="mapped.html")
    assert "abbreviations" not in doc
    rule = doc["sections"][0]["rules"][0]
    assert rule["stages"] == ["a", "b"]
    assert rule["env"] == "_$$oː"
    assert rule["raw"] == "a → b / _$%oː"


def test_parser_class_letters_unchanged(tmp_path: Path):
    html_path = tmp_path / "unmapped.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Unmapped",
        charset=True,
        section_body="""\
<h2>1.0 Test Section</h2>
<p class="schg">S → a / V_V</p>""",
    )
    doc = default_index_parser().parse(html_path, source_file="unmapped.html")
    assert "abbreviations" not in doc
    rule = doc["sections"][0]["rules"][0]
    assert rule["stages"][0] == "S"
    assert rule["env"] == "V_V"


@pytest.mark.parametrize(
    "input, expected",
    [
        ("C[+voiced]", "C[+voice]"),
        ("N[-voiced]", "N[-voice]"),
        ("C[+ sibilant]", "C[+strident]"),
    ],
)
def test_normalize_feature_matrices_in_field_rename(input, expected):
    mappings = minimal_feature_mappings()
    assert normalize_feature_matrices_in_field(input, mappings) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("u[+short]", "u[-long]"),
        ("V[-short]", "V[+long]"),
    ],
)
def test_normalize_feature_matrices_in_field_rename_invert(input, expected):
    mappings = minimal_feature_mappings()
    assert normalize_feature_matrices_in_field(input, mappings) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("S[- glottalized]", "S[+place]"),
        ("V[-glottalized]", "V[+place]"),
        ("V[+glottalized]", "V[-place]"),
        ("_CV[+close-mid](C)#", "_CV[-hi,-lo,+tense](C)#"),
        ("_CV[+open-mid](C)#", "_CV[-hi,-lo,-tense](C)#"),
        ("V[-open]", "V[-lo]"),
        ("V[-closed]", "V[-hi]"),
    ],
)
def test_normalize_feature_matrices_in_field_rename_polarity(input, expected):
    mappings = minimal_feature_mappings()
    assert normalize_feature_matrices_in_field(input, mappings) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("C:[+dental]", "C:[+cor,+anterior,+dist]"),
        ("_C[+dental]", "_C[+cor,+anterior,+dist]"),
        ("C:[+alveolar]", "C:[+cor,+anterior,-dist]"),
        ("O:[+palatal]", "O:[+cor,+dist]"),
        ("_C[+palatal]", "_C[+cor,+dist]"),
        ("C:[+velar]", "C:[-fr,+bk,+hi,-lo]"),
        ("C[+velar]_C[+velar]", "C[-fr,+bk,+hi,-lo]_C[-fr,+bk,+hi,-lo]"),
        ("Cʷ:[+uvular]", "Cʷ:[-fr,+bk,-hi,-lo]"),
        ("short u", "short u"),
        ("V[+high tone]", "V[tone: 5]"),
        ("V[+low tone]", "V[tone: 1]"),
        ("V[+ falling tone]", "V[tone: 51]"),
        ("V:[+long][+low falling tone]", "V:[+long][tone: 21]"),
        ("aː[+high rising tone]", "aː[tone: 35]"),
        ("V[+ low tone]", "V[tone: 1]"),
        ("V[+ high tone]", "V[tone: 5]"),
        ("V[- tone]", "V[- tone]"),
        ("V:[-falling tone]", "V:[-falling tone]"),
        ("V:[+stress][-long -falling tone]", "V:[+stress][-long -falling tone]"),
    ],
)
def test_normalize_feature_matrices_in_field_place_bundles(input, expected):
    mappings = minimal_feature_mappings()
    assert normalize_feature_matrices_in_field(input, mappings) == expected


def test_kenyah_vowel_height_rules_validate():
    mappings = minimal_feature_mappings()
    rules = [
        {
            "stages": ["i u", "e o"],
            "env": normalize_feature_matrices_in_field("_CV[+close-mid](C)#", mappings),
        },
        {
            "stages": ["i u", "ɛ ɔ"],
            "env": normalize_feature_matrices_in_field("_CV[+open-mid](C)#", mappings),
        },
    ]
    section = {
        "index": "10.2.6.2.1",
        "section": "Proto-Kenyah to Òma Lóngh",
        "rules": rules,
    }
    validate_asca(
        DiachronicSeries(section, "asca", compiler_config=minimal_compiler_config())
    )


def test_apply_feature_mappings():
    mappings = {
        "voiced": FeatureMapping("voiced", "rename", "voice", confidence="high"),
    }
    assert apply_feature_mappings(
        {"stages": ["C[+voiced]", "C[+voice]"]},
        mappings,
    ) == {"stages": ["C[+voice]", "C[+voice]"]}


def test_parser_config_resolved_section_mappings_ancestry_and_override():
    config = ParserConfig(
        ipa_mappings_confidence=frozenset({"high"}),
        section_mappings_sections={
            "10.1": {"*D": "D", "*R": "R"},
            "10.1.2": {"*D": "d"},
        },
    )
    assert config.resolved_section_mappings("10.1.2.1") == {
        "*D": "d",
        "*R": "R",
    }
    assert config.resolved_section_mappings("10.2.1") == {}
    assert config.resolved_section_mappings("") == {}


def test_apply_section_mappings_longest_from_first():
    config = ParserConfig(
        ipa_mappings_confidence=frozenset({"high"}),
        section_mappings_sections={"1.0": {"*D": "D", "*DZ": "dz"}},
    )
    assert apply_section_mappings("*DZ → z", "1.0", config) == "dz → z"


def test_parse_rule_element_applies_section_mapping_keeps_raw():
    el = html.fragment_fromstring(
        '<p class="schg">*D → d / _#</p>',
        create_parent=False,
    )
    parser = default_index_parser()
    rules = parser.parse_rule_element(
        el,
        source_file="index_diachronica_original.html",
        section_index="10.1.2.1",
    )
    assert rules[0]["stages"] == ["D", "d"]
    assert rules[0]["env"] == "_#"
    assert rules[0]["raw"] == "*D → d / _#"


def test_parse_order_correction_then_section_then_manual():
    el = html.fragment_fromstring(
        '<p class="schg" id="Test-rule">*D → d</p>',
        create_parent=False,
    )
    parser = default_index_parser(
        corrections={"Test-rule": "*D → mapped"},
        manual_mappings=[
            ManualMapping(from_text="D → mapped", to_text="D → manual", reason=""),
        ],
    )
    rules = parser.parse_rule_element(
        el,
        source_file="index.html",
        section_index="10.1",
        rule_id="Test-rule",
    )
    assert rules[0]["raw"] == "*D → mapped"
    assert rules[0]["stages"] == ["D", "manual"]


def test_parser_marks_skip_rules_from_config(tmp_path: Path):
    html_path = tmp_path / "skip_rule.html"
    config_path = tmp_path / "parser_config.yml"
    config_path.write_text(
        "ipa_mappings:\n  confidence: [high]\n"
        "skip_rules:\n"
        "  - id: Hold-out-rule\n"
        '    reason: "unrepresentable chain"\n',
        encoding="utf-8",
    )
    for name, content in [
        ("ipa_mappings.yml", "{}\n"),
        ("manual_mappings.yml", "[]\n"),
        ("feature_mappings.yml", "{}\n"),
        ("index_diachronica_corrections.yml", "rules: []\n"),
    ]:
        (tmp_path / name).write_text(content, encoding="utf-8")
    _write_index_diachronica_html(
        html_path,
        section_id="SkipRule",
        section_body="""\
<h2>1.0 Hold-out</h2>
<p class="schg" id="Hold-out-rule">i → j [ə?] → {e,a}</p>""",
    )
    parser = default_index_parser(parser_config=load_parser_config(config_path))
    rule = parser.parse(html_path)["sections"][0]["rules"][0]
    assert rule["status"] == "skipped"
    assert rule["stages"] == []
    assert rule["comment"] == "unrepresentable chain"
    assert rule["raw"] == "i → j [ə?] → {e,a}"


def test_normalize_ipa_in_field():
    mappings = minimal_ipa_mappings()
    assert normalize_ipa_in_field("TŠ", mappings) == "Tʃ"
    assert normalize_ipa_in_field("Š", mappings) == "ʃ"


def test_apply_ipa_mappings():
    mappings = {"Š": "ʃ"}
    assert apply_ipa_mappings(
        {"stages": ["TŠ", "TS"], "env": "_{Š}"},
        mappings,
    ) == {"stages": ["Tʃ", "TS"], "env": "_{ʃ}"}


def test_parse_rule_element_normalizes_ipa_characters():
    el = html.fragment_fromstring(
        '<p class="schg">K → TŠ / in Mentasta Ahtna</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"][-1] == "Tʃ"
    assert rules[0]["raw"] == "K → TŠ / in Mentasta Ahtna"


def test_parse_rule_element_applies_configured_ipa_confidence_levels():
    el = html.fragment_fromstring(
        '<p class="schg">ḱ → s / _i</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"][0] == "kʲ"
    assert "ḱ" in rules[0]["raw"]
    el2 = html.fragment_fromstring(
        '<p class="schg">é → ɛ / _#</p>',
        create_parent=False,
    )
    rules2 = _parse_rule_element(el2, source_file="index_diachronica_original.html")
    assert rules2[0]["stages"][0] == "e"
    assert "é" in rules2[0]["raw"]


def test_index_diachronica_parser_high_only_config_skips_medium_at_parse():
    config = ParserConfig(
        ipa_mappings_confidence=frozenset({"high"}),
        ipa_mappings=(
            IpaMapping("ḱ", "kʲ", confidence="high"),
            IpaMapping("è", "ɛ", confidence="high"),
            IpaMapping("é", "e", confidence="medium"),
        ),
    )
    parser = default_index_parser(parser_config=config)
    el = html.fragment_fromstring(
        '<p class="schg">é → ɛ / _#</p>',
        create_parent=False,
    )
    rules = parser.parse_rule_element(
        el,
        source_file="index_diachronica_original.html",
    )
    assert rules[0]["stages"][0] == "é"


def test_index_diachronica_parser_accepts_custom_parser_config():
    config = ParserConfig(ipa_mappings_confidence=frozenset({"high"}))
    parser = default_index_parser(parser_config=config)
    assert parser._parser_config.ipa_mappings_confidence == frozenset({"high"})


def test_parse_rule_element_normalizes_feature_matrices():
    el = html.fragment_fromstring(
        '<p class="schg">N → N / C[+voiced]</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"][0] == "N"
    assert rules[0]["env"] == "C[+voice]"
    assert "[+voiced]" in rules[0]["raw"]


def test_parse_rule_element_normalizes_short_to_neg_long():
    el = html.fragment_fromstring(
        '<p class="schg">v → ∅ / u[+short]_V[+short]</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "u[-long]_V[-long]"
    assert "[+short]" in rules[0]["raw"]


def test_parse_rule_element_normalizes_glottalized_to_place():
    el = html.fragment_fromstring(
        '<p class="schg">R[- glottalized]VˀR → ˀRVR[- glottalized] / _$</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"] == ["R[+place]VˀR", "ˀRVR[+place]"]
    assert "[- glottalized]" in rules[0]["raw"]


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_voiced_matrix_validates_asca():
    el = html.fragment_fromstring(
        '<p class="schg">s → z / _C[+voiced]</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    section = {"index": "17.12", "section": "Voicing", "rules": rules}
    validate_asca(
        DiachronicSeries(section, compiler_config=minimal_compiler_config()),
        probe_words=Path("tests/fixtures/asca_probe_words.wsca"),
    )


def test_split_field_semicolon_comment():
    assert split_field_semicolon_comment(
        "depending on the environment; again, the article is unclear"
    ) == (
        "depending on the environment",
        "again, the article is unclear",
    )
    assert split_field_semicolon_comment("short only") == ("short only", None)


def test_join_rule_comment():
    assert join_rule_comment(None, "  a  ", "b") == "a; b"
    assert join_rule_comment() is None


def test_parse_rule_element_captures_semicolon_comment():
    el = html.fragment_fromstring(
        '<p class="schg">V → ∅ / short only; blocked by following consonant</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "short only"
    assert "blocked by following consonant" in rules[0]["comment"]
    assert "; blocked" in rules[0]["raw"]


def test_split_line_semicolon_comment():
    assert split_line_semicolon_comment("a → b ; tail") == ("a → b", "tail")
    assert split_line_semicolon_comment("no semicolon") == ("no semicolon", None)


def test_parse_rule_element_archi_style_comment_before_chain_split():
    broken = "ɣ → q (more likely, *ɢ → q instead of → ɣ)"
    fixed = "ɣ → q ; (more likely, *ɢ → q instead of → ɣ)"
    el = html.fragment_fromstring(f'<p class="schg">{broken}</p>', create_parent=False)
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=broken, to_text=fixed, reason="comment"),
        ],
    )
    rules = parser.parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"] == ["ɣ", "q"]
    assert "more likely" in rules[0]["comment"]
    assert "ɢ" in rules[0]["comment"]


def test_parse_rule_element_native_editorial_tail_in_comment():
    el = html.fragment_fromstring(
        '<p class="schg">VOR → VːR; “this is a tad unclear, because in some instances it didn’t seem to apply”</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"] == ["VOR", "VːR"]
    assert ";" not in rules[0]["stages"][-1]
    assert "tad unclear" in rules[0]["comment"]


def test_parse_rule_element_leading_semicolon_keeps_comment():
    prose = "“In contrast, Romanian exhibits"
    mapped = "; “In contrast, Romanian exhibits"
    el = html.fragment_fromstring(f'<p class="schg">{prose}</p>', create_parent=False)
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=prose, to_text=mapped, reason="comment"),
        ],
    )
    rules = parser.parse_rule_element(el, source_file="index_diachronica_original.html")
    assert "status" not in rules[0]
    assert rules[0]["stages"] == []
    assert "Romanian exhibits" in rules[0]["comment"]
    assert rules[0]["raw"] == prose


def test_parse_rule_element_sporadic_before_semicolon_cut():
    el = html.fragment_fromstring(
        '<p class="schg">k → ∅ / _# / sporadic ; in Mentasta Ahtna</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["sporadic"] is True
    assert "Mentasta Ahtna" in rules[0]["comment"]
    assert rules[0]["env"] == "_#"


def test_parse_rule_element_sporadic_after_semicolon_not_detected():
    el = html.fragment_fromstring(
        '<p class="schg">i → yː ; (sometimes)</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert "sporadic" not in rules[0]
    assert "(sometimes)" in rules[0]["comment"]


def test_parse_rule_element_comment_tail_not_symbol_normalized():
    el = html.fragment_fromstring(
        '<p class="schg">a → b ; prose with % boundary and $ stem</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["comment"] == "prose with % boundary and $ stem"
    assert "%" in rules[0]["comment"]


def test_parse_rule_element_captures_short_only_paren_in_env():
    el = html.fragment_fromstring(
        '<p class="schg">i → e / _CVC#, when stressed (short only)</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_CVC#"
    assert "short only" in rules[0]["comment"]
    assert "when stressed" in rules[0]["comment"]


def test_apply_ipa_mappings_noop_when_mappings_empty():
    parts = {"stages": ["Š", "TS"]}
    assert apply_ipa_mappings(parts, {}) == parts


def test_normalize_ipa_in_field_noop_without_mappings():
    assert normalize_ipa_in_field("Š", {}) == "Š"
    assert normalize_ipa_in_field("", {"Š": "ʃ"}) == ""


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("oı̃ > wɛ̃", "oj\u0303 > wɛ\u0303"),
        ("VnV > ṽlṽ", "VnV > v\u0303lv\u0303"),
        ("iC uC > i û / _{C,#}", "iC uC > i u / _{C,#}"),
        ("Ṽ > V", "v\u0303 > V"),
    ],
)
def test_normalize_ipa_in_field_near_miss_unknown_characters(text, expected):
    mappings = minimal_ipa_mappings()
    assert normalize_ipa_in_field(text, mappings) == expected


@pytest.mark.parametrize(
    ("html_line", "stage_index", "expected_stage"),
    [
        ("{aı̃,eı̃} → ɛ̃", 0, "{aj\u0303,ej\u0303}"),
        ("VnV → ṽlṽ", -1, "v\u0303lv\u0303"),
        ("iC uC → î û / _{C,#}", -1, "i u"),
    ],
)
def test_parse_rule_element_normalizes_near_miss_unknown_characters(
    html_line,
    stage_index,
    expected_stage,
):
    el = html.fragment_fromstring(
        f'<p class="schg">{html_line}</p>',
        create_parent=False,
    )
    rules = _parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["stages"][stage_index] == expected_stage
    assert html_line.split(" → ")[0] in rules[0]["raw"] or "→" in rules[0]["raw"]


def test_index_diachronica_parser_accepts_custom_corrections():
    parser = default_index_parser(corrections={"Test-id": "a → b"})
    assert parser._corrections == {"Test-id": "a → b"}


def test_apply_manual_mappings_miss_leaves_text_unchanged():
    mappings = [ManualMapping(from_text="zzz", to_text="Q", reason="")]
    working, hits = apply_manual_mappings("a → b / _C", mappings)
    assert working == "a → b / _C"
    assert hits == []


def test_parse_rule_element_applies_manual_mapping_keeps_raw():
    broken = "m̩ n̩ → am an / _{s,({m,j,w)V}"
    fixed = "m̩ n̩ → am an / _{s,({m,j,w})V}"
    el = html.fragment_fromstring(
        f'<p class="schg">{broken}</p>',
        create_parent=False,
    )
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=broken, to_text=fixed, reason="bracket"),
        ],
    )
    rules = parser.parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["raw"] == broken
    assert rules[0]["stages"] == ["m̩ n̩", "am an"]
    assert rules[0]["env"] == "_{s,({m,j,w})V}"
    assert "status" not in rules[0]


def test_parse_rule_element_manual_mapping_rescues_quoted_prose():
    prose = (
        "\u201cThe PIE rules for the voicing of s → z, as in [nizdos] "
        "for *nisdos, are assumed to apply\u201d"
    )
    mapped = "s → z / _C[+voice]"
    el = html.fragment_fromstring(
        f'<p class="schg">{prose}</p>',
        create_parent=False,
    )
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=prose, to_text=mapped, reason="nisdos"),
        ],
    )
    rules = parser.parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["raw"] == prose
    assert rules[0]["stages"] == ["s", "z"]
    assert rules[0]["env"] == "_C[+voice]"
    assert rules[0].get("status") != "skipped"


def test_parse_rule_element_without_manual_row_unchanged():
    el = html.fragment_fromstring(
        '<p class="schg">a → e / _C</p>',
        create_parent=False,
    )
    with_mappings = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text="zzz", to_text="Q", reason=""),
        ],
    ).parse_rule_element(el, source_file="index_diachronica_original.html")
    without = default_index_parser(
        manual_mappings=[],
    ).parse_rule_element(el, source_file="index_diachronica_original.html")
    assert with_mappings == without


def test_write_manual_mappings_matched_csv(tmp_path: Path):
    from conlanger.utils.mappings import ManualMappingMatch

    path = tmp_path / "manual_mappings_matched_rules.csv"
    write_manual_mappings_matched_csv(
        [
            ManualMappingMatch(
                section_index="17.5.1",
                section_name="Proto-Indo-European to Old Irish",
                rule_id="Old-Irish-mn",
                source="index_diachronica_original.html:5509",
                manual_mapping="m̩ n̩ → am an / _{s,({m,j,w})V}",
            )
        ],
        path,
    )
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    assert list(df.columns) == [
        "section_index",
        "section_name",
        "rule_id",
        "source",
        "manual_mapping",
    ]
    assert df.iloc[0]["rule_id"] == "Old-Irish-mn"
    assert "_{s,({m,j,w})V}" in df.iloc[0]["manual_mapping"]


def test_parse_records_manual_mapping_matches_and_unmatched(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Old-Irish",
        section_body=(
            "<h2>17.5.1 Proto-Indo-European to Old Irish</h2>\n"
            '<p class="schg">m̩ n̩ → am an / _{s,({m,j,w)V}</p>\n'
            '<p class="schg">a → e / _C</p>\n'
        ),
        charset=True,
    )
    broken = "m̩ n̩ → am an / _{s,({m,j,w)V}"
    fixed = "m̩ n̩ → am an / _{s,({m,j,w})V}"
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=broken, to_text=fixed, reason="bracket"),
            ManualMapping(from_text="never-hits", to_text="x", reason="unused"),
        ],
    )
    doc = parser.parse(html_path, source_file="index.html")
    assert doc["sections"][0]["rules"][0]["env"] == "_{s,mV,jV,wV}"
    assert len(parser.manual_mapping_matches) == 1
    match = parser.manual_mapping_matches[0]
    assert match.section_index == "17.5.1"
    assert match.section_name == "Proto-Indo-European to Old Irish"
    assert match.rule_id == ""
    assert match.manual_mapping == fixed
    unmatched = parser.unmatched_manual_mappings()
    assert [row.from_text for row in unmatched] == ["never-hits"]


def test_unmatched_corrections_reports_unused_rule_ids(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Test",
        section_body='<h2>1.0 Test</h2>\n<p class="schg">a → b</p>',
        charset=True,
    )
    parser = default_index_parser(
        corrections={"unused-id": "x → y", "also-unused": "p → q"},
    )
    parser.parse(html_path, source_file="index.html")
    assert parser.unmatched_corrections() == ["unused-id", "also-unused"]


def test_parse_rule_element_sets_rule_id_on_missing_arrow():
    el = _html_fragment('<p class="schg" id="Test-bad">not a rule</p>')
    rules = default_index_parser().parse_rule_element(
        el,
        source_file="index.html",
        rule_id="Test-bad",
    )
    assert rules[0]["rule_id"] == "Test-bad"
    assert "status" not in rules[0]


def test_parse_rule_element_sets_rule_id_on_quoted_prose():
    el = _html_fragment('<p class="schg" id="Test-prose">"quoted prose only"</p>')
    rules = default_index_parser().parse_rule_element(
        el,
        source_file="index.html",
        rule_id="Test-prose",
    )
    assert rules[0]["rule_id"] == "Test-prose"
    assert "status" not in rules[0]


def test_parse_rule_element_indo_aryan_chain_retains_optional_segments():
    """Regression: trailing ``(a)`` on second spine token is phonology, not gloss."""
    el = _html_fragment(
        '<p class="schg" id="Central-Middle-Indo-Aryan-ai,ja-au,wa">'
        "a{i,j}(a) a{u,w}(a) → e o</p>"
    )
    rules = default_index_parser().parse_rule_element(
        el,
        source_file="index_diachronica_original.html",
        rule_id="Central-Middle-Indo-Aryan-ai,ja-au,wa",
    )
    assert len(rules) == 1
    assert rules[0]["stages"] == ["a{i,j}(a) a{u,w}(a)", "e o"]
    assert rules[0]["raw"] == "a{i,j}(a) a{u,w}(a) → e o"
    assert "comment" not in rules[0]
