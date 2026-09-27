"""YAML round-trip and validation for parse-time IndexRule / IndexContext."""

from __future__ import annotations

import pytest
import yaml

from conlanger.tools.ingest.index_models import IndexContext, IndexRule


@pytest.mark.parametrize(
    "yaml_doc, expected",
    [
        pytest.param(
            """
env:
  context: "#_"
  position:
    adjacent_to: C
  dialect: northern
""",
            {
                "context": "#_",
                "position": {"adjacent_to": "C"},
                "dialect": "northern",
            },
            id="context_position_dialect_scalar",
        ),
        pytest.param(
            """
env:
  position:
    adjacent_to:
      - N
      - V
    medial: true
  dialect:
    - west
    - gascon
""",
            {
                "position": {"adjacent_to": ["N", "V"], "medial": True},
                "dialect": ["west", "gascon"],
            },
            id="position_lists_and_dialect_list",
        ),
        pytest.param(
            """
env:
  dialect: true
""",
            {
                "dialect": True,
            },
            id="dialect_bool",
        ),
    ],
)
def test_index_context_yaml_round_trip(yaml_doc, expected):
    loaded = yaml.safe_load(yaml_doc)
    ctx = IndexContext.model_validate(loaded["env"])
    assert ctx.model_dump(exclude_none=True) == expected
    round_trip = yaml.safe_load(
        yaml.safe_dump({"env": ctx.model_dump(exclude_none=True)})
    )
    assert round_trip["env"] == expected


def test_index_rule_string_env_round_trip():
    rule = IndexRule(
        stages=["a", "b"],
        env="_#",
        raw="a → b / _#",
        source="index.html:1",
    )
    dumped = rule.to_index_dict()
    assert dumped == {
        "stages": ["a", "b"],
        "env": "_#",
        "raw": "a → b / _#",
        "source": "index.html:1",
    }
    restored = IndexRule.model_validate(dumped)
    assert restored == rule


def test_index_rule_structured_env_to_index_dict():
    rule = IndexRule(
        stages=["x", "y"],
        env=IndexContext(
            context="#_",
            position={"adjacent_to": "C"},
            dialect="northern",
        ),
        raw="x → y",
        source="index.html:2",
        sporadic=True,
        rule_id="Test-id",
    )
    dumped = rule.to_index_dict()
    assert dumped["env"] == {
        "context": "#_",
        "position": {"adjacent_to": "C"},
        "dialect": "northern",
    }
    assert dumped["sporadic"] is True
    assert dumped["rule_id"] == "Test-id"
    assert IndexRule.model_validate(dumped) == rule
