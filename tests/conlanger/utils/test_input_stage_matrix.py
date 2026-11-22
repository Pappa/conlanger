"""Tests for parse-tier input stage matrix attachment."""

from __future__ import annotations

import pytest

from conlanger.utils.input_stage_matrix import attach_focus_matrix_to_input_stage


@pytest.mark.parametrize(
    ("stages", "matrix", "expected"),
    [
        (["V[+mid]", "ɘ"], "[+stress]", ["V[+mid, +stress]", "ɘ"]),
        (["V", "ɘ"], "[-stress]", ["V:[-stress]", "ɘ"]),
        (["V:[+long]", "Vː"], "[+stress]", ["V:[+long, +stress]", "Vː"]),
        (["", "a"], "[+stress]", None),
        ([], "[+stress]", None),
        (["{V,a}", "e"], "[+stress]", None),
        (["V", "e"], "", None),
    ],
)
def test_attach_focus_matrix_to_input_stage(stages, matrix, expected):
    result = attach_focus_matrix_to_input_stage(stages, matrix)
    assert result == expected
