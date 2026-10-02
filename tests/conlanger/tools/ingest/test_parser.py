from pathlib import Path

import pytest
from helpers import default_index_parser, write_tmp_index_html

from conlanger.scripts.config_loaders import load_parser_config
from conlanger.utils.mappings import (
    IpaMapping,
    ManualMapping,
    ManualMappingMatch,
    ParserConfig,
)


@pytest.fixture
def fx_rule():
    return {
        "rule_id": "Klingon-abc",
        "section_index": "1.0",
        "section_name": "Proto-IndoEuropean to Klingon",
        "source": "index:1",
    }


def test_parse_rule_string_medial_with_exception_env_normalized(fx_rule):
    raw = "b → h / medially, ! r_"
    rules = default_index_parser().parse_rule_string(**fx_rule, raw=raw)
    assert rules[0] == {
        "raw": raw,
        "rule_id": fx_rule["rule_id"],
        "source": fx_rule["source"],
        "stages": ["b", "h"],
        "env": "_",
        "exception": "r_",
        "comment": "medially,",
    }


# TODO: Replace with test_parse_element_handles_dialectal
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


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a → i / in northern dialects", {"dialect": "northern"}),
        ("a → i / dialectal", {"dialect": True}),
    ],
)
def test_parse_element_handles_dialectal(fx_rule, raw, expected):
    parser = default_index_parser()
    rules = parser.parse_rule_string(**fx_rule, raw=raw)
    assert rules[0]["env"] == expected


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


