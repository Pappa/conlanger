"""Tests for ``compiled_rule_shape`` (asca_rules.yml v4 per-rule layout)."""

from __future__ import annotations

import pytest

from conlanger.compile.models.config import CompilerConfig
from conlanger.tools.compiled_rule_shape import (
    compiled_rule_validation_specs,
    inventory_targets_to_compiled_fields,
    target_rule_line,
    target_to_compiled_object,
)
from conlanger.tools.compiled_rules_yaml import compiled_rule_entry
from conlanger.tools.inventory_targets import (
    InventoryTarget,
    resolve_inventory_targets,
)

_SECTION = {"index": "1.0", "section": "Test"}
_FAN_OUT = CompilerConfig(sample_alternatives=False, seed=0)


def test_inventory_targets_to_rule_alternatives_and_steps():
    alt_rule = {"stages": ["d", "{∅,ð}"], "env": "V_V", "source": "s:1"}
    alt_targets = resolve_inventory_targets(
        _SECTION, alt_rule, "opt", compiler_config=_FAN_OUT
    )
    fields = inventory_targets_to_compiled_fields(alt_targets)
    assert set(fields) == {"alternatives"}
    assert [item["rule"] for item in fields["alternatives"]] == [
        "d > ∅ / V_V",
        "d > ð / V_V",
    ]

    chain_rule = {"stages": ["p", "t", "k"], "source": "s:2"}
    chain_targets = resolve_inventory_targets(
        _SECTION, chain_rule, "chain", compiler_config=_FAN_OUT
    )
    step_fields = inventory_targets_to_compiled_fields(chain_targets)
    assert step_fields == {
        "steps": [
            {"input": "p", "output": "t", "rule": "p > t"},
            {"input": "t", "output": "k", "rule": "t > k"},
        ],
    }

    simple = resolve_inventory_targets(
        _SECTION, {"stages": ["a", "b"]}, "r0", compiler_config=_FAN_OUT
    )
    assert inventory_targets_to_compiled_fields(simple) == {
        "input": "a",
        "output": "b",
        "rule": "a > b",
    }


def test_sample_alternatives_true_emits_single_optional_branch():
    alt_rule = {"stages": ["d", "{∅,ð}"], "env": "V_V", "source": "s:1"}
    config = CompilerConfig(sample_alternatives=True, seed=0)
    targets = resolve_inventory_targets(
        _SECTION, alt_rule, "opt", compiler_config=config
    )
    fields = inventory_targets_to_compiled_fields(targets)
    assert "alternatives" not in fields
    assert fields["rule"] in {"d > ∅ / V_V", "d > ð / V_V"}


def test_inventory_targets_correlated_chain_branches_as_alternatives():
    """``r → {r,h} → {∅,h}``: three composed paths (including ``r > h > ∅``)."""
    rule = {
        "stages": ["r", "{r,h}", "{∅,h}"],
        "source": "s:1",
    }
    targets = resolve_inventory_targets(
        _SECTION, rule, "Balinese-r", compiler_config=_FAN_OUT
    )
    fields = inventory_targets_to_compiled_fields(targets)
    assert len(fields["alternatives"]) == 3
    assert fields["alternatives"][0]["steps"][0]["rule"] == "r > r"
    specs = compiled_rule_validation_specs(
        {"rule_id": "x", "source": "s", **fields},
    )
    assert specs == [
        ("r > r", 0, 0),
        ("r > ∅", 1, 0),
        ("r > h", 0, 1),
        ("h > h", 1, 1),
        ("r > h", 0, 2),
        ("h > ∅", 1, 2),
    ]


def test_inventory_targets_late_chain_stage_alternatives_use_steps():
    from conlanger.scripts.pipeline_defaults import DEFAULT_YAML
    from conlanger.tools.index_io import read_cleaned_index

    doc = read_cleaned_index(DEFAULT_YAML)
    for sec in doc["sections"]:
        for rule in sec.get("rules") or []:
            if rule.get("rule_id") != "Attic-Greek-oj":
                continue
            section = {"index": sec["index"], "section": sec["section"]}
            targets = resolve_inventory_targets(
                section, rule, "Attic-Greek-oj", compiler_config=_FAN_OUT
            )
            fields = inventory_targets_to_compiled_fields(targets)
            assert len(fields["alternatives"]) == 2
            for branch_idx in (0, 1):
                branch = fields["alternatives"][branch_idx]
                expected = [
                    target_to_compiled_object(t)["rule"]
                    for t in targets
                    if t.alt_idx == branch_idx
                ]
                assert [step["rule"] for step in branch["steps"]] == expected
            return
    pytest.fail("Attic-Greek-oj not found")


