import pytest

from conlanger.ingest.models.index_models import IndexContext, IndexRule
from conlanger.ingest.parser import IndexDiachronicaParser
from conlanger.ingest.utils.index_context_position import (
    apply_index_context_position_extraction,
    extract_position_from_context,
)


@pytest.mark.parametrize(
    ("text", "expected_context", "expected_position"),
    [
        ("adjacent to C", None, {"adjacent_to": "C"}),
        ("adjacent to {s,z}", None, {"adjacent_to": "{s,z}"}),
        ("adjacent to V[+nasal]", None, {"adjacent_to": "V[+nasal]"}),
        ("adjacent to ŋ", None, {"adjacent_to": "ŋ"}),
        ("near u", None, {"near": "u"}),
        ("near {ħ,ʕ}", None, {"near": "{ħ,ʕ}"}),
        ("medially", None, {"medial": True}),
        ("when medial", None, {"medial": True}),
        (
            "C[-voice]_n, when medial",
            "C[-voice]_n",
            {"medial": True},
        ),
        ("_#", "_#", {}),
    ],
)
def test_extract_position_from_context(text, expected_context, expected_position):
    context, position = extract_position_from_context(text)
    assert context == expected_context
    assert position == expected_position


@pytest.mark.parametrize(
    ("input_env", "expected"),
    [
        (
            "medially",
            {"position": {"medial": True}},
        ),
        (
            "adjacent to {S,s,l̥}",
            {"position": {"adjacent_to": "{S,s,l̥}"}},
        ),
        (
            "near u",
            {"position": {"near": "u"}},
        ),
    ],
)
def test_apply_index_context_position_extraction_env(input_env, expected):
    rule = IndexRule(
        raw="x",
        source="t",
        stages=["a", "b"],
        env=input_env,
    )
    result = apply_index_context_position_extraction(rule)
    assert result.env is not None
    dumped = result.env.model_dump(exclude_none=True, mode="python")
    assert dumped == expected


def test_parser_near_u_inventory_rule_id():
    raw = "β b m → βʷ bʷ mʷ / near u"
    parser = IndexDiachronicaParser()
    rule = parser.parse_rule_string("Hiw-β-b-m", "index:3109", raw)[0]
    assert rule.env == IndexContext(position={"near": "u"})


def test_parser_medial_with_exception_structured():
    raw = "b → h / medially, ! r_"
    parser = IndexDiachronicaParser()
    rule = parser.parse_rule_string("test", "t", raw)[0]
    assert rule.env == IndexContext(position={"medial": True})
    assert rule.exception == IndexContext(context="r_")


def test_parser_adjacent_to_set_from_inventory_surface():
    raw = "F[+voice] → F[-voice] / adjacent to {S,ts}"
    parser = IndexDiachronicaParser()
    rule = parser.parse_rule_string("c332344f", "index:4755", raw)[0]
    assert rule.env == IndexContext(position={"adjacent_to": "{S,ts}"})


def test_parser_bare_medial_inventory_surface():
    raw = "t → l / medially"
    parser = IndexDiachronicaParser()
    rule = parser.parse_rule_string("703b4948", "index:13987", raw)[0]
    assert rule.env == IndexContext(position={"medial": True})
