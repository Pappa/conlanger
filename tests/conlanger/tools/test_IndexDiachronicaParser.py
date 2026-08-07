import shutil
from pathlib import Path

import pandas as pd
import pytest
from lxml import html

from conlanger.tools.asca_validator import validate_asca
from conlanger.tools.parsers import (
    ARROW,
    DEFAULT_GROUP_MAPPINGS_CSV,
    FeatureMapping,
    GroupMapping,
    IndexDiachronicaParser,
    apply_feature_mappings,
    apply_sporadic_qualifier,
    apply_stress_conditions,
    apply_trailing_glosses,
    extract_rule_parts,
    extract_semicolon_prose_from_field,
    extract_text_with_subs,
    feature_mappings_dict,
    join_rule_comment,
    load_feature_mappings,
    load_group_mappings,
    normalize_feature_matrices_in_field,
    normalize_stress_conditions,
    normalize_stress_marks,
    normalize_symbols,
    parse_rule_element,
    parse_section_heading,
    split_env_exception,
    split_input_output,
    split_output_rest,
    split_post_arrow,
    strip_leading_index_list_marker,
    strip_trailing_gloss_from_field,
    strip_uncertainty_qualifier_from_field,
    write_rule_comment_phrase_summary,
)
from conlanger.tools.phonological_ruleset import PhonologicalRuleSet