def test_compiled_rule_validation_specs_v2_targets_fallback():
    entry = {
        "rule_id": "r0",
        "source": "s:1",
        "targets": [
            {"rule": "a > b", "step_idx": None, "alt_idx": None},
        ],
    }
    assert compiled_rule_validation_specs(entry) == [("a > b", None, None)]


def test_compiled_rule_validation_specs_v4_single_rule_object():
    entry = {
        "rule_id": "r0",
        "input": "a",
        "output": "b",
        "rule": "a > b",
    }
    assert compiled_rule_validation_specs(entry) == [("a > b", None, None)]


def test_target_rule_line_requires_content():
    with pytest.raises(ValueError, match="missing ASCA"):
        target_rule_line(InventoryTarget())


def test_inventory_targets_to_compiled_fields_empty():
    assert inventory_targets_to_compiled_fields([]) == {}
    assert (
        inventory_targets_to_compiled_fields(
            [InventoryTarget(format_error="format_error: x")]
        )
        == {}
    )


def test_compiled_rule_validation_specs_rejects_ambiguous_keys():
    with pytest.raises(ValueError, match="exactly one"):
        compiled_rule_validation_specs(
            {"rule_id": "x", "rule": "a > b", "steps": ["a > b"]},
        )


def test_compiled_rule_validation_specs_rejects_invalid_step_item():
    with pytest.raises(TypeError, match="invalid steps item"):
        compiled_rule_validation_specs(
            {"rule_id": "x", "steps": [123]},
        )


def test_compiled_rule_validation_specs_rejects_invalid_alternative_branch():
    with pytest.raises(TypeError, match="invalid alternatives item"):
        compiled_rule_validation_specs(
            {"rule_id": "x", "alternatives": [123]},
        )


def test_compiled_rule_validation_specs_step_alternatives_block():
    entry = {
        "steps": [
            "a > b",
            {"alternatives": ["c > d", "c > e"]},
        ],
    }
    assert compiled_rule_validation_specs(entry) == [
        ("a > b", 0, None),
        ("c > d", 1, 0),
        ("c > e", 1, 1),
    ]


def test_compiled_rule_validation_specs_v4_step_alternatives_objects():
    entry = {
        "steps": [
            {"input": "a", "output": "b", "rule": "a > b"},
            {
                "alternatives": [
                    {"input": "c", "output": "d", "rule": "c > d"},
                    {"input": "c", "output": "e", "rule": "c > e"},
                ],
            },
        ],
    }
    assert compiled_rule_validation_specs(entry) == [
        ("a > b", 0, None),
        ("c > d", 1, 0),
        ("c > e", 1, 1),
    ]


def test_compiled_rule_validation_specs_branch_alternatives():
    entry = {
        "alternatives": [
            {"steps": ["r > r", "r > ∅"]},
            {"steps": ["r > h", "h > h"]},
        ],
    }
    assert compiled_rule_validation_specs(entry) == [
        ("r > r", 0, 0),
        ("r > ∅", 1, 0),
        ("r > h", 0, 1),
        ("h > h", 1, 1),
    ]


def test_target_to_compiled_object_asca_rule_only():
    obj = target_to_compiled_object(InventoryTarget.model_construct(asca_rule="a > b"))
    assert obj == {"rule": "a > b"}


def test_compiled_rule_validation_specs_rejects_steps_and_alternatives():
    with pytest.raises(ValueError, match="exactly one"):
        compiled_rule_validation_specs(
            {"alternatives": [{"rule": "a > b"}], "steps": [{"rule": "c > d"}]},
        )


def test_compiled_rule_validation_specs_alternative_object_without_steps():
    entry = {"alternatives": [{"input": "a", "output": "b", "rule": "a > b"}]}
    assert compiled_rule_validation_specs(entry) == [("a > b", None, 0)]


def test_compiled_rule_validation_specs_missing_shape():
    with pytest.raises(ValueError, match="exactly one"):
        compiled_rule_validation_specs({"rule_id": "x", "source": "s"})


def test_compiled_rule_entry_emits_rule_not_targets():
    rule = {"stages": ["a", "b"], "source": "s:1"}
    entry = compiled_rule_entry(
        rule,
        rule_id="r0",
        source="s:1",
        targets=resolve_inventory_targets(_SECTION, rule, "r0"),
        section=_SECTION,
    )
    assert entry["rule"] == "a > b"
    assert entry["input"] == "a"
    assert "targets" not in entry
