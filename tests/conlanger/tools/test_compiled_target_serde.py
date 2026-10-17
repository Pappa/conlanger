"""Tests for ``compiled_target_serde``."""

from __future__ import annotations

import pytest

from conlanger.compile.models.config import CompilerConfig
from conlanger.compile.models.rules import (
    DiachronicSeries,
    RuleCitation,
    RuleComment,
    RuleTitle,
    SoundChangeRule,
)
from conlanger.tools.compiled_target_serde import (
    _deserialize_rule_part,
    _serialize_rule_part,
    deserialize_series,
    inventory_target_from_yaml,
    inventory_target_to_yaml,
    serialize_series,
    sound_change_rule_from_series,
)
from conlanger.tools.inventory_targets import (
    InventoryTarget,
    _series_for_sound_change_rule,
    resolve_inventory_targets,
)

_SECTION = {"index": "1.0", "section": "Test"}


def test_serialize_and_deserialize_title_citation_comment():
    title = _serialize_rule_part(RuleTitle("1", "Sec#r0"))
    assert _deserialize_rule_part(title).value == "1 - Sec#r0"
    citation = _serialize_rule_part(RuleCitation("ref"))
    assert _deserialize_rule_part(citation).value == "ref"
    comment = _serialize_rule_part(RuleComment("note"))
    assert _deserialize_rule_part(comment).value == "note"


def test_deserialize_rule_part_rejects_unknown_type():
    with pytest.raises(ValueError, match="unsupported"):
        _deserialize_rule_part({"type": "nope"})


def test_inventory_target_to_yaml_requires_series():
    with pytest.raises(ValueError, match="missing series"):
        inventory_target_to_yaml(InventoryTarget())


def test_inventory_target_from_yaml_round_trip():
    rule = {"stages": ["a", "b"], "source": "s:1"}
    target = resolve_inventory_targets(_SECTION, rule, "r0")[0]
    restored = inventory_target_from_yaml(inventory_target_to_yaml(target))
    assert restored.alt_idx == target.alt_idx
    assert restored.step_idx == target.step_idx


def test_inventory_target_from_yaml_preserves_group_mapped_env(
    fx_sample_compiler_config,
):
    section = {"index": "6.2.2.1.2", "section": "Test"}
    rule = {
        "stages": ["f", "p"],
        "env": "#_V{Z,C[-voice],r}",
        "source": "s:1",
    }
    target = resolve_inventory_targets(
        section,
        rule,
        "r0",
        compiler_config=fx_sample_compiler_config,
    )[0]
    assert target.field_rule is not None
    yaml_target = inventory_target_to_yaml(target)
    assert "[+cont]" in yaml_target["rule"]
    assert "Z" not in yaml_target["rule"]

    restored = inventory_target_from_yaml(yaml_target)
    assert str(restored.field_rule).strip() == yaml_target["rule"]
    assert restored.field_rule.env is not None
    assert "[+cont]" in restored.field_rule.env.compiled


def test_series_round_trip_matches_rule_line():
    rule = {"stages": ["a", "b"], "source": "s:1"}
    target = resolve_inventory_targets(_SECTION, rule, "r0")[0]
    assert target.series is not None
    yaml_target = inventory_target_to_yaml(target)
    restored = deserialize_series(yaml_target["series"])
    field_rule = sound_change_rule_from_series(restored)
    assert field_rule is not None
    assert str(field_rule).strip() == yaml_target["rule"]


def test_serialize_series_from_mini_series():
    rule = SoundChangeRule(
        input="a",
        output="b",
        detect_alternatives=False,
        compiler_config=CompilerConfig(),
    )
    series = _series_for_sound_change_rule(_SECTION, "r0", rule)
    payload = serialize_series(series)
    restored = deserialize_series(payload)
    assert isinstance(restored, DiachronicSeries)
    assert str(sound_change_rule_from_series(restored)).strip() == "a > b"
