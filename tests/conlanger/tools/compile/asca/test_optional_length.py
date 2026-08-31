"""Parenthesized optional length ``(ː)`` expansion (ticket 104)."""

import shutil
from pathlib import Path

import pytest

from conlanger.tools.compile.asca.optional_length import (
    expand_optional_length_in_text,
    expand_optional_length_tokens,
    parse_optional_length_part,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.field_tokens import (
    OptionalLengthNode,
    parse_field_tokens,
    render_field_tokens,
)
from conlanger.tools.rules import DiachronicSeries, SoundChangeRule


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("e(ː)", "{e,e:[+long]}"),
        ("V3(ː)", "{V3,V3:[+long]}"),
        ("V3(ː)ʔ", "{V3ʔ,V3:[+long]ʔ}"),
        ("V:[+front](ː)", "{V:[+front],V:[+front, +long]}"),
        ("{o,u}(ː)", "{{o,u},{o:[+long],u:[+long]}}"),
        ("e(ː,j)", "{e,ej,e:[+long],e:[+long]j}"),
        ("_{i,e(ː),a}", "_{i,{e,e:[+long]},a}"),
        ("aː", "aː"),
    ],
)
def test_expand_optional_length_in_text(text, expected):
    assert expand_optional_length_in_text(text) == expected


def test_parse_optional_length_part_shapes():
    assert parse_optional_length_part("e(ː)") == OptionalLengthNode(segment="e")
    assert parse_optional_length_part("V3(ː)ʔ") == OptionalLengthNode(
        segment="V3", suffix="ʔ"
    )
    assert parse_optional_length_part("e(ː,j)") == OptionalLengthNode(
        segment="e", comma_alt="j"
    )


def test_field_tokens_parse_and_expand_optional_length():
    tokens = parse_field_tokens("e(ː) a")
    assert tokens[0] == OptionalLengthNode(segment="e")
    expanded = expand_optional_length_tokens(tokens)
    assert expanded[0] == ("e", "e:[+long]")
    assert render_field_tokens(expanded) == "{e,e:[+long]} a"


def test_sound_change_rule_compiles_optional_length():
    rule = SoundChangeRule(input="a(ː)", output="e(ː)")
    assert rule.input.compiled == "{a,a:[+long]}"
    assert rule.output.compiled == "{e,e:[+long]}"
    assert str(rule) == "\t{a,a:[+long]} > {e,e:[+long]}"


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        (
            {"input": "V3(ː)ʔ", "output": "V3(ː)ʔ", "env": "_#"},
            "\t{V3ʔ,V3:[+long]ʔ} > {V3ʔ,V3:[+long]ʔ} / _#",
        ),
        (
            {"input": "V3ʔ", "output": "V3(ː)ʔ", "env": "_#"},
            "\tV3ʔ > {V3ʔ,V3:[+long]ʔ} / _#",
        ),
        (
            {
                "input": "{t,dʱ}",
                "output": "tʲ",
                "env": "_V:[+front](ː)",
                "section_index": "17.13",
            },
            "\t{t,dʱ} > tʲ / _{V:[+front],V:[+front, +long]}",
        ),
    ],
    ids=["salish-template", "salish-comox-rule", "tocharian-matrix-env"],
)
def test_compile_optional_length_representative_rules(fields, expected):
    rule = SoundChangeRule(**fields)
    assert str(rule) == expected


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_validate_asca_optional_length_smoke():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "17.13",
        "section": "Optional length smoke",
        "rules": [
            {"stages": ["e(ː)", "a(ː)"]},
            {
                "stages": ["{t,dʱ}", "tʲ"],
                "env": "_V:[+front](ː)",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


def test_compile_rule_fields_tocharian_env():
    compiled = compile_asca_rule_fields("{t,dʱ}", "tʲ", env="_V:[+front](ː)")
    assert compiled == "{t,dʱ} > tʲ / _{V:[+front],V:[+front, +long]}"
