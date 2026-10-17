"""Tests for ``compiled_rule_shape`` (asca_rules.yml v3 per-rule layout)."""

from __future__ import annotations

import pytest

from conlanger.tools.compiled_rule_shape import (
    compiled_rule_validation_specs,
    inventory_targets_to_compiled_fields,
    target_rule_line,
)
from conlanger.tools.compiled_rules_yaml import compiled_rule_entry
from conlanger.tools.inventory_targets import (
    InventoryTarget,
    resolve_inventory_targets,
)

_SECTION = {"index": "1.0", "section": "Test"}


def test_inventory_targets_to_rule_alternatives_and_steps():
    alt_rule = {"stages": ["d", "{∅,ð}"], "env": "V_V", "source": "s:1"}
    alt_targets = resolve_inventory_targets(_SECTION, alt_rule, "opt")
    assert inventory_targets_to_compiled_fields(alt_targets) == {
        "alternatives": ["d > ∅ / V_V", "d > ð / V_V"],
    }

    chain_rule = {"stages": ["p", "t", "k"], "source": "s:2"}
    chain_targets = resolve_inventory_targets(_SECTION, chain_rule, "chain")
    assert inventory_targets_to_compiled_fields(chain_targets) == {
        "steps": ["p > t", "t > k"],
    }

    simple = resolve_inventory_targets(_SECTION, {"stages": ["a", "b"]}, "r0")
    assert inventory_targets_to_compiled_fields(simple) == {"rule": "a > b"}


def test_inventory_targets_correlated_chain_branches_as_alternatives():
    """``r → {r,h} → {∅,h}``: three composed paths (including ``r > h > ∅``)."""
    rule = {
        "stages": ["r", "{r,h}", "{∅,h}"],
        "source": "s:1",
    }
    targets = resolve_inventory_targets(_SECTION, rule, "Balinese-r")
    fields = inventory_targets_to_compiled_fields(targets)
    assert fields == {
        "alternatives": [
            {"steps": ["r > r", "r > ∅"]},
            {"steps": ["r > h", "h > h"]},
            {"steps": ["r > h", "h > ∅"]},
        ],
    }
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
            targets = resolve_inventory_targets(section, rule, "Attic-Greek-oj")
            fields = inventory_targets_to_compiled_fields(targets)
            assert fields["alternatives"] == [
                {
                    "steps": [
                        str(t.field_rule).strip() for t in targets if t.alt_idx == 0
                    ],
                },
                {
                    "steps": [
                        str(t.field_rule).strip() for t in targets if t.alt_idx == 1
                    ],
                },
            ]
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
    assert "targets" not in entry
