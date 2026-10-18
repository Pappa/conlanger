"""Classified ``position.in`` target projection (ticket 174)."""

import pytest

from conlanger.compile.position_in_projection import (
    PositionInAsca,
    env_is_projected_position_in_compile_string,
    materialize_position_in_asca,
    project_position_in_target,
)


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("#U", PositionInAsca("#<.._>", "#<.._>")),
        ("U#", PositionInAsca("<.._>#", "<.._>#")),
        ("U[-stress]", PositionInAsca("_ $[-stress]", "$[-stress]")),
        ("U[+stress]", PositionInAsca("_ $[+stress]", "$[+stress]")),
        ("U:[+stress]", PositionInAsca("_ %[+stress]", "%[+stress]")),
        (
            "U:[+stress][+lo]",
            PositionInAsca("_ %[+stress][+lo]", "%[+stress][+lo]"),
        ),
        ("#U[+stress]#", PositionInAsca("#_[+stress]", "#_[+stress]")),
        ("in #U", PositionInAsca("#<.._>", "#<.._>")),
        ("U:[+stress, +lo]", PositionInAsca("_ %[+stress][+lo]", "%[+stress][+lo]")),
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
    stress = PositionInAsca("_ $[-stress]", "$[-stress]")
    assert (
        materialize_position_in_asca(stress, structural_context=None) == "_ $[-stress]"
    )
    assert (
        materialize_position_in_asca(stress, structural_context="C_CV")
        == "C_CV in $[-stress]"
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("_ $[-stress]", True),
        ("_ %[+stress][+lo]", True),
        ("C_CV in $[-stress]", True),
        ("_ %[-nas]", False),
        ("in U[+lo]", False),
        ("prefix #<.._>", True),
    ],
)
def test_env_is_projected_position_in_compile_string(raw, expected):
    assert env_is_projected_position_in_compile_string(raw) is expected


def test_env_is_projected_position_in_compile_string_empty():
    assert env_is_projected_position_in_compile_string(None) is False
    assert env_is_projected_position_in_compile_string("  ") is False
