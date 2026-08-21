"""Optional-output alternatives + instance RNG on ``SoundChangeRule`` (ticket 66)."""

from __future__ import annotations

import random
import shutil

import pytest

from conlanger.tools.rules import DiachronicSeries, SoundChangeRule


def _rule(**overrides):
    base = {"input": "d", "output": "{∅,ð}", "env": "V_V"}
    base.update(overrides)
    return base


@pytest.mark.parametrize(
    ("input_text", "output_text", "expected_members"),
    [
        ("d", "{∅,ð}", ["∅", "ð"]),
        ("t", "{s,ʃ,tʃ}", ["s", "ʃ", "tʃ"]),
    ],
)
def test_optional_output_builds_alternatives(input_text, output_text, expected_members):
    rule = SoundChangeRule(input=input_text, output=output_text)
    assert [alt.output for alt in rule.alternatives] == expected_members
    assert [alt.input for alt in rule.alternatives] == [input_text] * len(
        expected_members
    )


@pytest.mark.parametrize(
    ("input_text", "output_text"),
    [
        ("{a,b}", "{c,d}"),  # paired sets are not optional outputs
        ("d", "ð"),  # no set at all
        ("d", "a{b,c}"),  # output set is not whole-field
        ("d", "{a,{b,c}}"),  # nested set is out of scope (ticket 67)
        ("d", "{}"),  # empty set has no members
    ],
)
def test_non_optional_output_has_no_alternatives(input_text, output_text):
    rule = SoundChangeRule(input=input_text, output=output_text)
    assert rule.alternatives == []


def test_alternatives_are_leaf_peers():
    rule = SoundChangeRule(**_rule())
    for alt in rule.alternatives:
        assert isinstance(alt, SoundChangeRule)
        assert alt.alternatives == []
        assert alt.env == "V_V"
        assert " > " in alt.value


def test_parent_pick_is_frozen_choice():
    rule = SoundChangeRule(**_rule(), seed=1234)
    chosen_values = {alt.value for alt in rule.alternatives}
    assert rule.value in chosen_values
    # ``str`` renders the frozen choice with no re-sample.
    first_render = str(rule)
    assert first_render == str(rule)
    assert first_render == f"\t{rule.value}"


def test_seed_selects_alternative_uniformly_via_instance_rng():
    rule = SoundChangeRule(**_rule(), seed=7)
    expected_idx = random.Random(7).randrange(len(rule.alternatives))
    assert rule.value == rule.alternatives[expected_idx].value


def test_caller_supplied_rng_is_used_for_pick():
    rule = SoundChangeRule(**_rule(), rng=random.Random(99))
    expected_idx = random.Random(99).randrange(len(rule.alternatives))
    assert rule.value == rule.alternatives[expected_idx].value


def test_same_seed_is_deterministic():
    first = SoundChangeRule(**_rule(), seed=2024)
    second = SoundChangeRule(**_rule(), seed=2024)
    assert first.value == second.value


def test_parent_pick_does_not_touch_global_random_state():
    random.seed(0)
    before = random.getstate()
    SoundChangeRule(**_rule(), seed=None)
    SoundChangeRule(**_rule(), seed=42)
    assert random.getstate() == before


def test_non_optional_rule_keeps_single_value():
    rule = SoundChangeRule(input="p", output="b", env="V_V")
    assert rule.alternatives == []
    assert rule.value == "p > b / V_V"


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_each_alternative_validates_independently():
    from pathlib import Path

    from conlanger.appliers.asca import validate_asca

    probe = Path("tests/fixtures/asca_probe_words.wsca")
    rule = SoundChangeRule(**_rule())
    for alt in rule.alternatives:
        section = {
            "index": "1.0",
            "section": "Optional",
            "rules": [{"stages": [alt.input, alt.output], "env": alt.env}],
        }
        validate_asca(DiachronicSeries(section), probe_words=probe)
