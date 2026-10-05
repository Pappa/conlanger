"""Tests for subscript token classification and parse-time collective expansion."""

from __future__ import annotations

import pytest

from conlanger.tools.ingest.corpus_apply import apply_series_expansions
from conlanger.tools.ingest.index_models import IndexRule
from conlanger.utils.series import (
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


@pytest.mark.parametrize(
    ("field_parts", "expected"),
    [
        ({"stages": ["sₓ", "ʃ"]}, {"stages": ["{s₁,s₂,s₃}", "ʃ"]}),
        ({"stages": ["{Hₓ,m̩,n̩}", "a"]}, {"stages": ["{h₁,h₂,h₃,m̩,n̩}", "a"]}),
        ({"env": "sₓ"}, {"env": "{s₁,s₂,s₃}"}),
        ({"exception": "sₓ"}, {"exception": "{s₁,s₂,s₃}"}),
        ({"stages": ["{sₓ,Hₓ}", "a"]}, {"stages": ["{s₁,s₂,s₃,h₁,h₂,h₃}", "a"]}),
    ],
)
def test_apply_series_expansions(field_parts, expected):
    expansions = {
        "sₓ": ("s₁", "s₂", "s₃"),
        "Hₓ": ("h₁", "h₂", "h₃"),
    }
    rule = IndexRule(raw="x", source="t", **field_parts)
    expected_rule = IndexRule(raw="x", source="t", **expected)
    assert apply_series_expansions(rule, expansions) == expected_rule
