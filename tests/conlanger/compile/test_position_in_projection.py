"""Classified ``position.in`` target projection (ticket 174)."""

import pytest

from conlanger.compile.position_in_projection import (
    env_is_projected_position_in_compile_string,
    materialize_position_in_asca,
    project_position_in_target,
)


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("#U", "#<(..)_(..)>"),
        ("U#", "<(..)_(..)>#"),
        (
            "U[-stress]",
            "<(..)_(..)>:[-stress]",
        ),
        (
            "U[+stress]",
            "<(..)_(..)>:[+stress]",
        ),
        (
            "U:[+stress]",
            "<(..)_(..)>:[+stress]",
        ),
        (
            "U:[+stress][+lo]",
            "<(..)_(..)>:[+stress][+lo]",
        ),
        (
            "#U[+stress]#",
            "#<(..)_(..)>:[+stress]#",
        ),
        ("in #U", "#<(..)_(..)>"),
        (
            "U:[+stress, +lo]",
            "<(..)_(..)>:[+stress][+lo]",
        ),
    ],
)
def test_project_position_in_target_classified(target, expected):
    assert project_position_in_target(target) == expected


@pytest.mark.parametrize(
    "target",
    ["U[+lo]", "U:[-stress]", "#U, U#", "", "   "],
)
def test_project_position_in_target_unclassified(target):
    assert project_position_in_target(target) is None


def test_materialize_position_in_asca():
    stress = "<(..)_(..)>:[-stress]"
    assert (
        materialize_position_in_asca(stress, structural_context=None)
        == "<(..)_(..)>:[-stress]"
    )
    assert (
        materialize_position_in_asca(stress, structural_context="C_CV")
        == "C_CV in <(..)_(..)>:[-stress]"
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("_ $[-stress]", True),
        ("_ %[+stress][+lo]", True),
        ("C_CV in $[-stress]", True),
        ("_ %[-nas]", False),
        ("in U[+lo]", False),
        ("prefix #<(..)_(..)>", True),
        (None, False),
        ("  ", False),
    ],
)
def test_env_is_projected_position_in_compile_string(raw, expected):
    assert env_is_projected_position_in_compile_string(raw) is expected
