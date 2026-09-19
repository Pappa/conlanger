"""Tests for BracketScanner and split_outside_brackets."""

import pytest

from conlanger.utils.bracket_scanner import (
    BRACES,
    BRACKETS,
    is_brace_wrapped,
    is_square_bracket_wrapped,
    split_outside_brackets,
)


@pytest.mark.parametrize(
    ("text", "start", "expected"),
    [
        ("{a,{b,c}}", 0, 8),
        ("{abc", 0, None),
        ("abc", 0, None),
        ("(x)", 0, None),
    ],
)
def test_braces_closing_index(text, start, expected):
    assert BRACES.closing_index(text, start) == expected


@pytest.mark.parametrize(
    ("text", "start"),
    [
        ("abc", 0),
        ("{abc", 0),
    ],
)
def test_braces_closing_index_rejects_invalid_starts(text, start):
    assert BRACES.closing_index(text, start) is None


def test_braces_top_level_spans_nested():
    assert BRACES.top_level_spans("{a,{b,c}}") == [(0, 9)]


@pytest.mark.parametrize(
    ("text", "separator", "expected", "kwargs"),
    [
        (
            "a,(b,c),d",
            ",",
            ["a", "(b,c)", "d"],
            {"strip_parts": True},
        ),  # test_split_outside_brackets_respects_nested_groupers
        (
            "a {b,c} d",
            " ",
            ["a", "{b,c}", "d"],
            {},
        ),  # test_split_outside_brackets_space_default_groupers
        (
            "a,{b,c},d",
            ",",
            ["a", "{b,c}", "d"],
            {"respect": (BRACES,), "strip_parts": True},
        ),  # test_split_outside_brackets_braces_only
        (
            "a  b",
            " ",
            ["a", "b"],
            {},
        ),  # test_split_if_non_empty_skips_blank_segments
    ],
)
def test_split_outside_brackets(text, separator, expected, kwargs):
    assert split_outside_brackets(text, separator, **kwargs) == expected


@pytest.mark.parametrize(
    ("text", "separator", "kwargs", "match"),
    [
        (
            "a b",
            "  ",
            {},
            "single character",
        ),  # test_split_rejects_multi_char_separator
        (
            "a,b",
            ",",
            {"flush_on_separator": "never"},
            "flush_on_separator",
        ),  # test_split_rejects_invalid_flush_mode
    ],
)
def test_split_outside_brackets_rejects_invalid_args(text, separator, kwargs, match):
    with pytest.raises(ValueError, match=match):
        split_outside_brackets(text, separator, **kwargs)


def test_braces_balance_and_max_depth():
    assert BRACES.balance("}{") < 0
    assert not BRACES.is_balanced("{a")
    assert BRACES.max_depth("{a,{b,c}}") == 2


def test_braces_top_level_spans_unbalanced_returns_empty():
    assert BRACES.top_level_spans("{a,{b") == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{a,b}", True),
        ("{a,b", False),
        ("", False),
        ("{}", True),
        ("x{a}", False),
    ],
)
def test_is_brace_wrapped(text, expected):
    assert is_brace_wrapped(text) == expected
    assert BRACES.wraps(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("[+stress]", True),
        ("[+stress", False),
        ("", False),
        ("[]", True),
    ],
)
def test_is_square_bracket_wrapped(text, expected):
    assert is_square_bracket_wrapped(text) == expected
    assert BRACKETS.wraps(text) == expected
