"""Compile-time env/exception feature matrices (ticket 131)."""

import re
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.env_exception_feature_matrices import (
    _attach_matrix_to_literal_segment,
    _attach_matrix_to_token,
    _merge_feature_matrix_inners,
    apply_segment_at_focus_matrix_to_input,
    flip_feature_matrix_polarity,
    parse_bare_feature_matrix,
    resolve_bare_env_exception_feature_matrices,
)
from conlanger.tools.compile.asca.host_bracket_matrices import (
    normalize_asca_host_bracket_matrices,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("[-stress]", "[-stress]"),
        ("[ +stress ]", "[ +stress ]"),
        ("[-long, -stress]", "[-long, -stress]"),
        ("C[+voice]_", None),
        ("_[+rtr], [+rtr]_", None),
        ("[-stress], but not in every case", None),
        ("[-stress]: {o,ɔ}", None),
        (None, None),
        ("", None),
    ],
)
def test_parse_bare_feature_matrix(text, expected):
    assert parse_bare_feature_matrix(text) == expected


@pytest.mark.parametrize(
    ("matrix", "expected"),
    [
        ("[-stress]", "[+stress]"),
        ("[+stress]", "[-stress]"),
        ("[-long, -stress]", "[+long, +stress]"),
        ("[- stress]", "[+stress]"),
        ("not-a-matrix", "not-a-matrix"),
    ],
)
def test_flip_feature_matrix_polarity(matrix, expected):
    assert flip_feature_matrix_polarity(matrix) == expected


@pytest.mark.parametrize(
    ("inner_a", "inner_b", "expected"),
    [
        ("", "+stress", "+stress"),
        ("+long", "", "+long"),
    ],
)
def test_merge_feature_matrix_inners(inner_a, inner_b, expected):
    assert _merge_feature_matrix_inners(inner_a, inner_b) == expected


@pytest.mark.parametrize(
    ("text", "matrix", "expected"),
    [
        ("CV", "[-stress]", None),
    ],
)
def test_attach_matrix_to_literal_segment(text, matrix, expected):
    assert _attach_matrix_to_literal_segment(text, matrix) == expected


@pytest.mark.parametrize(
    ("token", "matrix", "expected", "patch_class_host_bracket"),
    [
        ("  ", "[-stress]", "  ", False),
        ("#_", "[-stress]", "#_", False),
        ("xAT[+long]y", "[-stress]", "xAT[+long]y", True),
    ],
)
def test_attach_matrix_to_token(
    token,
    matrix,
    expected,
    patch_class_host_bracket,
    mocker,
):
    if patch_class_host_bracket:
        mocker.patch(
            "conlanger.tools.compile.asca.env_exception_feature_matrices."
            "_CLASS_HOST_BRACKET_RE",
            re.compile(r"a^"),
        )
    assert _attach_matrix_to_token(token, matrix) == expected


@pytest.mark.parametrize(
    ("input_text", "matrix", "expected"),
    [
        ("V", "[-stress]", "V[-stress]"),
        ("V[+nas]", "[-stress]", "V[+nas, -stress]"),
        ("V:[-long]", "[-stress]", "V:[-long, -stress]"),
        ("tVk", "[-stress]", "tV[-stress]k"),
        ("tC[+voice]k", "[-stress]", "tC[+voice, -stress]k"),
        ("ts[+long]", "[-stress]", "ts[+long, -stress]"),
        ("{i,eː}", "[+stress]", "{i[+stress],e[+stress]ː}"),
        ("eː", "[+stress]", "e[+stress]ː"),
        ("", "[-stress]", ""),
        ("V", "", "V"),
    ],
)
def test_apply_segment_at_focus_matrix_to_input(input_text, matrix, expected):
    assert apply_segment_at_focus_matrix_to_input(input_text, matrix) == expected


@pytest.mark.parametrize(
    (
        "inp",
        "output",
        "env",
        "exception",
        "expected_inp",
        "expected_env",
        "expected_exc",
    ),
    [
        (
            "V",
            "ə",
            "[-stress]",
            None,
            "V[-stress]",
            "_",
            None,
        ),
        (
            "V",
            "∅",
            "#UU(_)U(U(_)U)",
            "[-stress]",
            "V[+stress]",
            "#UU(_)U(U(_)U)",
            None,
        ),
    ],
)
def test_resolve_bare_env_exception_feature_matrices(
    inp, output, env, exception, expected_inp, expected_env, expected_exc
):
    result_inp, result_output, result_env, result_exc = (
        resolve_bare_env_exception_feature_matrices(
            inp,
            output,
            env,
            exception,
            env_raw=env,
            exception_raw=exception,
        )
    )
    assert result_output == output
    assert result_inp == expected_inp
    assert result_env == expected_env
    assert result_exc == expected_exc


@pytest.mark.parametrize(
    ("inp", "output", "env", "exception", "expected"),
    [
        ("V", "ə", "[-stress]", None, "V:[-stress] > ə / _"),
        ("s", "z", "C[+voice]_", None, "s > z / C:[+voice]_"),
        (
            "V",
            "∅",
            "#UU(_)U(U(_)U)",
            "[-stress]",
            "V:[+stress] > ∅ / #UU(_)U(U(_)U)",
        ),
        (
            "{h,ħ,q}",
            "ʕ",
            "C[+voice]_V",
            None,
            "{h,ħ,q} > ʕ / C:[+voice]_V",
        ),
        (
            "a(ː)",
            "ɑ(ː)",
            "_ [+rtr], [+rtr]_",
            None,
            "{a,a:[+long]} > {ɑ,ɑ:[+long]} / _ [+rtr], [+rtr]_",
        ),
    ],
)
def test_compile_asca_rule_fields_env_exception_feature_matrices(
    inp, output, env, exception, expected
):
    assert compile_asca_rule_fields(inp, output, env, exception) == expected


def test_normalize_asca_host_bracket_matrices_on_env_exception():
    assert normalize_asca_host_bracket_matrices("C[+voice]_V") == "C:[+voice]_V"


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
        ("V", "ə", "[-stress]", None),
        ("s", "z", "C[+voice]_", None),
        ("V", "∅", "_#", "[-stress]"),
        ("{h,ħ,q}", "ʕ", "C[+voice]_V", None),
        ("a(ː)", "ɑ(ː)", "_ [+rtr], [+rtr]_", None),
    ],
)
def test_validate_asca_env_exception_feature_matrices(inp, output, env, exception):
    section = {
        "index": "131",
        "section": "env-exception-feature-matrices",
        "rules": [{"stages": [inp, output], "env": env, "exception": exception}],
    }
    words = _write_probe_words(["a.ta", "ata", "sza", "aha"])
    try:
        validate_asca(DiachronicSeries(section, "asca"), probe_words=words)
    finally:
        words.unlink(missing_ok=True)
