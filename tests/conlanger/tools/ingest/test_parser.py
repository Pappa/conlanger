import pytest
from lxml import html

from conlanger.ingest import Index, IndexDiachronicaParser, IndexRule
from conlanger.ingest.models.mappings import (
    IpaMapping,
    ManualMapping,
    ManualMappingMatch,
    ParserConfig,
)

_FX_SECTION_INDEX = "1.0"
_FX_SECTION_NAME = "Proto-Indo-European to Klingon"


@pytest.fixture
def fx_rule() -> IndexRule:
    return IndexRule(
        raw="a → b",
        source="index:1",
        rule_id="Klingon-abc",
    )


def _rule_dump(rule: IndexRule) -> dict:
    return rule.model_dump(exclude_none=True, mode="python")


def prepare_parser(
    fx_rule: IndexRule | None = None,
    *,
    parser_config: ParserConfig | None = None,
) -> IndexDiachronicaParser:
    parser = IndexDiachronicaParser(parser_config=parser_config)
    if fx_rule is not None:
        parser.update_current_section(_FX_SECTION_INDEX, _FX_SECTION_NAME)
    return parser


def test_parse_rule_string_medial_with_exception_env_normalized(fx_rule):
    raw = "b → h / medially, ! r_"
    parser = prepare_parser(fx_rule)
    rules = parser.parse_rule_string(fx_rule.rule_id, fx_rule.source, raw)
    assert _rule_dump(rules[0]) == {
        "raw": raw,
        "rule_id": fx_rule.rule_id,
        "source": fx_rule.source,
        "stages": ["b", "h"],
        "env": "_",
        "exception": "r_",
        "comment": "medially,",
    }


# TODO: Replace with test_parse_element_handles_dialectal
def test_parse_element_handles_dialectal_rules():
    root = html.document_fromstring(
        """\
<!doctype html><html><body><section id="Dialectal">
<h2>1.0 Proto-Indo-European to Klingon</h2>
<p class="schg">a → i / in northern dialects</p>
<p class="schg">a → i / dialectal</p>
</section></body></html>"""
    )
    parser = IndexDiachronicaParser()
    doc = parser.parse(root)
    assert doc["name"] == "Index Diachronica"
    rule1 = doc["sections"][0]["rules"][0]
    rule2 = doc["sections"][0]["rules"][1]

    assert rule1["env"] == {"dialect": "northern"}
    assert rule2["env"] == {"dialect": True}
    assert "comments" not in doc["sections"][0]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a → i / in northern dialects", {"dialect": "northern"}),
        ("a → i / dialectal", {"dialect": True}),
    ],
)
def test_parse_element_handles_dialectal(fx_rule, raw, expected):
    parser = prepare_parser(fx_rule)
    rules = parser.parse_rule_string(fx_rule.rule_id, fx_rule.source, raw)
    assert _rule_dump(rules[0])["env"] == expected


@pytest.mark.parametrize("h2_element", ["", "<h2>   </h2>"])
def test_parser_skips_section_without_h2(h2_element):
    root = html.document_fromstring(
        f"""\
<!doctype html><html><body><section id="Klingon">
{h2_element}
<p class="schg">a → b</p>
</section></body></html>"""
    )
    assert IndexDiachronicaParser().parse(root)["sections"] == []


def test_parser_marks_skip_sections_from_config():
    root = html.document_fromstring(
        """\
<!doctype html><html><body><section id="Klingon">
<h2>9.9.9 Proto-Indo-European to Klingon</h2>
<p class="schg">a → b</p>
</section></body></html>"""
    )
    parser = IndexDiachronicaParser(
        parser_config=ParserConfig(
            skip_sections=[{"id": "9.9.9", "reason": "test skip"}],
        ),
    )
    sec = parser.parse(root)["sections"][0]

    assert sec["index"] == "9.9.9"
    assert sec["status"] == "skipped"
    assert "comments" not in sec


def test_parser_config_resolved_section_mappings_ancestry_and_override():
    config = ParserConfig(
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
            _FX_SECTION_INDEX: {"*D": "D"},
        },
        corrections={fx_rule.rule_id: "*D → mapped"},
        manual_mappings=[
            ManualMapping(from_text="D → mapped", to_text="D → manual"),
        ],
    )
    parser = prepare_parser(fx_rule, parser_config=config)
    rules = parser.parse_rule_string(fx_rule.rule_id, fx_rule.source, raw)
    dumped = _rule_dump(rules[0])
    assert dumped["raw"] == raw
    assert dumped["stages"] == ["D", "manual"]


