"""Tests for subscript token classification and parse-time collective expansion."""

from __future__ import annotations

import pytest

from conlanger.ingest.models.index_models import IndexRule
from conlanger.ingest.utils.corpus_apply import apply_series_expansions
from conlanger.ingest.utils.series import (
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
    ("rule", "expected"),
    [
        ("sₓ → ʃ", "{s₁,s₂,s₃} → ʃ"),
        ("{Hₓ,m̩,n̩} → a", "{h₁,h₂,h₃,m̩,n̩} → a"),
        ("sₓ → ʃ / _sₓ", "{s₁,s₂,s₃} → ʃ / _{s₁,s₂,s₃}"),
        ("sₓ → ʃ / _sₓ ! Hₓ_", "{s₁,s₂,s₃} → ʃ / _{s₁,s₂,s₃} ! {h₁,h₂,h₃}_"),
    ],
)
def test_apply_series_expansions(rule, expected):
    expansions = {
        "sₓ": ("s₁", "s₂", "s₃"),
        "Hₓ": ("h₁", "h₂", "h₃"),
    }
    assert apply_series_expansions(rule, expansions) == expected
