"""Tests for ASCA feature-matrix string helpers."""

from __future__ import annotations

import pytest

from conlanger.utils.features import (
    add_features_to_matrix_body,
    apply_features_to_token,
    merge_mapping_with_features,
)


@pytest.mark.parametrize(
    ("body", "extra", "expected"),
    [
        ("+stop", ("+voice",), "+stop,+voice"),
        ("", ("cg",), "+cg"),
        ("+nasal", ("-round",), "+nasal,-round"),
        ("+voice", ("+voice",), "+voice"),
        ("+voice", ("voice",), "+voice"),
        ("-voice", ("+voice",), "-voice"),
    ],
)
def test_add_features_to_matrix_body(body, extra, expected):
    assert add_features_to_matrix_body(body, extra) == expected


@pytest.mark.parametrize(
    ("token", "extra", "expected"),
    [
        ("p", (), "p"),
        ("p", ("+voice",), "p:[+voice]"),
        ("p:[+stop]", ("+voice",), "p:[+stop,+voice]"),
    ],
)
def test_apply_features_to_token(token, extra, expected):
    assert apply_features_to_token(token, extra) == expected


@pytest.mark.parametrize(
    ("mapping", "features", "expected"),
    [
        ("p", "+voice", "p:[+voice]"),
        ("{p,t}", "+voice", "{p:[+voice],t:[+voice]}"),
        ("{p,k}", "+cg,-round", "{p:[+cg,-round],k:[+cg,-round]}"),
    ],
)
def test_merge_mapping_with_features(mapping, features, expected):
    assert merge_mapping_with_features(mapping, features) == expected