def test_parser_marks_skip_rules_from_config():
    raw = "i → j [ə?] → {e,a}"
    root = html.document_fromstring(
        f"""\
<!doctype html><html><body><section id="SkipRule">
<h2>1.0 Hold-out</h2>
<p class="schg" id="Hold-out-rule">{raw}</p>
</section></body></html>"""
    )
    config = ParserConfig(
        skip_rules=[{"id": "Hold-out-rule", "reason": "unrepresentable chain"}],
    )
    parser = IndexDiachronicaParser(parser_config=config)
    rule = parser.parse(root)["sections"][0]["rules"][0]

    assert rule == {
        "raw": raw,
        "rule_id": "Hold-out-rule",
        "source": "index:3",
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
    parser = prepare_parser(fx_rule, parser_config=config)

    raw = "é → è / _#"

    rules = parser.parse_rule_string(fx_rule.rule_id, fx_rule.source, raw)

    assert [_rule_dump(rule) for rule in rules] == [
        {
            "raw": raw,
            "rule_id": fx_rule.rule_id,
            "source": fx_rule.source,
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
    parser = prepare_parser(fx_rule)
    rules = parser.parse_rule_string(fx_rule.rule_id, fx_rule.source, raw)

    assert _rule_dump(rules[0]) == {
        "raw": raw,
        "rule_id": fx_rule.rule_id,
        "source": fx_rule.source,
        "stages": ["V", "∅"],
        **expected,
    }


def test_parse_rule_string_without_manual_row_unchanged(fx_rule):
    parser = prepare_parser(fx_rule)
    rules = parser.parse_rule_string(fx_rule.rule_id, fx_rule.source, "a → b")
    assert _rule_dump(rules[0])["stages"] == ["a", "b"]
    assert parser.manual_mapping_matches == []
    assert parser.unmatched_manual_mappings == []


def test_parse_rule_string_manual_mappings_matches_and_unmatched(fx_rule):
    broken = "m̩ n̩ → am an / _{s,({m,j,w)V}"
    fixed = "m̩ n̩ → am an / _{s,({m,j,w})V}"
    manual_mappings = [
        ManualMapping(from_text=broken, to_text=fixed, reason="bracket"),
        ManualMapping(from_text="never-hits", to_text="x", reason="unused"),
    ]
    config = ParserConfig(manual_mappings=manual_mappings)
    parser = prepare_parser(fx_rule, parser_config=config)
    rules = parser.parse_rule_string(fx_rule.rule_id, fx_rule.source, broken)

    assert [_rule_dump(rule) for rule in rules] == [
        {
            "raw": broken,
            "rule_id": fx_rule.rule_id,
            "source": fx_rule.source,
            "stages": ["m̩ n̩", "am an"],
            "env": "_{s,({m,j,w})V}",
        }
    ]

    assert parser.manual_mapping_matches == [
        ManualMappingMatch(
            section_index=_FX_SECTION_INDEX,
            section_name=_FX_SECTION_NAME,
            rule_id=fx_rule.rule_id or "",
            source=fx_rule.source,
            from_text=broken,
            to_text=fixed,
        )
    ]
    assert parser.unmatched_manual_mappings == [manual_mappings[1]]


def test_unmatched_corrections(fx_rule):
    config = ParserConfig(corrections={"Klingon-abc": "x → y", "Klingon-def": "x → y"})
    parser = prepare_parser(fx_rule, parser_config=config)
    parser.parse_rule_string(fx_rule.rule_id, fx_rule.source)
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
    parser = prepare_parser(fx_rule)
    rules = parser.parse_rule_string(fx_rule.rule_id, fx_rule.source, raw)
    assert [_rule_dump(rule) for rule in rules] == [
        {
            "raw": raw,
            "rule_id": fx_rule.rule_id,
            "source": fx_rule.source,
            **expected,
        }
    ]


def test_parse_return_round_trips_through_index_model(fx_rule):
    root = html.document_fromstring(
        """\
<!doctype html><html><body><section id="Golden">
<h2>1.0 Proto-Indo-European to Klingon</h2>
<p class="schg" id="golden-rule">a → b / _#</p>
</section></body></html>"""
    )
    doc = prepare_parser(fx_rule).parse(root, source_file="golden.html")
    assert doc == Index.model_validate(doc).model_dump(exclude_none=True, mode="python")
    assert doc["name"] == "Index Diachronica"
    assert doc["sections"][0]["rules"][0]["source"] == "golden.html:3"
    assert "comments" not in doc["sections"][0]


def test_parse_returns_index_document_with_name_and_structured_env(fx_rule):
    root = html.document_fromstring(
        """\
<!doctype html><html><body><section id="Dialectal">
<h2>1.0 Proto-Indo-European to Klingon</h2>
<p class="schg">a → i / in northern dialects</p>
</section></body></html>"""
    )
    doc = prepare_parser(fx_rule).parse(root)
    assert doc["name"] == "Index Diachronica"
    assert doc["sections"][0]["rules"][0]["env"] == {"dialect": "northern"}
