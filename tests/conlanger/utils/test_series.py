"""Tests for subscript token classification and parse-time collective expansion."""

from __future__ import annotations

import pytest

from conlanger.utils.series import (
    apply_series_expansions,
    classify_subscript_token,
    expand_collectives_in_field,
    find_correspondence_series_tokens,
    find_subscript_tokens,
    is_collective_subscript_token,
    is_correspondence_series_token,
    is_identity_subscript_token,
    is_positional_slot_token,
    section_index_prefixes,
)


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("s₁", True),
        ("h₂", True),
        ("xₓ", True),
        ("sₓ", True),
        ("C₁", False),
        ("V₀", False),
        ("s", False),
        ("ʃ", False),
    ],
)
def test_is_correspondence_series_token(token, expected):
    assert is_correspondence_series_token(token) is expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("C₁", True),
        ("N₂", True),
        ("s₁", False),
    ],
)
def test_is_positional_slot_token(token, expected):
    assert is_positional_slot_token(token) is expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("V₀", True),
        ("h₀", True),
        ("s₁", False),
    ],
)
def test_is_identity_subscript_token(token, expected):
    assert is_identity_subscript_token(token) is expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("sₓ", True),
        ("hₓ", True),
        ("s₁", False),
    ],
)
def test_is_collective_subscript_token(token, expected):
    assert is_collective_subscript_token(token) is expected


def test_section_index_prefixes_shortest_first():
    assert section_index_prefixes("6.1.2.1") == ["6", "6.1", "6.1.2", "6.1.2.1"]


def test_find_correspondence_series_tokens_in_text():
    tokens = find_correspondence_series_tokens("s₁ s₂ → ʃ z / _{h₁,h₂}")
    assert tokens == {"s₁", "s₂", "h₁", "h₂"}


@pytest.mark.parametrize(
    ("token", "kind"),
    [
        ("s₁", "correspondence"),
        ("sₓ", "collective"),
        ("C₁", "positional"),
        ("V₀", "identity"),
        ("CV₁", "compound"),
        ("plain", "none"),
    ],
)
def test_classify_subscript_token(token, kind):
    assert classify_subscript_token(token) == kind


def test_find_correspondence_series_tokens_includes_collective():
    tokens = find_correspondence_series_tokens("sₓ s₁")
    assert tokens == {"sₓ", "s₁"}


def test_find_subscript_tokens_in_rule_fields():
    tokens = find_subscript_tokens("s₁ → ʃ / _ {C₁,V₀}")
    assert tokens == {"s₁", "C₁", "V₀"}


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ({"stages": ["sₓ", "ʃ"]}, {"stages": ["{s₁,s₂,s₃}", "ʃ"]}),
        ({"stages": ["{Hₓ,m̩,n̩}", "a"]}, {"stages": ["{h₁,h₂,h₃,m̩,n̩}", "a"]}),
        ({"env": "sₓ"}, {"env": "{s₁,s₂,s₃}"}),
        ({"exception": "sₓ"}, {"exception": "{s₁,s₂,s₃}"}),
    ],
)
def test_apply_series_expansions(input, expected):
    expansions = {"sₓ": ("s₁", "s₂", "s₃"), "Hₓ": ("h₁", "h₂", "h₃")}
    assert apply_series_expansions(input, expansions) == expected


def test_expand_collectives_in_field_unclosed_brace():
    expansions = {"Hₓ": ("h₁", "h₂", "h₃")}
    assert expand_collectives_in_field("{Hₓ foo", expansions) == "{{h₁,h₂,h₃} foo"
