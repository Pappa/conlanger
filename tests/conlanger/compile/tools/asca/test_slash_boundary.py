"""Tests for residual output/env slash-boundary compile transforms (ticket 82)."""

import pytest

from conlanger.compile.tools.asca.slash_boundary import (
    drop_concatenated_deletion_column,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{C,#,V:[+long]}∅ / _C", "{C,#,V:[+long]} / _C"),
        (
            "({C,#}Vː[+falling tone])∅ / _C",
            "({C,#}Vː[+falling tone]) / _C",
        ),
        (
            "{C,#,V:[+long, tone: 51]}∅ / _C",
            "{C,#,V:[+long, tone: 51]} / _C",
        ),
        ("{∅,h}", "{∅,h}"),
        ("χ > h / #_", "χ > h / #_"),
        ("", ""),
    ],
)
def test_drop_concatenated_deletion_column(text, expected):
    assert drop_concatenated_deletion_column(text) == expected
