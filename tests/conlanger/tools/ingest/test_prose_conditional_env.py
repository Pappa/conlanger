import pytest

from conlanger.tools.ingest.prose_conditional_env import (
    apply_prose_conditional_env_conditions,
    normalize_prose_conditional_env_field,
)


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_comment_part"),
    [
        ("the unstressed penult", "%_", "unstressed penult"),
        ("utterance-initially", "#_", "utterance-initially"),
        ("before modal suffixes", "_$", "before modal suffixes"),
        ("short only", "_", "short only"),
        ("syllables with /ɦ/", "_", "syllables with /ɦ/"),
        ("[-stress], but not in every case", "[-stress]", "but not in every case"),
        ("if the *a is not stressed", "_ *a[-stress]", "if the *a is not stressed"),
    ],
)
def test_normalize_prose_conditional_env_field(
    text, expected_env, expected_comment_part
):
    env, captures, _flags, _matrix = normalize_prose_conditional_env_field(text)
    assert env == expected_env
    assert any(expected_comment_part in fragment for fragment in captures)


@pytest.mark.parametrize(
    ("text", "expected_env", "sporadic"),
    [
        ("by analogy in some cases", "_", True),
        ("the name of the river", "_", True),
        ("a few data sets", "_", True),
        (
            "something to do with either back vowels or prefixes",
            "_",
            True,
        ),
        ("if /l/ is present in the same syllable", "_", True),
        (
            "V_V, where at least one of the vowels is nasalized",
            "V_V",
            False,
        ),
    ],
)
def test_normalize_prose_conditional_vague_and_where(text, expected_env, sporadic):
    env, captures, flags, _matrix = normalize_prose_conditional_env_field(text)
    assert env == expected_env
    assert bool(flags.get("sporadic")) is sporadic
    assert captures


def test_normalize_prose_conditional_bare_matrix_input_merge():
    env, _caps, _flags, matrix = normalize_prose_conditional_env_field("[-stress]")
    assert env == "[-stress]"
    assert matrix == "[-stress]"


def test_apply_prose_conditional_env_rhaeto_romance_stress_on_input():
    result = apply_prose_conditional_env_conditions(
        {
            "stages": ["a", "e"],
            "env": "[+stress], usually when Ḱ_",
        }
    )
    assert result["stages"] == ["a:[+stress]", "e"]
    assert result["env"] == "Ḱ_"
    assert "[+stress]" in result["comment"]


def test_apply_prose_conditional_strips_vague_env():
    result = apply_prose_conditional_env_conditions(
        {"stages": ["V", "Vː"], "env": "by analogy in some cases"}
    )
    assert result["env"] == "_"
    assert result["sporadic"] is True
    assert "by analogy" in result["comment"]


def test_apply_prose_conditional_noop_on_structural_env():
    parts = {"stages": ["t", "k"], "env": "_#"}
    assert apply_prose_conditional_env_conditions(parts) == parts


def test_apply_prose_conditional_exception_only_prose():
    result = apply_prose_conditional_env_conditions(
        {
            "stages": ["dʒ", "ʒ"],
            "exception": "syllables with a nasal or liquid",
        }
    )
    assert result["exception"] == "_"
    assert "syllables with a nasal or liquid" in result["comment"]


def test_attach_bare_matrix_skips_ambiguous_input():
    result = apply_prose_conditional_env_conditions(
        {
            "stages": ["a b", "c"],
            "env": "[-stress]",
        }
    )
    assert result["env"] == "[-stress]"
    assert result["stages"] == ["a b", "c"]


def test_normalize_prose_conditional_empty():
    assert normalize_prose_conditional_env_field("") == ("", [], {}, None)
