import pytest

from conlanger.tools.ingest.index_models import IndexContext, IndexRule
from conlanger.tools.ingest.prose_conditional_env import (
    apply_prose_conditional_env_conditions,
    normalize_prose_conditional_env_field,
)


def _rule_from_parts(parts: dict) -> IndexRule:
    rule = IndexRule(raw="x", source="t", stages=list(parts.get("stages") or []))
    if "env" in parts:
        rule.env = IndexContext(context=parts["env"])
    if "exception" in parts:
        rule.exception = IndexContext(context=parts["exception"])
    return rule


def _index_fields(rule: IndexRule) -> dict:
    dumped = rule.to_index_dict()
    out = {
        key: dumped[key]
        for key in ("stages", "env", "exception", "comment", "sporadic")
        if key in dumped
    }
    if out.get("stages") == []:
        out.pop("stages", None)
    return out


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
        _rule_from_parts(
            {
                "stages": ["a", "e"],
                "env": "[+stress], usually when Ḱ_",
            }
        )
    )
    fields = _index_fields(result)
    assert fields["stages"] == ["a:[+stress]", "e"]
    assert fields["env"] == "Ḱ_"
    assert "[+stress]" in result.comment


def test_apply_prose_conditional_strips_vague_env():
    result = apply_prose_conditional_env_conditions(
        _rule_from_parts({"stages": ["V", "Vː"], "env": "by analogy in some cases"})
    )
    fields = _index_fields(result)
    assert fields["env"] == "_"
    assert fields["sporadic"] is True
    assert "by analogy" in result.comment


def test_apply_prose_conditional_noop_on_structural_env():
    rule = _rule_from_parts({"stages": ["t", "k"], "env": "_#"})
    assert _index_fields(apply_prose_conditional_env_conditions(rule)) == _index_fields(
        rule
    )


def test_apply_prose_conditional_exception_only_prose():
    result = apply_prose_conditional_env_conditions(
        _rule_from_parts(
            {
                "stages": ["dʒ", "ʒ"],
                "exception": "syllables with a nasal or liquid",
            }
        )
    )
    fields = _index_fields(result)
    assert fields["exception"] == "_"
    assert "syllables with a nasal or liquid" in result.comment


def test_attach_bare_matrix_skips_ambiguous_input():
    result = apply_prose_conditional_env_conditions(
        _rule_from_parts(
            {
                "stages": ["a b", "c"],
                "env": "[-stress]",
            }
        )
    )
    fields = _index_fields(result)
    assert fields["env"] == "[-stress]"
    assert fields["stages"] == ["a b", "c"]


def test_normalize_prose_conditional_empty():
    assert normalize_prose_conditional_env_field("") == ("", [], {}, None)
