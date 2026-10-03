import pytest
from helpers import default_index_parser
from lxml import html

from conlanger.tools.ingest.section_policy import (
    is_catch_all_else_env,
    is_else_env_candidate,
    resolve_catch_all_else_rules,
)


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
        {"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"},
        {"stages": ["c", "d"], "env": "(else)", "raw": "c → d / (else)"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert "env" not in resolved[1]
    assert resolved[1]["comment"] == "(else)"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_complementary_pair():
    rules = [
        {"stages": ["kʼ", "{χʷ,qʷ}"], "env": "#_", "raw": "kʼ → {χʷ,qʷ} / #_"},
        {"stages": ["kʼ", "q"], "env": "else", "raw": "kʼ → q / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[0]["env"] == "#_"
    assert "exception" not in resolved[0]
    assert "env" not in resolved[1]
    assert resolved[1]["exception"] == "#_"
    assert resolved[1]["raw"] == "kʼ → q / else"


def test_resolve_catch_all_else_gloss_then_resolve():
    rules = [
        {"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"},
        {
            "stages": ["β", "f"],
            "env": "else (rarely)",
            "raw": "β → f / else (rarely)",
        },
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert "env" not in resolved[1]
    assert resolved[1]["exception"] == "#_"
    assert resolved[1]["comment"] == "(rarely)"


def test_resolve_catch_all_else_cascade_uses_immediate_prev_only():
    rules = [
        {"stages": ["a", "x"], "env": "_A", "raw": "a → x / _A"},
        {"stages": ["b", "y"], "env": "_B", "raw": "b → y / _B"},
        {"stages": ["c", "z"], "env": "else", "raw": "c → z / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[2]["exception"] == "_B"
    assert "env" not in resolved[2]


def test_resolve_catch_all_else_deferred_prev_env_and_exception():
    rules = [
        {
            "stages": ["p", "∅"],
            "env": "C_",
            "exception": "s_",
            "raw": "p → ∅ / C_ ! s_",
        },
        {"stages": ["p", "kʷ"], "env": "else", "raw": "p → kʷ / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "else"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_deferred_prev_neither():
    rules = [
        {"stages": ["a", "ɑː"], "raw": "a → ɑː"},
        {"stages": ["a", "æ"], "env": "else", "raw": "a → æ / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "else"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_deferred_else_after_else():
    rules = [
        {
            "stages": ["aɪ", "ɑeː"],
            "env": "else",
            "comment": "only for some speakers",
            "raw": "aɪ → ɑeː / else (only for some speakers)",
        },
        {
            "stages": ["aɪ", "aː"],
            "env": "else",
            "comment": "only for some speakers",
            "raw": "aɪ → aː / else (only for some speakers)",
        },
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "else"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_leaves_non_catch_all_fragments():
    rules = [
        {"stages": ["a", "b"], "env": "#_", "raw": "a → b / #_"},
        {"stages": ["c", "d"], "env": "_# else", "raw": "c → d / _# else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "_# else"
    assert "exception" not in resolved[1]


def test_resolve_catch_all_else_deferred_when_prev_env_is_prose():
    rules = [
        {
            "stages": ["dʒ", "{d,ɡ}"],
            "env": "if s or z occur somewhere else in the word",
            "raw": "dʒ → {d,ɡ} / if s or z occur somewhere else in the word",
        },
        {"stages": ["dʒ", "ʒ"], "env": "else", "raw": "dʒ → ʒ / else"},
    ]
    resolved = resolve_catch_all_else_rules(rules)
    assert resolved[1]["env"] == "else"
    assert "exception" not in resolved[1]


def test_parser_resolves_catch_all_else_in_section():
    root = html.document_fromstring(
        """\
<!doctype html><html><body><section id="Else">
<h2>1.0 Test Section</h2>
<p class="schg">kʼ → {χʷ,qʷ} / #_</p>
<p class="schg">kʼ → q / else</p>
</section></body></html>"""
    )
    rules = default_index_parser().parse(root)["sections"][0]["rules"]
    assert rules[0]["env"] == "#_"
    assert "env" not in rules[1]
    assert rules[1]["exception"] == "#_"
    assert rules[1]["raw"] == "kʼ → q / else"
