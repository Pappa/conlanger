from pathlib import Path

import pandas as pd
import pytest
from lxml import html

from conlanger.tools.parsers import (
    ARROW,
    DEFAULT_GROUP_MAPPINGS_CSV,
    GroupMapping,
    IndexDiachronicaParser,
    extract_rule_parts,
    extract_text_with_subs,
    load_group_mappings,
    normalize_stress_marks,
    normalize_symbols,
    parse_rule_element,
    parse_section_heading,
    split_env_exception,
    split_input_output,
    strip_leading_index_list_marker,
    split_output_rest,
    split_post_arrow,
)

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
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")
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
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rule["input"] == "w"
    assert rule["output"] == "∅"
    assert rule["env"] == "#C_V"
    assert rule["exception"] == "_i(ː)"


def test_parse_rule_element_no_env():
    el = html.fragment_fromstring('<p class="schg">ɬ → l</p>', create_parent=False)
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rule["input"] == "ɬ"
    assert rule["output"] == "l"
    assert "env" not in rule
    assert "exception" not in rule


def test_parse_rule_element_missing_arrow():
    el = html.fragment_fromstring('<p class="schg">a to b no arrow</p>', create_parent=False)
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rule["input"] == ""
    assert rule["output"] == ""
    assert rule["skipped"] == f"missing separator {ARROW!r}"


def test_parse_rule_element_arrow_without_spaces():
    el = html.fragment_fromstring('<p class="schg">a \u2192\u0259 / _#</p>', create_parent=False)
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rule["input"] == "a"
    assert rule["output"] == "ə"
    assert rule["env"] == "_#"
    assert "skipped" not in rule


def test_parse_rule_element_bang_exception():
    el = html.fragment_fromstring(
        '<p class="schg">s \u2192 \u0283 / !V_</p>', create_parent=False
    )
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rule["input"] == "s"
    assert rule["output"] == "ʃ"
    assert "env" not in rule
    assert rule["exception"] == "V_"


def test_parse_rule_element_env_and_bang_exception():
    el = html.fragment_fromstring(
        '<p class="schg">w \u2192 \u2205 / _# ! k(\u02d0)_</p>', create_parent=False
    )
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")
    assert rule["input"] == "w"
    assert rule["output"] == "∅"
    assert rule["env"] == "_#"
    assert rule["exception"] == "k(ː)_"


def test_parse_rule_element_except_without_comma():
    el = html.fragment_fromstring(
        '<p class="schg">q \u2192 \u0294 / except in several words</p>',
        create_parent=False,
    )
    rule = parse_rule_element(el, source_file="index_diachronica_original.html")
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
    assert sec["rules"][0]["input"] == "x₁"
    assert sec["rules"][0]["output"] == "k"


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


