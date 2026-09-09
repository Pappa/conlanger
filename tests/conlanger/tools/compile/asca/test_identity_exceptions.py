"""Compile-time Index identity exceptions ``! Host = seg`` (ticket 128)."""

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.identity_exceptions import (
    IdentityExceptionBinding,
    apply_identity_exception_input_narrowing,
    parse_index_identity_exception,
    resolve_index_identity_exceptions,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.compile_fields import RuleEnv, RuleInput, RuleOutput
from conlanger.tools.rules import DiachronicSeries, SoundChangeRule
from tests.fixtures.minimal_mappings import minimal_compiler_config


@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        ("C = j", ("C", "j")),
        ("C = {ɡ,m,n,r,w,ʃ,x}", ("C", "{ɡ,m,n,r,w,ʃ,x}")),
        ("V = u", ("V", "u")),
        ("B = ɒ", ("B", "ɒ")),
        ("F = ʍ", ("F", "ʍ")),
        ("R = j", ("R", "j")),
        ("C = K", ("C", "K")),
        ("C = l, or when reduplicated", ("C", "l")),
    ],
)
def test_parse_index_identity_exception(exception, expected):
    assert parse_index_identity_exception(exception) == expected


@pytest.mark.parametrize(
    ("exception",),
    [
        (None,),
        ("",),
        ("prose only",),
        ("#U",),
    ],
)
def test_parse_index_identity_exception_returns_none(exception):
    assert parse_index_identity_exception(exception) is None


@pytest.mark.parametrize(
    ("inp", "output", "env", "exception", "expected"),
    [
        (
            "V",
            "e",
            "C_#",
            "C = j",
            "V > e / C_# // j_#",
        ),
        (
            "r",
            "ʔ",
            "C_{t,w,j}#",
            "C = {ɡ,m,n,r,w,ʃ,x}",
            "r > ʔ / C_{t,w,j}# // {ɡ,m,n,r,w,ʃ,x}_{t,w,j}#",
        ),
        (
            "w",
            "∅",
            "C_",
            "C = K",
            "w > ∅ / C_ // C:[-front,+back,+hi,-lo]_",
        ),
        (
            "V[-long]",
            "∅",
            "_#",
            "V = u",
            "{V:[-long],-u} > ∅ / _#",
        ),
        (
            "F",
            "F[+voice]",
            "#_",
            "F = ʍ",
            "{F,-ʍ} > F:[+voice] / #_",
        ),
        (
            "{B,E}",
            "∅",
            "CC_{ʀ,s,t,θ}#",
            "B = ɒ",
            "{V:[+back],V:[+front],-ɒ} > ∅ / CC_{ʀ,s,t,θ}#",
        ),
        (
            "s",
            "z",
            "{#,V}_{V,R}",
            "R = j",
            "s > z / {#,V}_{V,[+son,-syll]} // j_{V,[+son,-syll]}",
        ),
    ],
)
def test_compile_asca_rule_fields_identity_exceptions(
    inp, output, env, exception, expected
):
    compiled = compile_asca_rule_fields(
        inp,
        output,
        env,
        exception,
        compiler_config=minimal_compiler_config(),
    )
    assert compiled == expected


def test_resolve_index_identity_exceptions_family_a():
    inp, output, env, exception, pending = resolve_index_identity_exceptions(
        "V",
        "e",
        "C_#",
        "C = j",
        exception_raw="C = j",
        group_mappings=minimal_compiler_config().group_mappings,
    )
    assert inp == "V"
    assert output == "e"
    assert env == "C_#"
    assert exception == "j_#"
    assert pending is None


def test_parse_index_identity_exception_rejects_empty_rhs():
    assert parse_index_identity_exception("C = ") is None


def test_apply_identity_exception_input_narrowing_noop_when_unmatched():
    binding = IdentityExceptionBinding(
        host_raw="X",
        host_expanded="X",
        rhs="y",
    )
    assert apply_identity_exception_input_narrowing("abc", binding) == "abc"


def test_resolve_index_identity_exceptions_unchanged_when_no_match():
    inp, output, env, exception, pending = resolve_index_identity_exceptions(
        "s",
        "z",
        "_#",
        "C = j",
        exception_raw="C = j",
        group_mappings=minimal_compiler_config().group_mappings,
    )
    assert inp == "s"
    assert exception == "C = j"
    assert pending is None


def test_resolve_index_identity_exceptions_family_b_defers_bracket_input():
    inp, _output, _env, exception, pending = resolve_index_identity_exceptions(
        "V[-long]",
        "∅",
        "_#",
        "V = u",
        exception_raw="V = u",
        group_mappings=minimal_compiler_config().group_mappings,
    )
    assert exception is None
    assert pending is not None
    assert apply_identity_exception_input_narrowing(inp, pending) == "{V:[-long],-u}"


def test_sound_change_rule_preserves_raw_identity_exception():
    rule = SoundChangeRule(
        input=RuleInput.from_raw("V"),
        output=RuleOutput.from_raw("e"),
        env=RuleEnv.from_raw("C_#"),
        exception=RuleEnv.from_raw("C = j"),
        raw="V → e / C_# ! C = j",
        detect_alternatives=False,
    )
    assert rule.raw == "V → e / C_# ! C = j"
    assert rule.exception.raw == "C = j"
    assert rule.value == "V > e / C_# // j_#"


def _write_probe_words(words: list[str]) -> Path:
    with NamedTemporaryFile(
        "w", suffix=".wsca", delete=False, encoding="utf-8"
    ) as handle:
        handle.write("\n".join(words) + "\n")
        path = Path(handle.name)
    return path


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
@pytest.mark.parametrize(
    ("inp", "output", "env", "exception"),
    [
        ("V", "e", "C_#", "C = j"),
        ("F", "F[+voice]", "#_", "F = ʍ"),
    ],
)
def test_validate_asca_identity_exceptions(inp, output, env, exception):
    section = {
        "index": "128",
        "section": "identity-exceptions",
        "rules": [
            {
                "stages": [inp, output],
                "env": env,
                "exception": exception,
            }
        ],
    }
    words = _write_probe_words(["a.ta", "a", "ta.a", "a.ta.mi"])
    try:
        validate_asca(DiachronicSeries(section, "asca"), probe_words=words)
    finally:
        words.unlink(missing_ok=True)
