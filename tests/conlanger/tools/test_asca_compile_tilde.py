"""Tests for Index tilde notation compile expansion (ticket 47)."""

import pytest

from conlanger.tools.asca_compile.tilde import (
    expand_index_tilde_notation,
    normalize_corpus_rule_tilde_fields,
)
from conlanger.tools.asca_validator import validate_asca
from conlanger.tools.rules import RuleChange, SoundChangeRuleSet


@pytest.mark.parametrize(
    ("index_rule", "expected"),
    [
        ("bj~vj~v", "{bj,vj,v}"),
        ("t~ɾ~n", "{t,ɾ,n}"),
        ("ɾ~l~∅", "{ɾ,l,∅}"),
        ("dzʲ~zʲ tʃ:[+cg] dʒ~ʒ", "{dzʲ,zʲ} tʃ:[+cg] {dʒ,ʒ}"),
        ("ɣ~ɡ", "{ɣ,ɡ}"),
        ("d~ð", "{d,ð}"),
        ("q:[+long]~qχ", "{q:[+long],qχ}"),
        ("{ts~tsʰ,ts,s}", "{ts,tsʰ,ts,s}"),
        ("{~ɛ,ẽ}", "{ɛ,ẽ}"),
        ("ʃ(~ʃ:[+long]) ʒ", "{ʃ,ʃ:[+long]} ʒ"),
        ("ɬʲ(~ɬʲʷ:[+long]) ɮʲ", "{ɬʲ,ɬʲʷ:[+long]} ɮʲ"),
        ("{ɛ,e} {~ɛ,ẽ}", "{ɛ,e} {ɛ,ẽ}"),
        ("!ɡ ~ !̃", "{!ɡ,!̃}"),
    ],
)
def test_expand_index_tilde_notation(index_rule, expected):
    assert expand_index_tilde_notation(index_rule) == expected


def test_expand_index_tilde_notation_leaves_bracket_matrices_untouched():
    assert expand_index_tilde_notation("C > V / [+high]") == "C > V / [+high]"


def test_is_multigraph_output_chain():
    from conlanger.tools.asca_compile.tilde import _is_multigraph_output_chain

    assert _is_multigraph_output_chain(["bj", "vj", "v"])
    assert not _is_multigraph_output_chain(["d", "n", "l"])
    assert not _is_multigraph_output_chain(["k", "x", "ɡ", "ɣ"])


def test_normalize_corpus_rule_tilde_fields_expands_alternation_not_chain():
    rule = {"input": "d", "output": "d~n~l", "env": "#_a"}
    assert normalize_corpus_rule_tilde_fields(rule)["output"] == "{d,n,l}"


def test_normalize_corpus_rule_tilde_fields_expands_output_chain():
    rule = {"input": "{β,w}", "output": "bj~vj~v"}
    assert normalize_corpus_rule_tilde_fields(rule) == {
        "input": "{β,w}",
        "output": "bj > vj > v",
    }


def test_sound_change_ruleset_expands_tilde_output_chain():
    section = {
        "index": "1.0",
        "section": "Tilde chain",
        "rules": [{"input": "{β,w}", "output": "bj~vj~v"}],
    }
    ruleset = SoundChangeRuleSet(section, "asca")
    rule_parts = [part for part in ruleset._parts if isinstance(part, RuleChange)]
    assert len(rule_parts) == 3
    assert rule_parts[0].value == "{β,w} > bj"
    assert rule_parts[1].value == "bj > vj"
    assert rule_parts[2].value == "vj > v"


@pytest.mark.parametrize(
    ("inp", "out", "env"),
    [
        ("{β,w}", "bj~vj~v", None),
        ("ɣ", "ɣ~ɡ", None),
        ("{d,ð}", "d", "V_u"),
        ("ts", "{ts~tsʰ,ts,s}", None),
        ("ʃ(~ʃ:[+long]) ʒ", "sʲ sʲ", None),
        ("{ɛ,e}", "{~ɛ,ẽ}", None),
        (
            "zʷʲ tsʷʲ:[+cg] dzʷʲ",
            "dzʲ~zʲ tʃ:[+cg] dʒ~ʒ",
            None,
        ),
        ("h", "j~ʔ", "_ V:[+front]"),
    ],
)
def test_tilde_inventory_representatives_validate(inp, out, env):
    rule = {"input": inp, "output": out}
    if env is not None:
        rule["env"] = env
    section = {"index": "1", "section": "tilde", "rules": [rule]}
    validate_asca(SoundChangeRuleSet(section, "asca"))


def test_tilde_inventory_representative_paren_input_validates_after_expansion():
    section = {
        "index": "1",
        "section": "paren",
        "rules": [{"input": "ʔ(ʷ)~q:[+cg](ʷ)", "output": "ʔ(ʷ)"}],
    }
    validate_asca(SoundChangeRuleSet(section, "asca"))
