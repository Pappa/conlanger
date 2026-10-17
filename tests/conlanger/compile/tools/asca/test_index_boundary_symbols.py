"""Compile-time Index ``%`` / stem ``$`` → ASCA ``$`` (ticket 153)."""

import pytest

from conlanger.compile.models.config import CompilerConfig
from conlanger.compile.tools.asca.pipeline import compile_asca_rule_fields
from conlanger.utils.symbols import project_index_syllable_stem_symbols
from tests.conftest import MINIMAL_GROUP_MAPPINGS


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("#_", "#_"),
        ("∅", "∅"),
        ("_$%oː", "_$$oː"),
        ("$am_w", "$am_w"),
        ("_%U(%,0)#", "_$U($,0)#"),
        ("%ː", "%ː"),
    ],
)
def test_project_index_syllable_stem_symbols(text, expected):
    assert project_index_syllable_stem_symbols(text) == expected


def test_compile_projects_syllable_stem_symbols_before_group_mappings():
    cfg = CompilerConfig(group_mappings=MINIMAL_GROUP_MAPPINGS)
    compiled = compile_asca_rule_fields(
        "a", "b", "_%U(%,0)#", None, compiler_config=cfg
    )
    assert compiled == "a > b / _$%($,0)#"


def test_compile_stem_plus_syllable_boundary():
    compiled = compile_asca_rule_fields("{o,u}(ː)", "iː", "_$%oː", None)
    assert compiled.endswith(" / _$$o:[+long]")