_SAMPLED_RULES_CSV = (
    Path(__file__).resolve().parents[2] / "fixtures" / "sound_change_rules.csv"
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


def _load_sampled_html_rules() -> list[tuple]:
    df = pd.read_csv(_SAMPLED_RULES_CSV, dtype=str, keep_default_na=False)
    if "kind" in df.columns:
        df = df[df["kind"].isin(["", "html_extract"])]
    cases: list[tuple] = []
    for row in df.itertuples(index=False):
        if row.expect_none == "True":
            expected = None
        else:
            expected = {"input": row.input, "output": row.output}
            if row.env:
                expected["env"] = row.env
            if row.exception:
                expected["exception"] = row.exception
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
    el = html.fragment_fromstring(
        "<p>before<sub>2</sub>after</p>", create_parent=False
    )
    assert extract_text_with_subs(el) == "before₂after"


def test_extract_text_with_subs_no_tail_after_sub():
    el = html.fragment_fromstring("<p>before<sub>2</sub></p>", create_parent=False)
    assert extract_text_with_subs(el) == "before₂"


def test_load_group_mappings_missing_columns(tmp_path: Path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("grouping\nS\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_group_mappings(bad_csv)


def test_load_group_mappings_without_comment_column(tmp_path: Path):
    csv_path = tmp_path / "minimal.csv"
    csv_path.write_text("grouping,mapping\nS,P\n", encoding="utf-8")
    mappings = load_group_mappings(csv_path)
    assert mappings == [GroupMapping("S", "P", "")]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#_", "#_"),
        ("∅", "∅"),
        ("_$%oː", "_$$oː"),
        ("$am_w", "$am_w"),
        ("in #”U", "in #U:[+stress]"),
        ('s “(for many speakers)”', 's “(for many speakers)”'),
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


def test_extract_rule_parts_strips_leading_list_marker():
    assert extract_rule_parts("— j w → i u / #_CV") == {
        "input": "j w",
        "output": "i u",
        "env": "#_CV",
    }


def test_extract_rule_parts_normalizes_chain_arrows():
    assert extract_rule_parts("dʒ → tʃ → ʃ") == {
        "input": "dʒ",
        "output": "tʃ > ʃ",
    }


def test_parse_rule_element_keeps_chain_without_env():
    el = html.fragment_fromstring(
        '<p class="schg">dʒ → tʃ → ʃ</p>', create_parent=False
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert len(rules) == 1
    assert rules[0] == {
        "input": "dʒ",
        "output": "tʃ > ʃ",
        "raw": "dʒ → tʃ → ʃ",
        "source": rules[0]["source"],
    }


def test_parse_rule_element_keeps_chain_with_env():
    el = html.fragment_fromstring(
        '<p class="schg">{θ,l} → r → l / V_V</p>', create_parent=False
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert len(rules) == 1
    assert rules[0]["input"] == "{θ,l}"
    assert rules[0]["output"] == "r > l"
    assert rules[0]["env"] == "V_V"


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
        ("a", "a"),
    ],
)
def test_strip_uncertainty_qualifier_from_field(text, expected):
    assert strip_uncertainty_qualifier_from_field(text) == expected


@pytest.mark.parametrize(
    ("text", "expected_value", "expected_captures"),
    [
        ("", "", []),
        ('h "sometimes"', "h", ['"sometimes"']),
        ("h sometimes", "h", ["sometimes"]),
        ("h (sometimes uncertain)", "h", ["(sometimes uncertain)"]),
    ],
)
def test_extract_uncertainty_qualifier_from_field(text, expected_value, expected_captures):
    from conlanger.tools.parsers import extract_uncertainty_qualifier_from_field

    value, captures = extract_uncertainty_qualifier_from_field(text)
    assert value == expected_value
    assert captures == expected_captures


def test_write_rule_comment_phrase_summary(tmp_path: Path):
    doc = {
        "sections": [
            {
                "rules": [
                    {"comment": "when stressed; sporadic in some dialects"},
                    {"comment": "plain gloss"},
                    {"input": "a", "output": "b"},
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
    assert apply_sporadic_qualifier(
        {"input": "p", "output": "h (sporadic)"}
    ) == {"input": "p", "output": "h", "sporadic": True, "comment": "(sporadic)"}


def test_apply_sporadic_qualifier_unchanged_when_no_marker():
    parts = {"input": "a", "output": "e", "env": "_#"}
    assert apply_sporadic_qualifier(parts) == parts


def test_parse_rule_element_marks_sporadic_and_strips_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">p → h (sporadic)</p>', create_parent=False
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert len(rules) == 1
    assert rules[0]["input"] == "p"
    assert rules[0]["output"] == "h"
    assert rules[0]["sporadic"] is True
    assert "(sporadic)" in rules[0]["comment"]
    assert rules[0]["raw"] == "p → h (sporadic)"


def test_parse_rule_element_strips_sporadic_env_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">qu → w / _{f,s} (sporadic)</p>', create_parent=False
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_{f,s}"
    assert rules[0]["sporadic"] is True


@pytest.mark.parametrize(
    ("text", "expected"),
    [
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
        ("_{f,s}", "_{f,s}"),
        ("_# (except as below)", "_#"),
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
            "{a,ə} / _{x,h} “in the odd-numbered of any sequence of one or more short-vowel open syllables”",
            "{a,ə} / _{x,h}",
        ),
        ("_# when unstressed", "_# when unstressed"),
        ("z > d / $_OO “", "z > d / $_OO"),
        ("k(ʼ)", "k(ʼ)"),
        ("(?)", "(?)"),
        ("C(…C)", "C(…C)"),
    ],
)
def test_strip_trailing_gloss_from_field(text, expected):
    assert strip_trailing_gloss_from_field(text) == expected


def test_apply_trailing_glosses():
    assert apply_trailing_glosses(
        {"input": "j", "output": "p (some Polynesian languages, such as Levei and Drehet)"}
    ) == {
        "input": "j",
        "output": "p",
        "comment": "(some Polynesian languages, such as Levei and Drehet)",
    }


def test_apply_trailing_glosses_keeps_field_when_strip_would_empty():
    assert apply_trailing_glosses(
        {"input": "hhy", "output": '"something like /ʒ/"'}
    ) == {
        "input": "hhy",
        "output": '"something like /ʒ/"',
        "comment": '"something like /ʒ/"',
    }


def test_parse_rule_element_strips_trailing_glosses():
    el = html.fragment_fromstring(
        '<p class="schg">w → f (Common Celtic; I’m not sure of the conditions)</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["input"] == "w"
    assert rules[0]["output"] == "f"
    assert "Celtic" in rules[0]["comment"]
    assert "Celtic" in rules[0]["raw"]


def test_parse_rule_element_strips_env_trailing_glosses():
    el = html.fragment_fromstring(
        '<p class="schg">t → k / _s̩ (Ōgami) (http://example.com)</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_s̩"
    assert "Ōgami" in rules[0]["raw"]


def test_parse_rule_element_strips_embedded_quoted_env_gloss():
    el = html.fragment_fromstring(
        '<p class="schg">z → d / “when another sibilant is in the word nearby” and (word-finally?) when</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "and (word-finally?) when"
    assert "sibilant" in rules[0]["raw"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("_C(C), when stressed", "_C(C) when stressed"),
        ("_$, when stressed", "_$ when stressed"),
        ("_N, when unstressed (?)", "_N when unstressed (?)"),
        ("when unstressed", "_ when unstressed"),
        ("when stressed unless primarily stressed", "_ when stressed unless primarily stressed"),
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
        {"input": "a", "output": "e", "env": "_C(C), when stressed"}
    ) == {"input": "a", "output": "e", "env": "_C(C) when stressed"}


def test_parse_rule_element_normalizes_stress_conditions():
    el = html.fragment_fromstring(
        '<p class="schg">a → i / _C(C), when stressed</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
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
        rules = parse_rule_element(el, source_file="index_diachronica_original.html")
        section = {
            "index": "47.1",
            "section": "Stress conditions",
            "rules": rules,
        }
        validate_asca(
            PhonologicalRuleSet(section).to_sound_change_ruleset(),
            probe_words=probe,
        )


def test_extract_rule_parts_with_symbol_normalization():
    raw = "a → b / _$%oː"
    assert extract_rule_parts(normalize_symbols(raw)) == {
        "input": "a",
        "output": "b",
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
    doc = IndexDiachronicaParser().parse(html_path)
    assert doc["abbreviations"] == {}
    assert doc["sections"][0]["rules"][0]["input"] == "S"


def test_parser_skips_section_without_h2(tmp_path: Path):
    html_path = tmp_path / "no_h2.html"
    _write_index_diachronica_html(
        html_path,
        section_id="NoH2",
        section_body='<p class="schg">a → b</p>',
    )
    assert IndexDiachronicaParser().parse(html_path)["sections"] == []


def test_parser_skips_section_with_empty_name(tmp_path: Path):
    html_path = tmp_path / "empty_name.html"
    _write_index_diachronica_html(
        html_path,
        section_id="Empty",
        section_body="""\
<h2>   </h2>
<p class="schg">a → b</p>""",
    )
    assert IndexDiachronicaParser().parse(html_path)["sections"] == []


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
    doc = IndexDiachronicaParser().parse(html_path)
    sec = doc["sections"][0]
    assert sec["rules"][0]["input"] == "a"
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
    sec = IndexDiachronicaParser().parse(html_path)["sections"][0]
    assert sec["citation"] == "Only a citation line."
    assert "rules" not in sec


@pytest.mark.parametrize(
    "post_arrow, expected",
    [
        ("ʒ s₁ s₂", ("ʒ s₁ s₂", None, None)),
        ("∅ / _s#", ("∅", "_s#", None)),
        ("ʃ / !V_", ("ʃ", None, "V_")),
        ("∅ / _# ! k(ː)_", ("∅", "_#", "k(ː)_")),
        ("∅ / #C_V, except _i(ː)", ("∅", "#C_V", "_i(ː)")),
        ("ʔ / except in several words", ("ʔ", None, "in several words")),
        ("ou øy ei, except in certain endings", ("ou øy ei", None, "in certain endings")),
        ("{∅,h} / _əNS / #_", ("{∅,h}", "_əNS", "#_")),
    ],
)
def test_split_post_arrow(post_arrow, expected):
    assert split_post_arrow(post_arrow) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            "w → ∅ / _# ! k(ː)_",
            {"input": "w", "output": "∅", "env": "_#", "exception": "k(ː)_"},
        ),
        (
            "s → ʃ / !V_",
            {"input": "s", "output": "ʃ", "exception": "V_"},
        ),
        ("ɬ → l", {"input": "ɬ", "output": "l"}),
        ("no arrow here", None),
    ],
)
def test_extract_rule_parts(raw, expected):
    assert extract_rule_parts(raw) == expected


def test_parse_rule_element_with_sub_and_env():
    el = html.fragment_fromstring(
        '<p class="schg">ʃ → s<sub>2</sub> / {i,j}_</p>', create_parent=False
    )
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["input"] == "ʃ"
    assert rule["output"] == "s₂"
    assert rule["env"] == "{i,j}_"
    assert rule["raw"] == "ʃ → s₂ / {i,j}_"
    assert rule["source"].startswith("index_diachronica_original.html:")
    assert "skipped" not in rule


def test_parse_rule_element_with_exception():
    el = html.fragment_fromstring(
        '<p class="schg">w → ∅ / #C_V, except _i(ː)</p>', create_parent=False
    )
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["input"] == "w"
    assert rule["output"] == "∅"
    assert rule["env"] == "#C_V"
    assert rule["exception"] == "_i(ː)"


def test_parse_rule_element_no_env():
    el = html.fragment_fromstring('<p class="schg">ɬ → l</p>', create_parent=False)
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["input"] == "ɬ"
    assert rule["output"] == "l"
    assert "env" not in rule
    assert "exception" not in rule


def test_parse_rule_element_missing_arrow():
    el = html.fragment_fromstring('<p class="schg">a to b no arrow</p>', create_parent=False)
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["input"] == ""
    assert rule["output"] == ""
    assert rule["skipped"] == f"missing separator {ARROW!r}"


def test_parse_rule_element_arrow_without_spaces():
    el = html.fragment_fromstring('<p class="schg">a \u2192\u0259 / _#</p>', create_parent=False)
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["input"] == "a"
    assert rule["output"] == "ə"
    assert rule["env"] == "_#"
    assert "skipped" not in rule


def test_parse_rule_element_bang_exception():
    el = html.fragment_fromstring(
        '<p class="schg">s \u2192 \u0283 / !V_</p>', create_parent=False
    )
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["input"] == "s"
    assert rule["output"] == "ʃ"
    assert "env" not in rule
    assert rule["exception"] == "V_"


def test_parse_rule_element_env_and_bang_exception():
    el = html.fragment_fromstring(
        '<p class="schg">w \u2192 \u2205 / _# ! k(\u02d0)_</p>', create_parent=False
    )
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["input"] == "w"
    assert rule["output"] == "∅"
    assert rule["env"] == "_#"
    assert rule["exception"] == "k(ː)_"


def test_parse_rule_element_except_without_comma():
    el = html.fragment_fromstring(
        '<p class="schg">q \u2192 \u0294 / except in several words</p>',
        create_parent=False,
    )
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")[0]
    assert rule["input"] == "q"
    assert rule["output"] == "ʔ"
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
    doc = IndexDiachronicaParser().parse(html_path, source_file="sample.html")
    sec = doc["sections"][0]
    assert sec["citation"] == "Mecislau, from Ehret (1995), Title"
    assert [c["raw"] for c in sec["comments"]] == [
        "NB: Does not include vowel developments.",
        "Interleaved note",
    ]
    assert len(sec["rules"]) == 2
    assert sec["rules"][0]["input"] == "k"
    assert sec["rules"][0]["output"] == "k"
    assert sec["rules"][0]["raw"] == "x₁ → k"


def test_parse_expands_afro_asiatic_series_tokens(tmp_path: Path):
    html_path = tmp_path / "afro.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    doc = IndexDiachronicaParser().parse(html_path, source_file="afro.html")
    aari = next(sec for sec in doc["sections"] if sec["index"] == "6.1.2.1")
    rule = aari["rules"][0]
    assert rule["input"] == "ʃ z tʃ"
    assert rule["output"] == "ʃ z tʃ"
    assert "s₁" in rule["raw"]
    assert aari["abbreviations"]["s₁"] == "ʃ"


def test_parse_leaves_positional_slots_literal(tmp_path: Path):
    html_path = tmp_path / "positional.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    doc = IndexDiachronicaParser().parse(html_path, source_file="positional.html")
    chamic = next(sec for sec in doc["sections"] if sec["index"] == "10.2.1")
    rule = chamic["rules"][0]
    assert rule["input"] == "C₁C₂"
    assert rule["output"] == "C₂"


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


def test_load_group_mappings_default_csv():
    assert DEFAULT_GROUP_MAPPINGS_CSV.is_file()
    mappings = load_group_mappings()
    abbrev = {m.grouping: m.mapping for m in mappings}
    assert abbrev["S"] == "P"
    assert abbrev["A"] == "O:[+delrel]"
    assert abbrev["R"] == "[+son,-syll]"
    assert "M" not in abbrev
    assert all(isinstance(m, GroupMapping) for m in mappings)


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
    doc = IndexDiachronicaParser().parse(html_path, source_file="mapped.html")
    assert doc["abbreviations"] == {}
    rule = doc["sections"][0]["rules"][0]
    assert rule["input"] == "a"
    assert rule["output"] == "b"
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
    doc = IndexDiachronicaParser().parse(html_path, source_file="unmapped.html")
    assert doc["abbreviations"] == {}
    rule = doc["sections"][0]["rules"][0]
    assert rule["input"] == "S"
    assert rule["env"] == "V_V"
    assert IndexDiachronicaParser().abbreviations() == {}


def test_load_feature_mappings_from_default_csv():
    rows = load_feature_mappings()
    assert rows
    by_name = {row.index_feature: row for row in rows}
    assert by_name["voiced"].mapping_kind == "rename"
    assert by_name["short"].mapping_kind == "rename_invert"
    assert by_name["short"].asca_target == "long"


def test_normalize_feature_matrices_in_field_rename():
    mappings = feature_mappings_dict()
    assert normalize_feature_matrices_in_field("C[+voiced]", mappings) == "C[+voice]"
    assert normalize_feature_matrices_in_field("N[-voiced]", mappings) == "N[-voice]"
    assert normalize_feature_matrices_in_field("C[+ sibilant]", mappings) == "C[+strident]"


def test_normalize_feature_matrices_in_field_rename_invert():
    mappings = feature_mappings_dict()
    assert normalize_feature_matrices_in_field("u[+short]", mappings) == "u[-long]"
    assert normalize_feature_matrices_in_field("V[-short]", mappings) == "V[+long]"


def test_normalize_feature_matrices_in_field_leaves_raw_tokens_outside_brackets():
    mappings = feature_mappings_dict()
    assert (
        normalize_feature_matrices_in_field("short u", mappings) == "short u"
    )


def test_apply_feature_mappings():
    mappings = {
        "voiced": FeatureMapping("voiced", "rename", "voice", confidence="high"),
    }
    assert apply_feature_mappings(
        {"input": "C[+voiced]", "output": "C[+voice]"},
        mappings,
    ) == {"input": "C[+voice]", "output": "C[+voice]"}


def test_parse_rule_element_normalizes_feature_matrices():
    el = html.fragment_fromstring(
        '<p class="schg">N → N / C[+voiced]</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["input"] == "N"
    assert rules[0]["env"] == "C[+voice]"
    assert "[+voiced]" in rules[0]["raw"]


def test_parse_rule_element_normalizes_short_to_neg_long():
    el = html.fragment_fromstring(
        '<p class="schg">v → ∅ / u[+short]_V[+short]</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "u[-long]_V[-long]"
    assert "[+short]" in rules[0]["raw"]


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parse_rule_element_voiced_matrix_validates_asca():
    el = html.fragment_fromstring(
        '<p class="schg">s → z / _C[+voiced]</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    section = {"index": "17.12", "section": "Voicing", "rules": rules}
    validate_asca(
        PhonologicalRuleSet(section).to_sound_change_ruleset(),
        probe_words=Path("tests/fixtures/asca_probe_words.wsca"),
    )


def test_join_rule_comment():
    assert join_rule_comment(None, "  a  ", "b") == "a; b"
    assert join_rule_comment() is None


def test_extract_semicolon_prose_captures_tail():
    cleaned, captures = extract_semicolon_prose_from_field(
        "depending on the environment; again, the article is unclear"
    )
    assert cleaned == "depending on the environment"
    assert captures == ["again, the article is unclear"]


def test_parse_rule_element_captures_semicolon_comment():
    el = html.fragment_fromstring(
        '<p class="schg">V → ∅ / short only; blocked by following consonant</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "short only"
    assert "blocked by following consonant" in rules[0]["comment"]
    assert "; blocked" in rules[0]["raw"]


def test_parse_rule_element_captures_short_only_paren_in_env():
    el = html.fragment_fromstring(
        '<p class="schg">i → e / _CVC#, when stressed (short only)</p>',
        create_parent=False,
    )
    rules = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rules[0]["env"] == "_CVC#"
    assert "short only" in rules[0]["comment"]
    assert "when stressed" in rules[0]["comment"]

