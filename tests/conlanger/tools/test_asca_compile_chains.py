"""Tests for compile-time chain expansion (ADR-0005 ticket 03)."""

from conlanger.tools.asca_compile.chains import expand_chained_corpus_rule
from conlanger.tools.rules import RuleChange, SoundChangeRuleSet


def test_expand_chained_corpus_rule_splits_output_chain():
    assert expand_chained_corpus_rule({"input": "dʒ", "output": "tʃ > ʃ"}) == [
        {"input": "dʒ", "output": "tʃ"},
        {"input": "tʃ", "output": "ʃ"},
    ]


def test_expand_chained_corpus_rule_keeps_single_step():
    rule = {"input": "a", "output": "e", "env": "_#"}
    assert expand_chained_corpus_rule(rule) == [rule]


def test_expand_chained_corpus_rule_propagates_env_to_each_step():
    rule = {"input": "{θ,l}", "output": "r > l", "env": "V_V"}
    assert expand_chained_corpus_rule(rule) == [
        {"input": "{θ,l}", "output": "r", "env": "V_V"},
        {"input": "r", "output": "l", "env": "V_V"},
    ]


def test_sound_change_ruleset_expands_chained_corpus_rule():
    section = {
        "index": "1.0",
        "section": "Chain",
        "rules": [{"input": "dʒ", "output": "tʃ > ʃ"}],
    }
    ruleset = SoundChangeRuleSet(section, "asca")
    rule_parts = [part for part in ruleset._parts if isinstance(part, RuleChange)]
    assert len(rule_parts) == 2
    assert rule_parts[0].value == "dʒ > tʃ"
    assert rule_parts[1].value == "tʃ > ʃ"


def test_sound_change_ruleset_expands_chain_with_env():
    section = {
        "index": "1.0",
        "section": "Chain env",
        "rules": [{"input": "{θ,l}", "output": "r > l", "env": "V_V"}],
    }
    ruleset = SoundChangeRuleSet(section, "asca")
    rule_parts = [part for part in ruleset._parts if isinstance(part, RuleChange)]
    assert len(rule_parts) == 2
    assert rule_parts[0].value == "{θ,l} > r / V_V"
    assert rule_parts[1].value == "r > l / V_V"
