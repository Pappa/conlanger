import pytest

from conlanger.tools.ingest.index_models import (
    IndexRule,
    join_rule_comment,
)
from conlanger.tools.ingest.transforms import (
    MEDIAL_BOUNDARY_EXCEPTION,
    apply_medial_env_conditions,
    apply_sporadic_qualifier,
    apply_stress_conditions,
    apply_trailing_glosses,
    normalize_medial_env_field,
    normalize_stress_conditions,
)


def test_apply_medial_env_conditions_bare_medial():
    result = apply_medial_env_conditions(
        IndexRule(raw="x", source="t", stages=["t", "r"], env="medially")
    )
    assert result.to_index_dict() == {
        "raw": "x",
        "source": "t",
        "stages": ["t", "r"],
        "env": "_",
        "exception": MEDIAL_BOUNDARY_EXCEPTION,
    }


def test_apply_medial_env_conditions_structural_when_medial():
    result = apply_medial_env_conditions(
        IndexRule(
            raw="x", source="t", stages=["m", "β"], env="C[-voice]_n, when medial"
        )
    )
    assert result.to_index_dict() == {
        "raw": "x",
        "source": "t",
        "stages": ["m", "β"],
        "env": "C[-voice]_n",
        "exception": MEDIAL_BOUNDARY_EXCEPTION,
    }


def test_apply_medial_env_conditions_deferred_env_and_exception():
    rule = IndexRule(
        raw="x",
        source="t",
        stages=["b", "h"],
        env="medially,",
        exception="{r(ʲ),l(ʲ)}_ or _ɡ",
    )
    assert apply_medial_env_conditions(rule).to_index_dict() == rule.to_index_dict()


@pytest.mark.parametrize(
    "input, output",
    [
        (
            {"stages": ["p", "h sporadic"]},
            {"stages": ["p", "h"], "comment": "sporadic"},
        ),
        (
            {
                "stages": ["p", "h (sometimes)"],
            },
            {"stages": ["p", "h"], "comment": "(sometimes)"},
        ),
        (
            {"stages": ["p", "h sometimes?"]},
            {"stages": ["p", "h"], "comment": "sometimes?"},
        ),
        (
            {"stages": ["p", "h occasionally?"]},
            {"stages": ["p", "h"], "comment": "occasionally?"},
        ),
        (
            {"stages": ["k", "∅"], "env": "sporadic", "comment": "in Mentasta Ahtna"},
            {
                "stages": ["k", "∅"],
                "comment": "in Mentasta Ahtna; sporadic",
            },  # TODO: check this is correct
        ),
    ],
)
def test_apply_sporadic_qualifier(input, output):
    args = {
        "raw": "x",
        "source": "t",
    }
    rule = IndexRule(**args, **input)
    result = apply_sporadic_qualifier(rule)
    assert result.to_index_dict() == {**args, **output, "sporadic": True}


def test_apply_sporadic_qualifier_unchanged_when_no_marker():
    rule = IndexRule(raw="x", source="t", stages=["a", "e"], env="_#")
    assert apply_sporadic_qualifier(rule).to_index_dict() == rule.to_index_dict()


def test_apply_stress_conditions():
    result = apply_stress_conditions(
        IndexRule(raw="x", source="t", stages=["a", "e"], env="_C(C), when stressed")
    )
    assert result.to_index_dict() == {
        "raw": "x",
        "source": "t",
        "stages": ["a", "e"],
        "env": "_C(C) when stressed",
    }
    cleaned = apply_stress_conditions(
        IndexRule(
            raw="x",
            source="t",
            stages=["ɾ", "∅"],
            env="V_V, when neither vowel is stressed",
        )
    )
    assert cleaned.to_index_dict()["env"] == "V_V"
    assert "when neither vowel is stressed" in cleaned.comment


def test_apply_trailing_glosses():
    result = apply_trailing_glosses(
        IndexRule(
            raw="x",
            source="t",
            stages=["j", "p (some Polynesian languages, such as Levei and Drehet)"],
        )
    )
    assert result.to_index_dict() == {
        "raw": "x",
        "source": "t",
        "stages": ["j", "p"],
        "comment": "(some Polynesian languages, such as Levei and Drehet)",
    }


def test_apply_trailing_glosses_strips_field_wrapped_gloss_to_comment():
    result = apply_trailing_glosses(
        IndexRule(raw="x", source="t", stages=["hhy", '"something like /ʒ/"'])
    )
    assert result.to_index_dict() == {
        "raw": "x",
        "source": "t",
        # TODO: check this is correct - seems wrong
        "stages": ["hhy", ""],
        "comment": '"something like /ʒ/"',
    }


def test_apply_trailing_glosses_keeps_unclosed_paren_on_env():
    """Env/exception unclosed parens stay paired for compile-time gloss strip."""
    result = apply_trailing_glosses(
        IndexRule(
            raw="x",
            source="t",
            stages=["Vn", "ṽ"],
            env="_# (seems to have been reverted in most dialects",
            exception="for Souletin)",
        )
    )
    assert result.to_index_dict() == {
        "raw": "x",
        "source": "t",
        "stages": ["Vn", "ṽ"],
        "env": "_# (seems to have been reverted in most dialects",
        "exception": "for Souletin)",
    }


def test_join_rule_comment():
    assert join_rule_comment(None, "  a  ", "b") == "a; b"
    assert join_rule_comment() is None


@pytest.mark.parametrize(
    ("text", "expected_env", "expected_medial"),
    [
        ("medial", "_", True),
        ("medially", "_", True),
        ("medially,", "_", True),
        ("  Medial  ", "_", True),
        ("when medial", "_", True),
        ("C[-voice]_n, when medial", "C[-voice]_n", True),
        ("_k, when medial", "_k", True),
        ("_#", "_#", False),
        ("ku_", "ku_", False),
    ],
)
def test_normalize_medial_env_field(text, expected_env, expected_medial):
    env, is_medial = normalize_medial_env_field(text)
    assert env == expected_env
    assert is_medial is expected_medial


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("V_V, when neither vowel is stressed", "V_V"),
        ("_C(C), when stressed", "_C(C) when stressed"),
        ("_$, when stressed", "_$ when stressed"),
        ("_N, when unstressed (?)", "_N when unstressed (?)"),
        ("when unstressed", "_ when unstressed"),
        (
            "when stressed unless primarily stressed",
            "_ when stressed unless primarily stressed",
        ),
        ("_# when unstressed", "_#"),
        ("_#, when unstressed", "_#"),
        ("C_# when unstressed", "C_#"),
        ("in open syllables, when stressed", "_ when stressed"),
        ("short only when unstressed", "_ when unstressed"),
        ("_j when stressed", "_j when stressed"),
        ("l_ when unstressed", "l_ when unstressed"),
        ("_#", "_#"),
    ],
)
def test_normalize_stress_conditions(text, expected):
    cleaned, _ = normalize_stress_conditions(text)
    assert cleaned == expected


def test_split_semicolon_comment_via_build():
    rule = IndexRule(raw="a → b ; tail", source="test").init()
    assert rule.stages == ["a", "b"]
    assert rule.comment == "tail"
    rule = IndexRule(raw="no semicolon", source="test").init()
    assert rule.comment is None
