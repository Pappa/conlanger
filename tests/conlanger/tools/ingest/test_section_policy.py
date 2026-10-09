import pytest

from conlanger.ingest.models.index_models import IndexRule
from conlanger.ingest.utils.section_policy import (
    is_catch_all_else_env,
    is_else_env_candidate,
    resolve_catch_all_else_rules,
)


def _rule(data: dict) -> IndexRule:
    return IndexRule.model_validate(
        {"source": "t", "raw": data.get("raw", "rule"), **data}
    )


def _rule_dump(rule: IndexRule) -> dict:
    return rule.model_dump(exclude_none=True, mode="python")


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ("else", True),
        ("else?", True),
        ("  else  ", True),
        ("else (rarely)", False),
        ("_# else", False),
        ("if ɑ is elsewhere in the word", False),
    ],
)
def test_is_catch_all_else_env(env, expected):
    assert is_catch_all_else_env(env) == expected


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ("else", True),
        ("else?", True),
        ("  else  ", True),
        ("else (rarely)", True),
        ("_# else", True),
        ("if ɑ is elsewhere in the word", False),
    ],
)
def test_is_else_env_candidate(env, expected):
    assert is_else_env_candidate(env) == expected


def test_resolve_catch_all_else_empty_rules():
    assert resolve_catch_all_else_rules([]) == []


def test_resolve_catch_all_else_paren_gloss_only_env():
    rules = [
        _rule({"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"}),
        _rule({"stages": ["c", "d"], "env": "(else)", "raw": "c → d / (else)"}),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    dumped = _rule_dump(resolved[1])
    assert "env" not in dumped
    assert dumped["comment"] == "(else)"
    assert "exception" not in dumped


def test_resolve_catch_all_else_complementary_pair():
    rules = [
        _rule(
            {
                "stages": ["kʼ", "{χʷ,qʷ}"],
                "env": "#_",
                "raw": "kʼ → {χʷ,qʷ} / #_",
            }
        ),
        _rule({"stages": ["kʼ", "q"], "env": "else", "raw": "kʼ → q / else"}),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert _rule_dump(resolved[0])["env"] == "#_"
    assert resolved[0].exception is None
    dumped_else = _rule_dump(resolved[1])
    assert "env" not in dumped_else
    assert dumped_else["exception"] == "#_"
    assert resolved[1].raw == "kʼ → q / else"


def test_resolve_catch_all_else_gloss_then_resolve():
    rules = [
        _rule({"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"}),
        _rule(
            {
                "stages": ["β", "f"],
                "env": "else (rarely)",
                "raw": "β → f / else (rarely)",
            }
        ),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    dumped = _rule_dump(resolved[1])
    assert "env" not in dumped
    assert dumped["exception"] == "#_"
    assert dumped["comment"] == "(rarely)"


def test_resolve_catch_all_else_cascade_uses_immediate_prev_only():
    rules = [
        _rule({"stages": ["a", "x"], "env": "_A", "raw": "a → x / _A"}),
        _rule({"stages": ["b", "y"], "env": "_B", "raw": "b → y / _B"}),
        _rule({"stages": ["c", "z"], "env": "else", "raw": "c → z / else"}),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    dumped = _rule_dump(resolved[2])
    assert dumped["exception"] == "_B"
    assert "env" not in dumped


def test_resolve_catch_all_else_deferred_prev_env_and_exception():
    rules = [
        _rule(
            {
                "stages": ["p", "∅"],
                "env": "C_",
                "exception": "s_",
                "raw": "p → ∅ / C_ ! s_",
            }
        ),
        _rule({"stages": ["p", "kʷ"], "env": "else", "raw": "p → kʷ / else"}),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    dumped = _rule_dump(resolved[1])
    assert dumped["env"] == "else"
    assert "exception" not in dumped


def test_resolve_catch_all_else_deferred_prev_neither():
    rules = [
        _rule({"stages": ["a", "ɑː"], "raw": "a → ɑː"}),
        _rule({"stages": ["a", "æ"], "env": "else", "raw": "a → æ / else"}),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    dumped = _rule_dump(resolved[1])
    assert dumped["env"] == "else"
    assert "exception" not in dumped


def test_resolve_catch_all_else_deferred_else_after_else():
    rules = [
        _rule(
            {
                "stages": ["aɪ", "ɑeː"],
                "env": "else",
                "comment": "only for some speakers",
                "raw": "aɪ → ɑeː / else (only for some speakers)",
            }
        ),
        _rule(
            {
                "stages": ["aɪ", "aː"],
                "env": "else",
                "comment": "only for some speakers",
                "raw": "aɪ → aː / else (only for some speakers)",
            }
        ),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    dumped = _rule_dump(resolved[1])
    assert dumped["env"] == "else"
    assert "exception" not in dumped


def test_resolve_catch_all_else_leaves_non_catch_all_fragments():
    rules = [
        _rule({"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"}),
        _rule({"stages": ["c", "d"], "env": "_# else", "raw": "c → d / _# else"}),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    dumped = _rule_dump(resolved[1])
    assert dumped["env"] == "_# else"
    assert "exception" not in dumped


def test_resolve_catch_all_else_deferred_when_prev_env_is_prose():
    rules = [
        _rule(
            {
                "stages": ["dʒ", "{d,ɡ}"],
                "env": "if s or z occur somewhere else in the word",
                "raw": "dʒ → {d,ɡ} / if s or z occur somewhere else in the word",
            }
        ),
        _rule({"stages": ["dʒ", "ʒ"], "env": "else", "raw": "dʒ → ʒ / else"}),
    ]
    resolved = resolve_catch_all_else_rules(rules)
    dumped = _rule_dump(resolved[1])
    assert dumped["env"] == "else"
    assert "exception" not in dumped
