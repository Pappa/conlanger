import pytest

from conlanger.ingest.models.index_models import IndexRule
from conlanger.tools.ingest.flatten_nested_sets import (
    _consume_segment_tail,
    _try_distribute,
    flatten_nested_sets,
    flatten_nested_sets_in_rule_fields,
    flatten_nested_sets_in_section_rules,
)


def _rule(data: dict) -> IndexRule:
    return IndexRule.model_validate(
        {"source": "t", "raw": data.get("raw", "rule"), **data}
    )


@pytest.mark.parametrize(
    "input,expected",
    [
        pytest.param("{a,{b,c}}", "{a,b,c}", id="unions_inner_member"),
        pytest.param(
            "{{h,k,ŋ}n,w,v,l,r}_",
            "{hn,kn,ŋn,w,v,l,r}_",
            id="distributes_suffix_over_inner_set",
        ),
        pytest.param(
            "_{s,({m,j,w})V}",
            "_{s,mV,jV,wV}",
            id="expands_parenthetical_1",
        ),
        pytest.param(
            "_ə{(C){p,kʷ},m,w}",
            "_ə{(C)p,(C)kʷ,m,w}",
            id="expands_parenthetical_2",
        ),
        pytest.param(
            "{x,({a,b})V}",
            "{x,aV,bV}",
            id="expands_parenthetical_3",
        ),
        pytest.param(
            "{x,({a,b})[+voice]}",
            "{x,a[+voice],b[+voice]}",
            id="expands_parenthetical_4",
        ),
        pytest.param(
            "e o u æ ø y → {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i}",
            "e o u æ ø y → {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i}",
            id="leaves_unbalanced_1",
        ),
        pytest.param(
            "}{a,b}",
            "}{a,b}",
            id="leaves_unbalanced_2",
        ),
        pytest.param(
            "(h)ə{p,b}",
            "(h)ə{p,b}",
            id="leaves_parallel_columns",
        ),
        pytest.param(
            "V[+nas]({ʔ,s})w_",
            "V[+nas]({ʔ,s})w_",
            id="leaves_paren_wrapped_flat_set_1",
        ),
        pytest.param(
            "({p,t,k})n",
            "({p,t,k})n",
            id="leaves_paren_wrapped_flat_set_2",
        ),
        pytest.param(
            "{{C[-fr,+bk,-hi,-lo],K}ʷ,w}_",
            "{C[-fr,+bk,-hi,-lo]ʷ,Kʷ,w}_",
            id="flattens_with_diacritic_marks_applied_to_sets",
        ),
        pytest.param(
            "#_, _#",
            "#_, _#",
            id="leaves_flat_env_sets",
        ),
        pytest.param(
            "{a, b, c}",
            "{a, b, c}",
            id="leaves_flat_sets",
        ),
        pytest.param(
            "{({a,b})}",
            "{a,b}",
            id="flattens_paren_only_set_member",
        ),
    ],
)
def test_flatten_nested_sets(input, expected):
    assert flatten_nested_sets(input) == expected


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        ("({a,b})V", ["aV", "bV"]),
        ("{a,b}", None),
        ("x{}y", None),
    ],
)
def test_try_distribute_paren_wrapped_and_guard_paths(member, expected):
    assert _try_distribute(member) == expected


@pytest.mark.parametrize(
    ("text", "start", "expected_end"),
    [
        ("a[+voice", 1, 1),
        ("a(C)", 1, 1),
    ],
)
def test_consume_segment_tail_stops_on_unclosed_or_nested_groupers(
    text, start, expected_end
):
    assert _consume_segment_tail(text, start) == expected_end


