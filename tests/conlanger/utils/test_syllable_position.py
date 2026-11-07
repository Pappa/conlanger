"""Compile-time ASCA syllable position #% / %# transforms (ticket 98)."""

import pytest

from conlanger.compile.models.compile_fields import RuleEnv, RuleInput, RuleOutput
from conlanger.compile.models.rules import SoundChangeRule
from conlanger.compile.tools.asca.pipeline import compile_asca_rule_fields
from conlanger.compile.tools.asca.syllable_position import (
    apply_syllable_position_compiled_overrides,
    compile_syllable_position_env,
    compile_syllable_position_exception,
    normalize_syllable_position_marker,
    project_position_in_compiled_field,
    project_syllable_stress_compiled_env,
    strip_editorial_in_before_syllable_position,
)
from conlanger.ingest.models.index_models import IndexContext, IndexRule
from conlanger.ingest.utils.transforms import apply_syllable_position_editorial_strip
from conlanger.scripts.config_loaders import load_compiler_config


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("in #U", "#U"),
        ("in U#", "U#"),
        ("In #U", "#U"),
        ("in #U, U#", "#%, %#"),
        ("in #U,U#", "#%, %#"),
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
        ("#U, U#", "#%, %#"),
        ("in #U, U#", "#%, %#"),
        ("_V", None),
        ("#U before prose", None),
    ],
)
def test_normalize_syllable_position_marker(text, expected):
    assert normalize_syllable_position_marker(text) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("#U", "#<(..)_(..)>"),
        ("in #U", "#<(..)_(..)>"),
        ("U#", "<(..)_(..)>#"),
        ("in U#", "<(..)_(..)>#"),
        ("#U, U#", ":{#<(..)_(..)>, <(..)_(..)>#}:"),
        ("prose tail", None),
        (None, None),
    ],
)
def test_compile_syllable_position_exception(raw, expected):
    assert compile_syllable_position_exception(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("#U", "#<(..)_(..)>"),
        ("in #U", "#<(..)_(..)>"),
        ("U#", "<(..)_(..)>#"),
        ("in U#", "<(..)_(..)>#"),
        ("#U, U#", ":{#<(..)_(..)>, <(..)_(..)>#}:"),
        (None, None),
    ],
)
def test_compile_syllable_position_env(raw, expected):
    assert compile_syllable_position_env(raw) == expected


@pytest.mark.parametrize(
    ("env_raw", "compiled_before", "expected"),
    [
        ("%[-stress]", "%[-stress]", "<(..)_(..)>:[-stress]"),
        ("in %[+stress]", "in %[+stress]", "<(..)_(..)>:[+stress]"),
        ("#%[+stress]#", "#%[+stress]#", "#<(..)_(..)>:[+stress]#"),
        ("U[-nas]", "U[-nas]", "<(..)_(..)>:[-nas]"),
        ("%[-nas]", "%[-nas]", "<(..)_(..)>:[-nas]"),
        ("in U[-nas]", "in U[-nas]", "<(..)_(..)>:[-nas]"),
        (None, "C_CV, in %[-stress]", ":{C_CV, <(..)_(..)>:[-stress]}:"),
        (None, "_V", "_V"),
    ],
)
def test_project_syllable_stress_compiled_env(env_raw, compiled_before, expected):
    assert project_syllable_stress_compiled_env(env_raw, compiled_before) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "e:[+stress]_ in U[+lo]",
            ":{e:[+stress]_, <(..)_(..)>:[+lo]}:",
        ),
        (
            "e:[+stress]_ in %[+lo]",
            ":{e:[+stress]_, <(..)_(..)>:[+lo]}:",
        ),
        (
            ":{e:[+stress]_, %[+lo]}:",
            ":{e:[+stress]_, <(..)_(..)>:[+lo]}:",
        ),
        (
            "seg_ in U[+lo]",
            ":{seg_, <(..)_(..)>:[+lo]}:",
        ),
        (
            "_{m,ŋ} when posttonic in U[+hi] or when pretonic",
            ":{_{m,ŋ} when posttonic, <(..)_(..)>:[+hi] or when pretonic}:",
        ),
    ],
)
def test_project_position_in_compiled_field_env_set_syllable_tail(text, expected):
    assert project_position_in_compiled_field(text) == expected


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ("U[-stress]", "<(..)_(..)>:[-stress]"),
        ("in U[+stress]", "<(..)_(..)>:[+stress]"),
        ("#U[+stress]#", "#<(..)_(..)>:[+stress]#"),
        (
            "C_CV in U[-stress]",
            ":{C_CV, <(..)_(..)>:[-stress]}:",
        ),
        (
            "C_CV, in U[-stress]",
            ":{C_CV, <(..)_(..)>:[-stress]}:",
        ),
        ("w_ in U[-stress]", ":{w_, <(..)_(..)>:[-stress]}:"),
        ("in U:[+stress]", "<(..)_(..)>:[+stress]"),
        (
            "in U:[+stress][+lo]",
            "<(..)_(..)>:[+stress][+lo]",
        ),
        ("U[-nas]", "<(..)_(..)>:[-nas]"),
    ],
)
def test_compile_asca_rule_fields_syllable_stress_env(env, expected):
    config = load_compiler_config()
    input, output = "V", "V:[-long]"
    assert (
        compile_asca_rule_fields(
            input,
            output,
            env=env,
            compiler_config=config,
        )
        == f"{input} > {output} / {expected}"
    )


def test_apply_syllable_position_compiled_overrides_replaces_group_mapping_damage():
    env, exception = apply_syllable_position_compiled_overrides(
        "#U",
        "in #U",
        "U",
        ":{#_#, #U}:",
    )
    assert env == "#<(..)_(..)>"
    assert exception == "#<(..)_(..)>"


@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        ("#U", "#<(..)_(..)>"),
        ("in #U", "#<(..)_(..)>"),
        ("U#", "<(..)_(..)>#"),
        ("#U, U#", ":{#<(..)_(..)>, <(..)_(..)>#}:"),
    ],
)
def test_compile_asca_rule_fields_syllable_position_exceptions(exception, expected):
    input, output = "V", "V:[-long]"
    assert (
        compile_asca_rule_fields(input, output, exception=exception)
        == f"{input} > {output} // {expected}"
    )


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ("#U", "#<(..)_(..)>"),
        ("in #U", "#<(..)_(..)>"),
        ("U#", "<(..)_(..)>#"),
        ("in U#", "<(..)_(..)>#"),
    ],
)
def test_compile_asca_rule_fields_syllable_position_env(env, expected):
    input, output = "V", "V:[-long]"
    assert (
        compile_asca_rule_fields(input, output, env=env)
        == f"{input} > {output} / {expected}"
    )


def test_sound_change_rule_preserves_raw():
    rule = SoundChangeRule(
        input=RuleInput.from_raw("Vː"),
        output=RuleOutput.from_raw("V[-long]"),
        exception=RuleEnv.from_raw("in #U"),
        raw="Vː → V[-long] / ! in #U",
        detect_alternatives=False,
    )
    assert rule.raw == "Vː → V[-long] / ! in #U"
    assert rule.value == "V:[+long] > V:[-long] // #<(..)_(..)>"


def test_apply_syllable_position_editorial_strip_on_rule_parts():
    rule = IndexRule(
        raw="x",
        source="t",
        env=IndexContext(context="in #U"),
        exception=IndexContext(context="in U#"),
    )
    result = apply_syllable_position_editorial_strip(rule)
    dumped = result.to_index_dict()
    assert dumped["env"] == "#U"
    assert dumped["exception"] == "U#"
