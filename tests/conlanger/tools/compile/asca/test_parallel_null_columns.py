"""Tests for compile-time parallel-column null stripping (ticket 60)."""

import pytest

from conlanger.tools.asca_compile.parallel_null_columns import (
    drop_mixed_parallel_null_columns,
)
from conlanger.tools.rules import RuleChange, SoundChangeRuleSet


@pytest.mark.parametrize(
    ("side", "expected"),
    [
        ("c ɲ", "c ɲ"),
        ("∅ n", "n"),
        ("∅ ʃ", "ʃ"),
        ("k ʃ", "k ʃ"),
        ("∅", "∅"),
        ("*", "*"),
        ("x", "x"),
        ("k c > ∅ {j,∅}", "k c > {j,∅}"),  # only top-level ∅ dropped when used as I/O
    ],
)
def test_drop_mixed_parallel_null_columns_side(side, expected):
    if " > " in side:
        inp, out = side.split(" > ", 1)
        assert drop_mixed_parallel_null_columns(inp) + " > " + drop_mixed_parallel_null_columns(
            out
        ) == expected
    else:
        assert drop_mixed_parallel_null_columns(side) == expected


def test_drop_mixed_parallel_null_columns_proto_star_token_unchanged():
    assert drop_mixed_parallel_null_columns("*T") == "*T"
    assert drop_mixed_parallel_null_columns("*L") == "*L"


def test_rule_change_compiles_parallel_column_output_null():
    part = RuleChange({"input": "c ɲ", "output": "∅ n"}, "asca")
    assert part.value == "c ɲ > n"


def test_rule_change_compiles_parallel_column_input_null():
    part = RuleChange({"input": "∅ ʃ", "output": "k ʃ", "env": "V_$#"}, "asca")
    assert part.value == "ʃ > k ʃ / V_$#"


def test_rule_change_compiles_parallel_column_with_env():
    part = RuleChange({"input": "k ʃ", "output": "∅ ʃ", "env": "V_V"}, "asca")
    assert part.value == "k ʃ > ʃ / V_V"


def test_rule_change_pure_deletion_unchanged():
    part = RuleChange({"input": "ɡ", "output": "∅", "env": "V_(VC…)V"}, "asca")
    assert part.value == "ɡ > ∅ / V_(VC,0)V"


def test_rule_change_pure_insertion_unchanged():
    part = RuleChange({"input": "∅", "output": "x"}, "asca")
    assert part.value == "∅ > x"


def test_sound_change_ruleset_parallel_column_from_stages():
    section = {
        "index": "10.3.9.2",
        "section": "Proto-Utupua to Nebao",
        "rules": [{"stages": ["c ɲ", "∅ n"]}],
    }
    ruleset = SoundChangeRuleSet(section, "asca")
    rule_parts = [part for part in ruleset._parts if isinstance(part, RuleChange)]
    assert len(rule_parts) == 1
    assert rule_parts[0].value == "c ɲ > n"