@pytest.mark.parametrize(
    ("rule_in", "expected"),
    [
        pytest.param(
            {
                "raw": "Cʷ → C / _ə{(C){p,kʷ},m,w}",
                "stages": ["Cʷ", "C"],
                "env": "_ə{(C){p,kʷ},m,w}",
            },
            {
                "raw": "Cʷ → C / _ə{(C){p,kʷ},m,w}",
                "env": "_ə{(C)p,(C)kʷ,m,w}",
            },
            id="munsee_env",
        ),
        pytest.param(
            {
                "raw": "e → ja / ! {{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}",
                "stages": ["e", "ja"],
                "exception": "{{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}",
            },
            {
                "raw": "e → ja / ! {{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}",
                "exception": "{hn,kn,ŋn,w,v,l,r}_, _{u,o,i}",
            },
            id="old_norse_exception",
        ),
        pytest.param(
            {
                "raw": "s → ʃ / #_{xʲ,w{i,a},qʷa}",
                "stages": ["s", "ʃ"],
                "env": "#_{xʲ,w{i,a},qʷa}",
            },
            {
                "raw": "s → ʃ / #_{xʲ,w{i,a},qʷa}",
                "env": "#_{xʲ,wi,wa,qʷa}",
            },
            id="nooksack_env",
        ),
        pytest.param(
            {
                "raw": "{{h₁,h₃}s,s{h₁,h₃}} → sː",
                "stages": ["{{h₁,h₃}s,s{h₁,h₃}}", "sː"],
            },
            {
                "raw": "{{h₁,h₃}s,s{h₁,h₃}} → sː",
                "stages": ["{h₁s,h₃s,sh₁,sh₃}", "sː"],
            },
            id="common_anatolian_stages",
        ),
        pytest.param(
            {
                "raw": "a(i) {e,w{æ,i}} {we,ei} (w)ɪ → ey ø y ʏ / w_ ! hw_",
                "stages": [
                    "a(i) {e,w{æ,i}} {we,ei} (w)ɪ",
                    "ey ø y ʏ",
                ],
                "env": "w_",
                "exception": "hw_",
            },
            {
                "raw": "a(i) {e,w{æ,i}} {we,ei} (w)ɪ → ey ø y ʏ / w_ ! hw_",
                "stages": [
                    "a(i) {e,wæ,wi} {we,ei} (w)ɪ",
                    "ey ø y ʏ",
                ],
            },
            id="old_norse_stages",
        ),
        pytest.param(
            {
                "raw": "{{s,z}(ˤ),ʒ}ʃ → ʃː",
                "stages": ["{{s,z}(ˤ),ʒ}ʃ", "ʃː"],
            },
            {
                "raw": "{{s,z}(ˤ),ʒ}ʃ → ʃː",
                "stages": ["{s(ˤ),z(ˤ),ʒ}ʃ", "ʃː"],
            },
            id="egyptian_arabic_stages",
        ),
        pytest.param(
            {"stages": ["{x₁,x₂}", "ɡ"]},
            {"stages": ["{x₁,x₂}", "ɡ"]},
            id="leaves_compile_created_nesting",
        ),
    ],
)
def test_flatten_nested_sets_in_rule_fields(rule_in, expected):
    rule = flatten_nested_sets_in_rule_fields(_rule(rule_in))
    dumped = rule.model_dump(exclude_none=True, mode="python")
    for key, value in expected.items():
        assert dumped[key] == value


@pytest.mark.parametrize(
    ("rules_in", "expected"),
    [
        pytest.param(
            [
                {
                    "raw": "m̩ n̩ → am an / _{s,({m,j,w})V}",
                    "stages": ["m̩ n̩", "am an"],
                    "env": "_{s,({m,j,w})V}",
                },
                {
                    "raw": "m̩ n̩ → em en / else",
                    "stages": ["m̩ n̩", "em en"],
                    "exception": "_{s,({m,j,w})V}",
                },
            ],
            [
                {
                    "raw": "m̩ n̩ → am an / _{s,({m,j,w})V}",
                    "stages": ["m̩ n̩", "am an"],
                    "env": "_{s,mV,jV,wV}",
                },
                {
                    "raw": "m̩ n̩ → em en / else",
                    "stages": ["m̩ n̩", "em en"],
                    "exception": "_{s,mV,jV,wV}",
                },
            ],
            id="else_copied_exception",
        ),
        pytest.param(
            [
                {
                    "raw": "aː → aa / W_ ! when _{C{C,ː},#}",
                    "stages": ["aː", "aa"],
                    "env": "W_",
                    "exception": "when _{C{C,ː},#}",
                },
                {
                    "raw": "aː → a / else",
                    "stages": ["aː", "a"],
                    "env": "else",
                },
            ],
            [
                {
                    "raw": "aː → aa / W_ ! when _{C{C,ː},#}",
                    "stages": ["aː", "aa"],
                    "env": "W_",
                    "exception": "when _{CC,Cː,#}",
                },
                {"raw": "aː → a / else", "stages": ["aː", "a"], "env": "else"},
            ],
            id="deferred_else_prev_exception",
        ),
        pytest.param(
            [
                {
                    "stages": ["(h)ə{p,b}", "t"],
                    "env": "_l",
                },
                {
                    "stages": ["e(C){V[- low]} e(C)a", "e(C) e(C)ə"],
                },
                {
                    "stages": ["a(C){o,e}", "a"],
                },
            ],
            [
                {
                    "stages": ["(h)ə{p,b}", "t"],
                    "env": "_l",
                },
                {"stages": ["e(C){V[- low]} e(C)a", "e(C) e(C)ə"]},
                {"stages": ["a(C){o,e}", "a"]},
            ],
            id="leaves_bucket_d_stage_shapes",
        ),
    ],
)
def test_flatten_nested_sets_in_section_rules(rules_in, expected):
    rules = flatten_nested_sets_in_section_rules([_rule(r) for r in rules_in])
    assert len(rules) == len(expected)
    for rule, exp in zip(rules, expected, strict=True):
        dumped = rule.model_dump(exclude_none=True, mode="python")
        for key, value in exp.items():
            assert dumped[key] == value
