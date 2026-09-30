import shutil
from pathlib import Path

import pandas as pd
import pytest
from helpers import default_index_parser, write_tmp_index_html
from lxml import html

from conlanger.appliers.asca import validate_asca
from conlanger.scripts.config_loaders import load_parser_config
from conlanger.tools.rules import DiachronicSeries
from conlanger.utils.mappings import (
    IpaMapping,
    ManualMapping,
    ParserConfig,
    normalize_feature_matrices_in_field,
)
from conlanger.utils.parsing import (
    build_stages_from_spine,
    extract_element_text,
    extract_missing_arrow_rule_parts,
    extract_rule_parts,
    finalize_stages_shape,
    normalize_html_sub_tags,
    parse_section_heading,
    split_env_exception,
    split_input_output,
    split_output_rest,
    split_post_arrow,
    strip_leading_index_list_marker,
)
from conlanger.utils.symbols import normalize_symbols
from tests.fixtures.minimal_mappings import (
    minimal_feature_mappings,
)


def _parse_rule_element(el):
    """Parse one rule element with package-default injected tables."""
    parser = default_index_parser()
    return parser.parse_rule_element(el)


_SAMPLED_RULES_CSV = (
    Path(__file__).resolve().parents[3] / "fixtures" / "sound_change_rules.csv"
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


def test_extract_element_text_tail_after_sub():
    el = html.fragment_fromstring(
        normalize_html_sub_tags("<p>before<sub>2</sub>after</p>")
    )
    assert extract_element_text(el) == "before₂after"


def test_extract_element_text_no_tail_after_sub():
    el = html.fragment_fromstring(normalize_html_sub_tags("<p>before<sub>2</sub></p>"))
    assert extract_element_text(el) == "before₂"


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
    el = html.fragment_fromstring('<p class="schg">dʒ → tʃ → ʃ</p>')
    rules = _parse_rule_element(el)
    assert len(rules) == 1
    assert rules[0] == {
        "stages": ["dʒ", "tʃ", "ʃ"],
        "raw": "dʒ → tʃ → ʃ",
        "source": rules[0]["source"],
    }


def test_parse_rule_element_keeps_chain_with_env():
    el = html.fragment_fromstring('<p class="schg">{θ,l} → r → l / V_V</p>')
    rules = _parse_rule_element(el)
    assert len(rules) == 1
    assert rules[0]["stages"] == ["{θ,l}", "r", "l"]
    assert rules[0]["env"] == "V_V"


def test_parse_rule_element_marks_sporadic_and_strips_gloss():
    el = html.fragment_fromstring('<p class="schg">p → h (sporadic)</p>')
    rules = _parse_rule_element(el)
    assert len(rules) == 1
    assert rules[0]["stages"] == ["p", "h"]
    assert rules[0]["sporadic"] is True
    assert "(sporadic)" in rules[0]["comment"]
    assert rules[0]["raw"] == "p → h (sporadic)"


def test_parse_rule_element_strips_sporadic_env_gloss():
    el = html.fragment_fromstring('<p class="schg">qu → w / _{f,s} (sporadic)</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "_{f,s}"
    assert rules[0]["sporadic"] is True


def test_parse_rule_element_marks_occasionally_sporadic_and_strips_gloss():
    el = html.fragment_fromstring('<p class="schg">l → ∅ (occasionally?)</p>')
    rules = _parse_rule_element(el)
    assert len(rules) == 1
    assert rules[0]["stages"] == ["l", "∅"]
    assert rules[0]["sporadic"] is True
    assert "(occasionally?)" in rules[0]["comment"]
    assert rules[0]["raw"] == "l → ∅ (occasionally?)"


def test_parse_rule_element_splits_env_glued_after_spaced_slash():
    el = html.fragment_fromstring('<p class="schg">ð → ∅ /{a,E}_</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["stages"] == ["ð", "∅"]
    assert rules[0]["env"] == "{a,E}_"


def test_parse_rule_element_strips_trailing_question_mark_from_env():
    el = html.fragment_fromstring('<p class="schg">l → ∅ / _# ?</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["stages"] == ["l", "∅"]
    assert rules[0]["env"] == "_#"
    assert rules[0]["sporadic"] is True
    assert "?" in rules[0]["comment"]


def test_parse_rule_element_strips_trailing_question_mark_from_albanian_env():
    el = html.fragment_fromstring('<p class="schg">kʷ → c / _B?</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "_B"
    assert rules[0]["sporadic"] is True
    assert "?" in rules[0]["comment"]


def test_parse_rule_element_keeps_gloss_only_output():
    el = html.fragment_fromstring(
        '<p class="schg">hhy \u2192 \u201csomething like /\u0292/\u201d</p>'
    )
    rules = _parse_rule_element(el)
    assert len(rules) == 1
    assert "status" not in rules[0]
    assert rules[0]["stages"] == ["hhy"]
    assert "something like" in rules[0]["comment"]
    assert rules[0]["raw"] == "hhy \u2192 \u201csomething like /\u0292/\u201d"


def test_parse_rule_element_strips_trailing_glosses():
    el = html.fragment_fromstring(
        '<p class="schg">w → f (Common Celtic, I’m not sure of the conditions)</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["stages"] == ["w", "f"]
    assert "Celtic" in rules[0]["comment"]
    assert "Celtic" in rules[0]["raw"]


def test_parse_rule_element_keeps_set_and_matrix_parentheticals():
    el = html.fragment_fromstring(
        '<p class="schg">({C,#}V[-long])ʔ → ({C,#}Vː[+falling tone])∅ / _C</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["stages"] == [
        "({C,#}V[-long])ʔ",
        "({C,#}Vː[tone: 51])∅",
    ]
    assert rules[0]["env"] == "_C"
    assert "comment" not in rules[0]


def test_parse_rule_element_keeps_nested_feature_matrix_optionals():
    el = html.fragment_fromstring(
        '<p class="schg">V[+high +ATR](C(V[+high -ATR])) → '
        "#(C)V[-high +ATR](CV[+high +ATR]) / #J[+dorsal -voiced]_</p>"
    )
    rules = _parse_rule_element(el)
    assert rules[0]["stages"] == [
        "V[+high +atr](C(V[+high -atr]))",
        "#(C)V[-high +atr](CV[+high +atr])",
    ]


def test_parse_rule_element_strips_unclosed_paren_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">d ɡ → t k (may have been part of a more sweeping merger</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["stages"] == ["d ɡ", "t k"]
    assert "sweeping merger" in rules[0]["comment"]
    assert "sweeping merger" in rules[0]["raw"]


def test_parse_rule_element_strips_env_trailing_glosses():
    el = html.fragment_fromstring(
        '<p class="schg">t → k / _s̩ (Ōgami) (http://example.com)</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "_s̩"
    assert "Ōgami" in rules[0]["raw"]


def test_parse_rule_element_strips_embedded_quoted_env_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">z → d / “when another sibilant is in the word nearby” and (word-finally?) when</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "and (word-finally?) when"
    assert "sibilant" in rules[0]["raw"]


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_medial_validate_asca(fx_sample_compiler_config):
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    el = html.fragment_fromstring('<p class="schg">t → r / medially</p>')
    rules = _parse_rule_element(el)
    section = {"index": "6.2.1.1.2", "section": "Proto-Agaw to Blin", "rules": rules}
    validate_asca(
        DiachronicSeries(section, compiler_config=fx_sample_compiler_config),
        probe_words=probe,
    )


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_medial_with_exception_env_normalized():
    el = html.fragment_fromstring(
        '<p class="schg">b → h / medially, ! {r(ʲ),l(ʲ)}_ or _ɡ</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "_"
    assert rules[0]["exception"] == "{r(ʲ),l(ʲ)}_ or _ɡ"
    assert "medially" in rules[0]["comment"]


def test_parse_rule_element_normalizes_stress_conditions():
    el = html.fragment_fromstring('<p class="schg">a → i / _C(C), when stressed</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "_C(C) when stressed"
    assert ", when stressed" in rules[0]["raw"]


def test_parse_element_handles_dialectal_rules(tmp_path: Path):
    html_path = tmp_path / "dialectal.html"
    write_tmp_index_html(
        html_path,
        section_id="Dialectal",
        section_body="""\
<h2>1.0 Proto-IndoEuropean to Klingon</h2>
<p class="schg">a → i / in northern dialects</p>
<p class="schg">a → i / dialectal</p>""",
    )
    doc = default_index_parser().parse(html_path)
    rule1 = doc["sections"][0]["rules"][0]
    rule2 = doc["sections"][0]["rules"][1]

    assert rule1["env"] == {"dialect": "northern"}
    assert rule2["env"] == {"dialect": True}


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_stress_conditions_validate_asca(fx_sample_compiler_config):
    cases = [
        '<p class="schg">a → i / _C(C), when stressed</p>',
        '<p class="schg">{u,a,i} → ∅ / _%, when stressed (short only)</p>',
        '<p class="schg">e oj ɛa → i u ɛ / when unstressed</p>',
        '<p class="schg">e → i / l_ when unstressed</p>',
    ]
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    for html_snippet in cases:
        el = html.fragment_fromstring(html_snippet)
        rules = _parse_rule_element(el)
        section = {
            "index": "47.1",
            "section": "Stress conditions",
            "rules": rules,
        }
        validate_asca(
            DiachronicSeries(section, compiler_config=fx_sample_compiler_config),
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
    write_tmp_index_html(
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
    write_tmp_index_html(
        html_path,
        section_id="NoH2",
        section_body='<p class="schg">a → b</p>',
    )
    assert default_index_parser().parse(html_path)["sections"] == []


def test_parser_skips_section_with_empty_name(tmp_path: Path):
    html_path = tmp_path / "empty_name.html"
    write_tmp_index_html(
        html_path,
        section_id="Empty",
        section_body="""\
<h2>   </h2>
<p class="schg">a → b</p>""",
    )
    assert default_index_parser().parse(html_path)["sections"] == []


def test_parser_skips_empty_paragraph(tmp_path: Path):
    html_path = tmp_path / "empty_p.html"
    write_tmp_index_html(
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
    write_tmp_index_html(
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
    write_tmp_index_html(
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
    write_tmp_index_html(
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
    el = html.fragment_fromstring(
        normalize_html_sub_tags('<p class="schg">ʃ → s<sub>2</sub> / {i,j}_</p>')
    )
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["ʃ", "s₂"]
    assert rule["env"] == "{i,j}_"
    assert rule["raw"] == "ʃ → s₂ / {i,j}_"
    assert rule["source"].startswith("index:")
    assert "status" not in rule


def test_parse_rule_element_with_exception():
    el = html.fragment_fromstring('<p class="schg">w → ∅ / #C_V, except _i(ː)</p>')
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["w", "∅"]
    assert rule["env"] == "#C_V"
    assert rule["exception"] == "_i(ː)"


def test_parse_rule_element_no_env():
    el = html.fragment_fromstring('<p class="schg">ɬ → l</p>')
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["ɬ", "l"]
    assert "env" not in rule
    assert "exception" not in rule


def test_parse_rule_element_missing_arrow():
    el = html.fragment_fromstring('<p class="schg">a to b no arrow</p>')
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["a to b no arrow"]
    assert "status" not in rule


def test_parse_rule_element_missing_arrow_with_env_exception_comment():
    el = html.fragment_fromstring(
        '<p class="schg">a to b no arrow / _# ! V_ ; editorial note</p>'
    )
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["a to b no arrow"]
    assert rule["env"] == "_#"
    assert rule["exception"] == "V_"
    assert rule["comment"] == "editorial note"
    assert "status" not in rule


def test_parse_rule_element_arrow_without_spaces():
    el = html.fragment_fromstring('<p class="schg">a \u2192\u0259 / _#</p>')
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["a", "ə"]
    assert rule["env"] == "_#"
    assert "status" not in rule


def test_parse_rule_element_bang_exception():
    el = html.fragment_fromstring('<p class="schg">s \u2192 \u0283 / !V_</p>')
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["s", "ʃ"]
    assert "env" not in rule
    assert rule["exception"] == "V_"


def test_parse_rule_element_env_and_bang_exception():
    el = html.fragment_fromstring(
        '<p class="schg">w \u2192 \u2205 / _# ! k(\u02d0)_</p>'
    )
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["w", "∅"]
    assert rule["env"] == "_#"
    assert rule["exception"] == "k(ː)_"


def test_parse_rule_element_except_without_comma():
    el = html.fragment_fromstring(
        '<p class="schg">q \u2192 \u0294 / except in several words</p>'
    )
    rule = _parse_rule_element(el)[0]
    assert rule["stages"] == ["q", "ʔ"]
    assert "env" not in rule
    assert rule["exception"] == "in several words"


def test_first_p_is_citation_rest_comments(tmp_path: Path):
    html_path = tmp_path / "sample.html"
    write_tmp_index_html(
        html_path,
        section_id="Bench",
        section_body="""\
<h2>6.1.1.1 North Omotic to Bench</h2>
<p><i>Mecislau</i>, from Ehret (1995), Title</p>
<p>NB: Does not include vowel developments.</p>
<p class="schg">x<sub>1</sub> \u2192 k</p>
<p>Interleaved note</p>
<p class="schg">\u026c \u2192 l</p>""",
    )
    doc = default_index_parser().parse(html_path)
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
    doc = default_index_parser().parse(html_path)
    rules = doc["sections"][0]["rules"]
    assert rules[0]["stages"] == ["{s₁,s₂,s₃}", "ʃ"]
    assert rules[0]["raw"] == "sₓ → ʃ"
    assert rules[1]["stages"] == ["{h₁,h₂,h₃,m̩,n̩}", "a"]
    assert rules[1]["raw"] == "{Hₓ,m̩,n̩} → a"


def test_parse_applies_corrections_overlay_by_rule_id(tmp_path: Path):
    html_path = tmp_path / "index.html"
    write_tmp_index_html(
        html_path,
        section_id="Blackfoot",
        section_body=(
            "<h2>7.4 Proto-Algonquian to Blackfoot</h2>\n"
            '<p class="schg" id="Blackfoot-nr">nr → s</p>\n'
        ),
    )
    doc = default_index_parser(
        corrections={"Blackfoot-nr": "nl → s"},
    ).parse(html_path)
    rule = doc["sections"][0]["rules"][0]
    assert rule["rule_id"] == "Blackfoot-nr"
    assert rule["raw"] == "nr → s"
    assert rule["stages"] == ["nl", "s"]


def test_normalize_html_sub_tags_skips_nested_markup():
    html_text = "<p>x<sub>1<sub>2</sub></sub></p>"
    assert normalize_html_sub_tags(html_text) == html_text
    assert normalize_html_sub_tags("<p>x<sub>1</sub></p>") == "<p>x₁</p>"


def test_parse_keeps_correspondence_series_indices_literal(tmp_path: Path):
    html_path = tmp_path / "afro.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    doc = default_index_parser().parse(html_path)
    aari = next(sec for sec in doc["sections"] if sec["index"] == "6.1.2.1")
    rule = aari["rules"][0]
    assert rule["stages"] == ["s₁ s₂ s₃", "ʃ z tʃ"]
    assert "s₁" in rule["raw"]
    assert "abbreviations" not in aari


def test_parse_leaves_positional_slots_literal(tmp_path: Path):
    html_path = tmp_path / "positional.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    doc = default_index_parser().parse(html_path)
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
    write_tmp_index_html(
        html_path,
        section_id="Mapped",
        section_body="""\
<h2>1.0 Test Section</h2>
<p class="schg">a → b / _$%oː</p>""",
    )
    doc = default_index_parser().parse(html_path)
    assert "abbreviations" not in doc
    rule = doc["sections"][0]["rules"][0]
    assert rule["stages"] == ["a", "b"]
    assert rule["env"] == "_$$oː"
    assert rule["raw"] == "a → b / _$%oː"


def test_parser_class_letters_unchanged(tmp_path: Path):
    html_path = tmp_path / "unmapped.html"
    write_tmp_index_html(
        html_path,
        section_id="Unmapped",
        section_body="""\
<h2>1.0 Test Section</h2>
<p class="schg">S → a / V_V</p>""",
    )
    doc = default_index_parser().parse(html_path)
    assert "abbreviations" not in doc
    rule = doc["sections"][0]["rules"][0]
    assert rule["stages"][0] == "S"
    assert rule["env"] == "V_V"


def test_kenyah_vowel_height_rules_validate(fx_sample_compiler_config):
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
        DiachronicSeries(section, "asca", compiler_config=fx_sample_compiler_config)
    )


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


def test_parse_rule_element_applies_section_mapping_keeps_raw():
    el = html.fragment_fromstring('<p class="schg">*D → d / _#</p>')
    parser = default_index_parser()
    rules = parser.parse_rule_element(
        el,
        section_index="10.1.2.1",
    )
    assert rules[0]["stages"] == ["D", "d"]
    assert rules[0]["env"] == "_#"
    assert rules[0]["raw"] == "*D → d / _#"


def test_parse_order_correction_then_section_then_manual():
    el = html.fragment_fromstring('<p class="schg" id="Test-rule">*D → d</p>')
    parser = default_index_parser(
        corrections={"Test-rule": "*D → mapped"},
        manual_mappings=[
            ManualMapping(from_text="D → mapped", to_text="D → manual", reason=""),
        ],
    )
    rules = parser.parse_rule_element(
        el,
        section_index="10.1",
        rule_id="Test-rule",
    )
    assert rules[0]["raw"] == "*D → d"
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
    write_tmp_index_html(
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


def test_parse_rule_element_normalizes_ipa_characters():
    el = html.fragment_fromstring('<p class="schg">K → TŠ / in Mentasta Ahtna</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["stages"][-1] == "Tʃ"
    assert rules[0]["raw"] == "K → TŠ / in Mentasta Ahtna"


def test_parse_rule_element_applies_configured_ipa_confidence_levels():
    el = html.fragment_fromstring('<p class="schg">ḱ → s / _i</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["stages"][0] == "kʲ"
    assert "ḱ" in rules[0]["raw"]
    el2 = html.fragment_fromstring('<p class="schg">é → ɛ / _#</p>')
    rules2 = _parse_rule_element(el2)
    assert rules2[0]["stages"][0] == "e"
    assert "é" in rules2[0]["raw"]


def test_index_diachronica_parser_high_only_config_skips_medium_at_parse():
    config = ParserConfig(
        ipa_mappings_confidence=frozenset({"high"}),
        ipa_mappings=(
            IpaMapping(index_feature="ḱ", ipa_target="kʲ", confidence="high"),
            IpaMapping(index_feature="è", ipa_target="ɛ", confidence="high"),
            IpaMapping(index_feature="é", ipa_target="e", confidence="medium"),
        ),
    )
    parser = default_index_parser(parser_config=config)
    el = html.fragment_fromstring('<p class="schg">é → ɛ / _#</p>')
    rules = parser.parse_rule_element(el)
    assert rules[0]["stages"][0] == "é"


def test_index_diachronica_parser_accepts_custom_parser_config():
    config = ParserConfig(ipa_mappings_confidence=frozenset({"high"}))
    parser = default_index_parser(parser_config=config)
    assert parser._parser_config.ipa_mappings_confidence == frozenset({"high"})


def test_parse_rule_element_normalizes_feature_matrices():
    el = html.fragment_fromstring('<p class="schg">N → N / C[+voiced]</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["stages"][0] == "N"
    assert rules[0]["env"] == "C[+voice]"
    assert "[+voiced]" in rules[0]["raw"]


def test_parse_rule_element_normalizes_short_to_neg_long():
    el = html.fragment_fromstring('<p class="schg">v → ∅ / u[+short]_V[+short]</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "u[-long]_V[-long]"
    assert "[+short]" in rules[0]["raw"]


def test_parse_rule_element_normalizes_glottalized_to_place():
    el = html.fragment_fromstring(
        '<p class="schg">R[- glottalized]VˀR → ˀRVR[- glottalized] / _$</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["stages"] == ["R[+place]VˀR", "ˀRVR[+place]"]
    assert "[- glottalized]" in rules[0]["raw"]


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_voiced_matrix_validates_asca(fx_sample_compiler_config):
    el = html.fragment_fromstring('<p class="schg">s → z / _C[+voiced]</p>')
    rules = _parse_rule_element(el)
    section = {"index": "17.12", "section": "Voicing", "rules": rules}
    validate_asca(
        DiachronicSeries(section, compiler_config=fx_sample_compiler_config),
        probe_words=Path("tests/fixtures/asca_probe_words.wsca"),
    )


def test_parse_rule_element_captures_semicolon_comment():
    el = html.fragment_fromstring(
        '<p class="schg">V → ∅ / short only; blocked by following consonant</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "_"
    assert "short only" in rules[0]["comment"]
    assert "blocked by following consonant" in rules[0]["comment"]
    assert "; blocked" in rules[0]["raw"]


@pytest.mark.parametrize(
    ("rule_text", "expected_env", "expected_exception"),
    [
        (
            "V → ∅ / V_C in northern dialects",
            {"dialect": "northern", "context": "V_C"},
            None,
        ),
        (
            "V → ∅ / V_C in northern dialects ! in southern dialects",
            {"dialect": "northern", "context": "V_C"},
            {"dialect": "southern"},
        ),
        (
            "V → ∅ / in northern and southern dialects",
            {
                "dialect": ["northern", "southern"],
            },
            None,
        ),
        (
            "V → ∅ / dialectal",
            {"dialect": True},
            None,
        ),
        (
            "V → ∅ / dialectal ; in northern dialects",
            {"dialect": True},
            None,
        ),
        (
            "V → ∅ / #_V",
            "#_V",
            None,
        ),
    ],
)
def test_parse_rule_element_apply_dialects_to_context(
    rule_text, expected_env, expected_exception
):
    el = html.fragment_fromstring(f'<p class="schg">{rule_text}</p>')
    rules = _parse_rule_element(el)
    if expected_env is not None:
        assert rules[0]["env"] == expected_env
    if expected_exception is not None:
        assert rules[0]["exception"] == expected_exception


def test_parse_rule_element_archi_style_comment_before_chain_split():
    broken = "ɣ → q (more likely, *ɢ → q instead of → ɣ)"
    fixed = "ɣ → q ; (more likely, *ɢ → q instead of → ɣ)"
    el = html.fragment_fromstring(f'<p class="schg">{broken}</p>')
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=broken, to_text=fixed, reason="comment"),
        ],
    )
    rules = parser.parse_rule_element(el)
    assert rules[0]["stages"] == ["ɣ", "q"]
    assert "more likely" in rules[0]["comment"]
    assert "ɢ" in rules[0]["comment"]


def test_parse_rule_element_native_editorial_tail_in_comment():
    el = html.fragment_fromstring(
        '<p class="schg">VOR → VːR; “this is a tad unclear, because in some instances it didn’t seem to apply”</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["stages"] == ["VOR", "VːR"]
    assert ";" not in rules[0]["stages"][-1]
    assert "tad unclear" in rules[0]["comment"]


def test_parse_rule_element_leading_semicolon_keeps_comment():
    prose = "“In contrast, Romanian exhibits"
    mapped = "; “In contrast, Romanian exhibits"
    el = html.fragment_fromstring(f'<p class="schg">{prose}</p>')
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=prose, to_text=mapped, reason="comment"),
        ],
    )
    rules = parser.parse_rule_element(el)
    assert "status" not in rules[0]
    assert rules[0]["stages"] == []
    assert "Romanian exhibits" in rules[0]["comment"]
    assert rules[0]["raw"] == prose


def test_parse_rule_element_sporadic_before_semicolon_cut():
    el = html.fragment_fromstring(
        '<p class="schg">k → ∅ / _# / sporadic ; in Mentasta Ahtna</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["sporadic"] is True
    assert "Mentasta Ahtna" in rules[0]["comment"]
    assert rules[0]["env"] == "_#"


@pytest.mark.parametrize(
    "sporadic_qualifier", ["sporadic", "(sometimes)", "sometimes?", "occasionally?"]
)
def test_parse_rule_element_sporadic_after_semicolon_detected(sporadic_qualifier):
    el = html.fragment_fromstring(f'<p class="schg">i → yː ; {sporadic_qualifier}</p>')
    rules = _parse_rule_element(el)
    assert "sporadic" in rules[0]
    assert sporadic_qualifier in rules[0]["comment"]


def test_parse_rule_element_comment_tail_not_symbol_normalized():
    el = html.fragment_fromstring(
        '<p class="schg">a → b ; prose with % boundary and $ stem</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["comment"] == "prose with % boundary and $ stem"
    assert "%" in rules[0]["comment"]


def test_parse_rule_element_captures_short_only_paren_in_env():
    el = html.fragment_fromstring(
        '<p class="schg">i → e / _CVC#, when stressed (short only)</p>'
    )
    rules = _parse_rule_element(el)
    assert rules[0]["env"] == "_CVC#"
    assert "short only" in rules[0]["comment"]
    assert "when stressed" in rules[0]["comment"]


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
    el = html.fragment_fromstring(f'<p class="schg">{html_line}</p>')
    rules = _parse_rule_element(el)
    assert rules[0]["stages"][stage_index] == expected_stage
    assert html_line.split(" → ")[0] in rules[0]["raw"] or "→" in rules[0]["raw"]


def test_index_diachronica_parser_accepts_custom_corrections():
    parser = default_index_parser(corrections={"Test-id": "a → b"})
    assert parser._corrections == {"Test-id": "a → b"}


def test_parse_rule_element_applies_manual_mapping_keeps_raw():
    broken = "m̩ n̩ → am an / _{s,({m,j,w)V}"
    fixed = "m̩ n̩ → am an / _{s,({m,j,w})V}"
    el = html.fragment_fromstring(f'<p class="schg">{broken}</p>')
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=broken, to_text=fixed, reason="bracket"),
        ],
    )
    rules = parser.parse_rule_element(el)
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
    el = html.fragment_fromstring(f'<p class="schg">{prose}</p>')
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=prose, to_text=mapped, reason="nisdos"),
        ],
    )
    rules = parser.parse_rule_element(el)
    assert rules[0]["raw"] == prose
    assert rules[0]["stages"] == ["s", "z"]
    assert rules[0]["env"] == "_C[+voice]"
    assert rules[0].get("status") != "skipped"


def test_parse_rule_element_without_manual_row_unchanged():
    el = html.fragment_fromstring('<p class="schg">a → e / _C</p>')
    with_mappings = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text="zzz", to_text="Q", reason=""),
        ],
    ).parse_rule_element(el)
    without = default_index_parser(
        manual_mappings=[],
    ).parse_rule_element(el)
    assert with_mappings == without


def test_parse_records_manual_mapping_matches_and_unmatched(tmp_path: Path):
    html_path = tmp_path / "index.html"
    write_tmp_index_html(
        html_path,
        section_id="Old-Irish",
        section_body=(
            "<h2>17.5.1 Proto-Indo-European to Old Irish</h2>\n"
            '<p class="schg">m̩ n̩ → am an / _{s,({m,j,w)V}</p>\n'
            '<p class="schg">a → e / _C</p>\n'
        ),
    )
    broken = "m̩ n̩ → am an / _{s,({m,j,w)V}"
    fixed = "m̩ n̩ → am an / _{s,({m,j,w})V}"
    parser = default_index_parser(
        manual_mappings=[
            ManualMapping(from_text=broken, to_text=fixed, reason="bracket"),
            ManualMapping(from_text="never-hits", to_text="x", reason="unused"),
        ],
    )
    doc = parser.parse(html_path)
    assert doc["sections"][0]["rules"][0]["env"] == "_{s,mV,jV,wV}"
    assert len(parser.manual_mapping_matches) == 1
    match = parser.manual_mapping_matches[0]
    assert match.section_index == "17.5.1"
    assert match.section_name == "Proto-Indo-European to Old Irish"
    assert match.rule_id == ""
    assert match.from_text == broken
    assert match.to_text == fixed
    unmatched = parser.unmatched_manual_mappings()
    assert [row.from_text for row in unmatched] == ["never-hits"]


def test_unmatched_corrections_reports_unused_rule_ids(tmp_path: Path):
    html_path = tmp_path / "index.html"
    write_tmp_index_html(
        html_path,
        section_id="Test",
        section_body='<h2>1.0 Test</h2>\n<p class="schg">a → b</p>',
    )
    parser = default_index_parser(
        corrections={"unused-id": "x → y", "also-unused": "p → q"},
    )
    parser.parse(html_path)
    assert parser.unmatched_corrections() == ["unused-id", "also-unused"]


def test_parse_rule_element_sets_rule_id_on_missing_arrow():
    el = html.fragment_fromstring('<p class="schg" id="Test-bad">not a rule</p>')
    rules = default_index_parser().parse_rule_element(
        el,
        rule_id="Test-bad",
    )
    assert rules[0]["rule_id"] == "Test-bad"
    assert "status" not in rules[0]


def test_parse_rule_element_sets_rule_id_on_quoted_prose():
    el = html.fragment_fromstring(
        '<p class="schg" id="Test-prose">"quoted prose only"</p>'
    )
    rules = default_index_parser().parse_rule_element(
        el,
        rule_id="Test-prose",
    )
    assert rules[0]["rule_id"] == "Test-prose"
    assert "status" not in rules[0]


def test_parse_rule_element_indo_aryan_chain_retains_optional_segments():
    """Regression: trailing ``(a)`` on second spine token is phonology, not gloss."""
    el = html.fragment_fromstring(
        '<p class="schg" id="Central-Middle-Indo-Aryan-ai,ja-au,wa">'
        "a{i,j}(a) a{u,w}(a) → e o</p>"
    )
    rules = default_index_parser().parse_rule_element(
        el,
        rule_id="Central-Middle-Indo-Aryan-ai,ja-au,wa",
    )
    assert len(rules) == 1
    assert rules[0]["stages"] == ["a{i,j}(a) a{u,w}(a)", "e o"]
    assert rules[0]["raw"] == "a{i,j}(a) a{u,w}(a) → e o"
    assert "comment" not in rules[0]
