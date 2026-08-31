"""Compile-time ASCA syllable position #U / U# transforms (ticket 98)."""

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.asca.syllable_position import (
    apply_syllable_position_compiled_overrides,
    compile_syllable_position_env,
    compile_syllable_position_exception,
    normalize_syllable_position_marker,
    strip_editorial_in_before_syllable_position,
)
from conlanger.tools.compile.compile_fields import RuleEnv, RuleInput, RuleOutput
from conlanger.tools.ingest.transforms import apply_syllable_position_editorial_strip
from conlanger.tools.rules import DiachronicSeries, SoundChangeRule


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("in #U", "#U"),
        ("in U#", "U#"),
        ("In #U", "#U"),
        ("in #U, U#", "#U, U#"),
        ("in #U,U#", "#U, U#"),
        ("#U", "#U"),
        ("_V", "_V"),
        ("#U before a U with /iː/", "#U before a U with /iː/"),
    ],
)
def test_strip_editorial_in_before_syllable_position(text, expected):
    assert strip_editorial_in_before_syllable_position(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("#U", "#U"),
        ("in #U", "#U"),
        ("U#", "U#"),
        ("#U, U#", "#U, U#"),
        ("in #U, U#", "#U, U#"),
        ("_V", None),
        ("#U before prose", None),
    ],
)
def test_normalize_syllable_position_marker(text, expected):
    assert normalize_syllable_position_marker(text) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("#U", ":{#_#, #<.._>}:"),
        ("in #U", ":{#_#, #<.._>}:"),
        ("U#", ":{#_#, <.._>#}:"),
        ("in U#", ":{#_#, <.._>#}:"),
        ("#U, U#", ":{#_#, #<.._>, <.._>#}:"),
        ("prose tail", None),
        (None, None),
    ],
)
def test_compile_syllable_position_exception(raw, expected):
    assert compile_syllable_position_exception(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("#U", "#<.._>"),
        ("in #U", "#<.._>"),
        ("U#", "<.._>#"),
        ("in U#", "<.._>#"),
        ("#U, U#", None),
        (None, None),
    ],
)
def test_compile_syllable_position_env(raw, expected):
    assert compile_syllable_position_env(raw) == expected


def test_apply_syllable_position_compiled_overrides_replaces_group_mapping_damage():
    env, exception = apply_syllable_position_compiled_overrides(
        "#U",
        "in #U",
        "%",
        ":{#_#, #%}:",
    )
    assert env == "#<.._>"
    assert exception == ":{#_#, #<.._>}:"


@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        ("#U", "V:[+long] > V[-long] // :{#_#, #<.._>}:"),
        ("in #U", "V:[+long] > V[-long] // :{#_#, #<.._>}:"),
        ("U#", "V:[+long] > V[-long] // :{#_#, <.._>#}:"),
        ("#U, U#", "V:[+long] > V[-long] // :{#_#, #<.._>, <.._>#}:"),
    ],
)
def test_compile_asca_rule_fields_syllable_position_exceptions(exception, expected):
    assert compile_asca_rule_fields("Vː", "V[-long]", exception=exception) == expected


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ("#U", "V:[+long] > V[-long] / #<.._>"),
        ("in #U", "V:[+long] > V[-long] / #<.._>"),
        ("U#", "V:[+long] > V[-long] / <.._>#"),
        ("in U#", "V:[+long] > V[-long] / <.._>#"),
    ],
)
def test_compile_asca_rule_fields_syllable_position_env(env, expected):
    assert compile_asca_rule_fields("Vː", "V[-long]", env=env) == expected


def test_sound_change_rule_preserves_raw():
    rule = SoundChangeRule(
        input=RuleInput.from_raw("Vː"),
        output=RuleOutput.from_raw("V[-long]"),
        exception=RuleEnv.from_raw("in #U"),
        raw="Vː → V[-long] / ! in #U",
        detect_alternatives=False,
    )
    assert rule.raw == "Vː → V[-long] / ! in #U"
    assert rule.value == "V:[+long] > V[-long] // :{#_#, #<.._>}:"


def test_apply_syllable_position_editorial_strip_on_rule_parts():
    parts = apply_syllable_position_editorial_strip(
        {"env": "in #U", "exception": "in U#"}
    )
    assert parts == {"env": "#U", "exception": "U#"}


def _write_probe_words(words: list[str]) -> Path:
    with NamedTemporaryFile(
        "w", suffix=".wsca", delete=False, encoding="utf-8"
    ) as handle:
        handle.write("\n".join(words) + "\n")
        path = Path(handle.name)
    return path


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
@pytest.mark.parametrize(
    "exception",
    ["#U", "U#", "#U, U#"],
)
def test_validate_asca_syllable_position_exceptions(exception):
    section = {
        "index": "98",
        "section": "syllable-position",
        "rules": [{"stages": ["V:[+long]", "[-long]"], "exception": exception}],
    }
    words = _write_probe_words(
        ["ska:.ta:", "a:", "ta:.ska:", "a:.ta:", "a", "ska:.ta:.mi:"]
    )
    try:
        validate_asca(DiachronicSeries(section, "asca"), probe_words=words)
    finally:
        words.unlink(missing_ok=True)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_validate_asca_syllable_position_positive_env():
    section = {
        "index": "98",
        "section": "syllable-position-env",
        "rules": [{"stages": ["V:[+long]", "[-long]"], "env": "in #U"}],
    }
    words = _write_probe_words(["ska:.ta:", "a:", "ta:.ska:"])
    try:
        validate_asca(DiachronicSeries(section, "asca"), probe_words=words)
    finally:
        words.unlink(missing_ok=True)
