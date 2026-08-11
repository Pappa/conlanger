"""Tests for compile-time chain expansion (ADR-0005 ticket 03)."""

from conlanger.tools.compile.asca.chains import expand_chained_corpus_rule
from conlanger.tools.rules import RuleChange, SoundChangeRuleSet


def test_expand_chained_corpus_rule_splits_stages_chain():
    assert expand_chained_corpus_rule({"stages": ["dʒ", "tʃ", "ʃ"]}) == [
        {"input": "dʒ", "output": "tʃ"},
        {"input": "tʃ", "output": "ʃ"},
    ]


def test_expand_chained_corpus_rule_keeps_single_step():
    rule = {"stages": ["a", "e"], "env": "_#"}
    assert expand_chained_corpus_rule(rule) == [
        {"input": "a", "output": "e", "env": "_#"}
    ]


def test_expand_chained_corpus_rule_empty_stages_emits_nothing():
    assert expand_chained_corpus_rule({"stages": []}) == []


def test_expand_chained_corpus_rule_single_stage_emits_nothing():
    assert expand_chained_corpus_rule({"stages": ["a"]}) == []


def test_expand_chained_corpus_rule_propagates_env_to_each_step():
    rule = {"stages": ["{θ,l}", "r", "l"], "env": "V_V"}
    assert expand_chained_corpus_rule(rule) == [
        {"input": "{θ,l}", "output": "r", "env": "V_V"},
        {"input": "r", "output": "l", "env": "V_V"},
    ]


def test_expand_chained_corpus_rule_propagates_exception_and_comment():
    rule = {
        "stages": ["a", "b", "c"],
        "env": "_V",
        "exception": "C_",
        "comment": "note",
    }
    steps = expand_chained_corpus_rule(rule)
    assert steps == [
        {
            "input": "a",
            "output": "b",
            "env": "_V",
            "exception": "C_",
            "comment": "note",
        },
        {
            "input": "b",
            "output": "c",
            "env": "_V",
            "exception": "C_",
            "comment": "note",
        },
    ]


def test_expand_chained_corpus_rule_propagates_skip_meta():
    rule = {"stages": ["a", "b"], "skip": True}
    assert expand_chained_corpus_rule(rule) == [
        {"input": "a", "output": "b", "skip": True},
    ]


def test_expand_chained_corpus_rule_propagates_sporadic_to_each_step():
    rule = {"stages": ["a", "b", "c"], "sporadic": True, "comment": "note"}
    assert expand_chained_corpus_rule(rule) == [
        {"input": "a", "output": "b", "sporadic": True, "comment": "note"},
        {"input": "b", "output": "c", "sporadic": True, "comment": "note"},
    ]


def test_sound_change_ruleset_expands_chained_corpus_rule():
    section = {
        "index": "1.0",
        "section": "Chain",
        "rules": [{"stages": ["dʒ", "tʃ", "ʃ"]}],
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
        "rules": [{"stages": ["{θ,l}", "r", "l"], "env": "V_V"}],
    }
    ruleset = SoundChangeRuleSet(section, "asca")
    rule_parts = [part for part in ruleset._parts if isinstance(part, RuleChange)]
    assert len(rule_parts) == 2
    assert rule_parts[0].value == "{θ,l} > r / V_V"
    assert rule_parts[1].value == "r > l / V_V"
