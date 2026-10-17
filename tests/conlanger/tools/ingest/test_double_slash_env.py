import pytest

from conlanger.compile.project_index_context import (
    resolve_rule_env_exception_for_compile,
)
from conlanger.ingest.models.index_models import IndexContext, IndexRule
from conlanger.ingest.utils.double_slash_env import (
    _merge_position,
    apply_double_slash_env_conditions,
    normalize_prose_env_head,
    normalize_prose_exception_or_env_tail,
    split_embedded_double_slash,
)
from conlanger.ingest.utils.index_context_position import (
    apply_index_context_position_extraction,
)


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        (
            {
                "exception": "adjacent to C",
            },
            {
                "exception": {"position": {"adjacent_to": "C"}},
            },
        ),
        (
            {
                "env": "#_e",
                "exception": "Logudorese",
            },
            {
                "env": "#_e",
                "comment": "Logudorese",
            },
        ),
        (
            {
                "env": "odd syllables",
                "exception": "_{w,j,H}",
            },
            {
                "env": "_",
                "exception": "_{w,j,H}",
                "comment": "odd syllables",
            },
        ),
        (
            {
                "env": "∅",
                "exception": "_#",
            },
            {
                "exception": "_#",
            },
        ),
        (
            {
                "exception": "onset of U[+stress]",
            },
            {
                "exception": "onset of U[+stress]",
            },
        ),
        (
            {
                "env": "#_",
                "exception": "before an identical vowel",
            },
            {
                "env": "#_",
                "exception": "V_V",
                "comment": "before an identical vowel",
            },
        ),
        (
            {
                "env": "maybe",
                "exception": "_#?",
            },
            {
                "env": "_",
                "exception": "_#",
                "comment": "maybe; ?",
                "sporadic": True,
            },
        ),
        (
            {
                "env": "odd syllables // _{w,j,H}",
            },
            {
                "env": "_",
                "exception": "_{w,j,H}",
                "comment": "odd syllables",
            },
        ),
        (
            {
                "env": "#_e // extra gloss",
                "exception": "_{w,j,H}",
            },
            {
                "env": "#_e",
                "exception": "_{w,j,H}",
                "comment": "extra gloss",
            },
        ),
        (
            {
                "exception": "_# (sporadic)",
            },
            {
                "exception": "_#",
                "comment": "(sporadic)",
                "sporadic": True,
            },
        ),
    ],
)
def test_apply_double_slash_env_conditions(parts, expected):
    args = {
        "raw": "x",
        "source": "t",
        "stages": [],
    }
    rule = IndexRule(**args, **parts)
    result = apply_index_context_position_extraction(
        apply_double_slash_env_conditions(rule)
    )
    assert result.to_index_dict() == {**expected, **args}


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_captures"),
    [
        ("{a,ɛ}_, typically", "{a,ɛ}_", ["typically"]),
        ("%[-stress]", "%[-stress]", ["%[-stress]"]),
        ("unstressed syllables", "U[-stress]", ["unstressed syllables"]),
        ("", "", []),
    ],
)
def test_normalize_prose_env_head(text, expected_env, expected_captures):
    env, captures, flags = normalize_prose_env_head(text)
    assert env == expected_env
    assert captures == expected_captures
    assert flags == {}


@pytest.mark.parametrize(
    ("text", "expected_context", "expected_position", "expected_captures"),
    [
        ("adjacent to ŋ", "adjacent to ŋ", None, []),
        ("adjacent to S", "adjacent to S", None, []),
        ("adjacent to C[+voice]", "adjacent to C[+voice]", None, []),
        ("Logudorese", None, None, ["Logudorese"]),
        ("onset of U[+stress]", "onset of U[+stress]", None, []),
        ("penult", None, {"penult": True}, ["penult"]),
        ("final syllables", "U#", None, ["final syllables"]),
        (
            "#% with the following conditions",
            "#% with the following conditions",
            None,
            ["#% with the following conditions"],
        ),
        ("_k, short only)", "_k", None, ["short only"]),
        ("%[-stress]", "%[-stress]", None, ["%[-stress]"]),
        ("", None, None, []),
    ],
)
def test_normalize_prose_exception_or_env_tail(
    text, expected_context, expected_position, expected_captures
):
    ctx, captures, flags = normalize_prose_exception_or_env_tail(text)
    if expected_context is None and expected_position is None:
        assert ctx is None
    else:
        assert ctx is not None
        assert ctx.context == expected_context
        assert ctx.position == expected_position
    assert captures == expected_captures
    assert flags == {}


@pytest.mark.parametrize(
    ("text", "expected_head", "expected_tail"),
    [
        ("odd syllables // _{w,j,H}", "odd syllables", "_{w,j,H}"),
        ("#_e", "#_e", None),
    ],
)
def test_split_embedded_double_slash(text, expected_head, expected_tail):
    assert split_embedded_double_slash(text) == (expected_head, expected_tail)


@pytest.mark.parametrize(
    ("env", "exception", "expected_env", "expected_exc"),
    [
        (
            {"context": "V_C"},
            {"position": {"penult": True}},
            "V_C",
            "%_",
        ),
        (
            {"context": "#_"},
            {"context": "V_V"},
            "#_",
            "V_V",
        ),
    ],
)
def test_double_slash_compile_round_trip(env, exception, expected_env, expected_exc):
    assert resolve_rule_env_exception_for_compile(env, exception) == (
        expected_env,
        expected_exc,
    )


def test_merge_position_no_inputs_returns_none():
    assert _merge_position(None) is None


def test_apply_skips_exception_without_context_string():
    rule = IndexRule(
        raw="x",
        source="t",
        stages=[],
        exception={"position": {"penult": True}},
    )
    result = apply_double_slash_env_conditions(rule)
    assert result.exception == IndexContext(position={"penult": True})


def test_normalize_prose_exception_voice_earlier_unchanged():
    ctx, captures, flags = normalize_prose_exception_or_env_tail(
        "O[+voice] earlier in the word"
    )
    assert ctx is not None
    assert ctx.context == "O[+voice] earlier in the word"
    assert captures == ["O[+voice] earlier in the word"]
    assert flags == {}


def test_normalize_prose_exception_complex_prose_unchanged():
    ctx, captures, flags = normalize_prose_exception_or_env_tail(
        "#% with the following conditions"
    )
    assert ctx is not None
    assert ctx.context == "#% with the following conditions"
    assert captures == ["#% with the following conditions"]
    assert flags == {}
