"""Tests for subscript token classification and parse-time collective expansion."""

from __future__ import annotations

import pytest

from conlanger.tools.ingest.index_models import IndexContext, IndexRule
from conlanger.tools.ingest.ingest_apply import apply_series_expansions
from conlanger.utils.series import (
    expand_collectives_in_field,
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


def _rule_from_field_parts(parts: dict) -> IndexRule:
    rule = IndexRule(raw="x", source="t", stages=list(parts.get("stages") or []))
    if "env" in parts:
        rule.env = IndexContext(context=parts["env"])
    if "exception" in parts:
        rule.exception = IndexContext(context=parts["exception"])
    return rule


def _field_parts(rule: IndexRule) -> dict:
    dumped = rule.to_index_dict()
    out = {key: dumped[key] for key in ("stages", "env", "exception") if key in dumped}
    if out.get("stages") == []:
        out.pop("stages", None)
    return out


@pytest.mark.parametrize(
    ("field_parts", "expected"),
    [
        ({"stages": ["sₓ", "ʃ"]}, {"stages": ["{s₁,s₂,s₃}", "ʃ"]}),
        ({"stages": ["{Hₓ,m̩,n̩}", "a"]}, {"stages": ["{h₁,h₂,h₃,m̩,n̩}", "a"]}),
        ({"env": "sₓ"}, {"env": "{s₁,s₂,s₃}"}),
        ({"exception": "sₓ"}, {"exception": "{s₁,s₂,s₃}"}),
    ],
)
def test_apply_series_expansions(field_parts, expected):
    expansions = {
        "sₓ": ("s₁", "s₂", "s₃"),
        "Hₓ": ("h₁", "h₂", "h₃"),
    }
    assert (
        _field_parts(
            apply_series_expansions(_rule_from_field_parts(field_parts), expansions)
        )
        == expected
    )


def test_expand_collectives_in_field_unclosed_brace():
    expansions = {"Hₓ": ("h₁", "h₂", "h₃")}
    assert expand_collectives_in_field("{Hₓ foo", expansions) == "{{h₁,h₂,h₃} foo"
