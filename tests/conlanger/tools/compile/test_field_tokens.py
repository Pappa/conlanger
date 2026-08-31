"""Field-token IR structure tests (ticket 105 / ADR-0015)."""

from __future__ import annotations

import pytest

from conlanger.tools.compile.asca.parallel import (
    _column_branch_pairs,
    drop_mixed_parallel_null_columns,
    drop_mixed_parallel_null_columns_tokens,
    expand_parallel_output_null_branches_from_tokens,
)
from conlanger.tools.compile.compile_fields import RuleInput, RuleOutput
from conlanger.tools.compile.field_tokens import (
    OptionalLengthNode,
    is_optional_output_shape,
    is_whole_field_set_tokens,
    parse_field_tokens,
    render_field_tokens,
)
from conlanger.tools.rules import SoundChangeRule


@pytest.mark.parametrize(
    ("raw", "expected_tokens"),
    [
        ("c ɲ", ("c", "ɲ")),
        ("{r,h}", (("r", "h"),)),
        ("d", ("d",)),
        ("", ()),
    ],
)
def test_parse_field_tokens_shape(raw, expected_tokens):
    assert parse_field_tokens(raw) == expected_tokens


def test_render_field_tokens_round_trip():
    raw = "{m,ɲ} n"
    assert render_field_tokens(parse_field_tokens(raw)) == raw


def test_optional_length_node_type_exists():
    node = OptionalLengthNode(segment="e")
    assert render_field_tokens((node,)) == "e(ː)"


@pytest.mark.parametrize(
    ("input_raw", "output_raw", "expected"),
    [
        ("d", "{∅,ð}", True),
        ("{a,b}", "{c,d}", False),
        ("d", "ð", False),
    ],
)
def test_is_optional_output_shape(input_raw, output_raw, expected):
    assert (
        is_optional_output_shape(
            parse_field_tokens(input_raw),
            parse_field_tokens(output_raw),
        )
        is expected
    )


def test_drop_mixed_parallel_null_columns_on_tokens():
    tokens = parse_field_tokens("∅ n")
    assert drop_mixed_parallel_null_columns_tokens(tokens) == ("n",)


def test_expand_parallel_null_branches_from_tokens():
    branches = expand_parallel_output_null_branches_from_tokens(
        parse_field_tokens("{r,h}"),
        parse_field_tokens("{∅,h}"),
    )
    assert branches is not None
    assert [render_field_tokens(inp) for inp, _ in branches] == ["r", "h"]
    assert [render_field_tokens(out) for _, out in branches] == ["∅", "h"]


def test_rule_input_holds_raw_tokens_and_compiled():
    rule = SoundChangeRule(input="a(ː)", output="e(ː)")
    assert isinstance(rule.input, RuleInput)
    assert rule.input.raw == "a(ː)"
    assert rule.input.tokens == ("a(ː)",)
    assert rule.input.compiled == "a:[+long]"
    assert isinstance(rule.output, RuleOutput)
    assert rule.output.compiled == "e:[+long]"


def test_rule_field_equality_hash_and_render():
    first = RuleInput.from_raw("a")
    second = RuleInput.from_raw("a")
    compiled = first.with_compiled("a:[+long]")
    assert first == second
    assert compiled == "a:[+long]"
    assert compiled.render() == "a:[+long]"
    assert str(compiled) == "a:[+long]"
    assert hash(first) == hash(second)
    assert first != 42


def test_rule_field_with_tokens_updates_raw():
    field = RuleInput.from_raw("a")
    updated = field.with_tokens(("b", "c"))
    assert updated.raw == "b c"
    assert updated.tokens == ("b", "c")


def test_rule_field_model_validate_from_dict():
    field = RuleInput.model_validate({"raw": "x", "tokens": ("x",), "compiled": "x"})
    assert field.tokens == ("x",)


def test_drop_mixed_parallel_null_columns_whitespace_only():
    assert drop_mixed_parallel_null_columns("   ") == "   "


def test_column_branch_pairs_empty_columns():
    assert _column_branch_pairs("", "{a,b}") is None


def test_optional_output_alternatives_use_field_token_gate():
    input_field = RuleInput.from_raw("d")
    output_field = RuleOutput.from_raw("{∅,ð}")
    assert is_whole_field_set_tokens(output_field.tokens)
    assert not is_whole_field_set_tokens(input_field.tokens)
    assert is_optional_output_shape(input_field.tokens, output_field.tokens)
    rule = SoundChangeRule(input="d", output="{∅,ð}")
    assert len(rule.alternatives) == 2