def test_parser_marks_skip_sections_from_config(tmp_path: Path):
    html_path = tmp_path / "skip_section.html"
    config_path = tmp_path / "parser_config.yml"
    config_path.write_text(
        "ipa_mappings_confidence: [high]\n"
        "skip_sections:\n"
        '  - id: "9.9.9"\n'
        '    reason: "test skip"\n',
        encoding="utf-8",
    )
    for name, content in [
        ("ipa_mappings.yml", "{}\n"),
        ("manual_mappings.yml", "[]\n"),
        ("feature_mappings.yml", "{}\n"),
        ("index_corrections.yml", "rules: []\n"),
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


def test_parse_order_correction_then_section_then_manual(fx_rule):
    raw = "*D → d"
    config = ParserConfig(
        section_mappings_sections={
            fx_rule["section_index"]: {"*D": "D"},
        },
        corrections={fx_rule["rule_id"]: "*D → mapped"},
        manual_mappings=[
            ManualMapping(from_text="D → mapped", to_text="D → manual"),
        ],
    )
    parser = default_index_parser(parser_config=config)
    rules = parser.parse_rule_string(**fx_rule, raw=raw)
    assert rules[0]["raw"] == raw
    assert rules[0]["stages"] == ["D", "manual"]


def test_parser_marks_skip_rules_from_config(tmp_path: Path):
    raw = "i → j [ə?] → {e,a}"
    html_path = tmp_path / "skip_rule.html"
    write_tmp_index_html(
        html_path,
        section_id="SkipRule",
        section_body=f"""\
<h2>1.0 Hold-out</h2>
<p class="schg" id="Hold-out-rule">{raw}</p>""",
    )
    config = ParserConfig(
        skip_rules=[{"id": "Hold-out-rule", "reason": "unrepresentable chain"}],
    )
    parser = default_index_parser(parser_config=config)
    rule = parser.parse(html_path)["sections"][0]["rules"][0]

    assert rule == {
        "raw": raw,
        "rule_id": "Hold-out-rule",
        "source": "skip_rule.html:9",
        "stages": [],
        "status": "skipped",
        "comment": "unrepresentable chain",
    }


def test_index_diachronica_parser_accepts_custom_parser_config(fx_rule):
    config = ParserConfig(
        ipa_mappings_confidence=frozenset({"high"}),
        ipa_mappings=(
            IpaMapping(index_feature="è", ipa_target="ɛ", confidence="medium"),
            IpaMapping(index_feature="é", ipa_target="e", confidence="high"),
        ),
    )
    parser = default_index_parser(parser_config=config)

    raw = "é → è / _#"

    rules = parser.parse_rule_string(**fx_rule, raw=raw)

    assert rules == [
        {
            "raw": raw,
            "rule_id": fx_rule["rule_id"],
            "source": fx_rule["source"],
            "stages": ["e", "è"],
            "env": "_#",
        }
    ]


@pytest.mark.parametrize(
    ("raw,expected"),
    [
        (
            "V → ∅ / V_C in northern dialects",
            {"env": {"dialect": "northern", "context": "V_C"}},
        ),
        (
            "V → ∅ / V_C in northern dialects ! in southern dialects",
            {
                "env": {"dialect": "northern", "context": "V_C"},
                "exception": {"dialect": "southern"},
            },
        ),
        (
            "V → ∅ / in northern and southern dialects",
            {"env": {"dialect": ["northern", "southern"]}},
        ),
        (
            "V → ∅ / dialectal",
            {"env": {"dialect": True}},
        ),
        (
            "V → ∅ / dialectal ; in northern dialects",
            {"env": {"dialect": True}, "comment": "in northern dialects"},
        ),
        (
            "V → ∅ / #_V",
            {"env": "#_V"},
        ),
    ],
)
def test_parse_rule_string_apply_dialects_to_context(fx_rule, raw, expected):
    parser = default_index_parser()
    rules = parser.parse_rule_string(**fx_rule, raw=raw)

    assert rules[0] == {
        "raw": raw,
        "rule_id": fx_rule["rule_id"],
        "source": fx_rule["source"],
        "stages": ["V", "∅"],
        **expected,
    }


def test_parse_rule_string_without_manual_row_unchanged(fx_rule):
    parser = default_index_parser(manual_mappings=[])
    rules = parser.parse_rule_string(**fx_rule, raw="a → b")
    assert rules[0]["stages"] == ["a", "b"]
    assert parser.manual_mapping_matches == []
    assert parser.unmatched_manual_mappings == []


def test_parse_rule_string_manual_mappings_matches_and_unmatched(fx_rule):
    broken = "m̩ n̩ → am an / _{s,({m,j,w)V}"
    fixed = "m̩ n̩ → am an / _{s,({m,j,w})V}"
    manual_mappings = [
        ManualMapping(from_text=broken, to_text=fixed, reason="bracket"),
        ManualMapping(from_text="never-hits", to_text="x", reason="unused"),
    ]
    parser = default_index_parser(
        manual_mappings=manual_mappings,
    )
    rules = parser.parse_rule_string(**fx_rule, raw=broken)

    assert rules == [
        {
            "raw": broken,
            "rule_id": fx_rule["rule_id"],
            "source": fx_rule["source"],
            "stages": ["m̩ n̩", "am an"],
            "env": "_{s,({m,j,w})V}",
        }
    ]

    assert parser.manual_mapping_matches == [
        ManualMappingMatch(**fx_rule, from_text=broken, to_text=fixed, reason="bracket")
    ]
    assert parser.unmatched_manual_mappings == [manual_mappings[1]]


def test_unmatched_corrections(fx_rule):
    parser = default_index_parser(
        corrections={"Klingon-abc": "x → y", "Klingon-def": "x → y"},
    )
    parser.parse_rule_string(**fx_rule)
    assert parser.unmatched_corrections == ["Klingon-def"]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a{i,j}(a) a{u,w}(a) → e o", {"stages": ["a{i,j}(a) a{u,w}(a)", "e o"]}),
        ('"quoted prose only"', {"stages": [], "comment": '"quoted prose only"'}),
        ("a → b", {"stages": ["a", "b"]}),
        # ("not-a-rule", {"stages": [], "comment": "not-a-rule"}),
    ],
)
def test_parse_rule_string_comment(fx_rule, raw, expected):
    rules = default_index_parser().parse_rule_string(
        **fx_rule,
        raw=raw,
    )
    assert rules == [
        {
            "raw": raw,
            "rule_id": fx_rule["rule_id"],
            "source": fx_rule["source"],
            **expected,
        }
    ]
