"""Tests for ``inventory_targets``."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from conlanger.tools.inventory_targets import (
    InventoryTarget,
    _series_for_sound_change_rule,
    resolve_inventory_targets,
)

_SECTION = {"index": "1.0", "section": "Test"}


def test_resolve_inventory_targets_single_target():
    rule = {"stages": ["a", "b"], "source": "s:1"}
    targets = resolve_inventory_targets(_SECTION, rule, "r0")
    assert len(targets) == 1
    assert targets[0].field_rule is not None
    assert str(targets[0].field_rule).strip() == "a > b"
    assert targets[0].alt_idx is None
    assert targets[0].step_idx is None


def test_resolve_inventory_targets_alternatives_and_steps():
    alt_rule = {"stages": ["d", "{∅,ð}"], "env": "V_V", "source": "s:1"}
    alt_targets = resolve_inventory_targets(_SECTION, alt_rule, "opt")
    assert len(alt_targets) == 2
    assert alt_targets[0].alt_idx == 0
    assert alt_targets[1].alt_idx == 1

    chain_rule = {"stages": ["p", "t", "k"], "source": "s:2"}
    chain_targets = resolve_inventory_targets(_SECTION, chain_rule, "chain")
    assert len(chain_targets) == 2
    assert chain_targets[0].step_idx == 0
    assert chain_targets[1].step_idx == 1


def test_resolve_inventory_targets_format_error():
    targets = resolve_inventory_targets(_SECTION, {"stages": []}, "bad")
    assert len(targets) == 1
    assert targets[0].format_error is not None


def test_resolve_inventory_targets_no_composed_chain_paths():
    from conlanger.compile.models.config import CompilerConfig
    from conlanger.compile.models.rules import SoundChangeRule
    from conlanger.tools.inventory_targets import _enumerate_composed_chain_paths

    config = CompilerConfig()
    first = SoundChangeRule(
        input="a",
        output="b",
        detect_alternatives=False,
        compiler_config=config,
    )
    second = SoundChangeRule(
        input="c",
        output="d",
        detect_alternatives=False,
        compiler_config=config,
    )
    assert _enumerate_composed_chain_paths([first, second]) == []


def test_inventory_target_is_frozen_pydantic_model():
    target = InventoryTarget()
    with pytest.raises(ValidationError):
        target.alt_idx = 1  # type: ignore[misc]


def test_resolve_inventory_targets_composes_balinese_r_paths():
    rule = {
        "stages": ["r", "{r,h}", "{∅,h}"],
        "source": "s:1",
    }
    targets = resolve_inventory_targets(_SECTION, rule, "Balinese-r")
    assert len(targets) == 6
    paths: dict[int, list[str]] = {}
    for alt_idx in {t.alt_idx for t in targets}:
        paths[alt_idx] = [
            str(t.field_rule).strip()
            for t in sorted(
                [t for t in targets if t.alt_idx == alt_idx],
                key=lambda t: t.step_idx or 0,
            )
        ]
    assert paths[0] == ["r > r", "r > ∅"]
    assert paths[1] == ["r > h", "h > h"]
    assert paths[2] == ["r > h", "h > ∅"]


def test_series_for_sound_change_rule_builds_mini_series():
    from conlanger.compile.models.config import CompilerConfig
    from conlanger.compile.models.rules import SoundChangeRule

    rule = SoundChangeRule(
        input="a",
        output="b",
        detect_alternatives=False,
        compiler_config=CompilerConfig(),
    )
    series = _series_for_sound_change_rule(_SECTION, "r0", rule)
    assert str(series).strip().endswith("a > b")
