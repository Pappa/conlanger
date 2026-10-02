import pytest

from conlanger.tools.ingest.transforms import (
    MEDIAL_BOUNDARY_EXCEPTION,
    apply_medial_env_conditions,
    apply_sporadic_qualifier,
    apply_stress_conditions,
    apply_trailing_glosses,
    join_rule_comment,
    normalize_medial_env_field,
    normalize_stress_conditions,
    split_field_semicolon_comment,
    split_line_semicolon_comment,
)


def test_apply_medial_env_conditions_bare_medial():
    assert apply_medial_env_conditions({"stages": ["t", "r"], "env": "medially"}) == {
        "stages": ["t", "r"],
        "env": "_",
        "exception": MEDIAL_BOUNDARY_EXCEPTION,
    }


def test_apply_medial_env_conditions_structural_when_medial():
    assert apply_medial_env_conditions(
        {"stages": ["m", "β"], "env": "C[-voice]_n, when medial"}
    ) == {
        "stages": ["m", "β"],
        "env": "C[-voice]_n",
        "exception": MEDIAL_BOUNDARY_EXCEPTION,
    }


def test_apply_medial_env_conditions_deferred_env_and_exception():
    parts = {
        "stages": ["b", "h"],
        "env": "medially,",
        "exception": "{r(ʲ),l(ʲ)}_ or _ɡ",
    }
    assert apply_medial_env_conditions(parts) == parts


@pytest.mark.parametrize(
    "sporadic_qualifier", ["sporadic", "(sometimes)", "sometimes?", "occasionally?"]
)
def test_apply_sporadic_qualifier(sporadic_qualifier):
    assert apply_sporadic_qualifier({"stages": ["p", f"h {sporadic_qualifier}"]}) == {
        "stages": ["p", "h"],
        "sporadic": True,
        "comment": sporadic_qualifier,
    }


def test_apply_sporadic_qualifier_unchanged_when_no_marker():
    parts = {"stages": ["a", "e"], "env": "_#"}
    assert apply_sporadic_qualifier(parts) == parts


def test_apply_stress_conditions():
    assert apply_stress_conditions(
        {"stages": ["a", "e"], "env": "_C(C), when stressed"}
    ) == {"stages": ["a", "e"], "env": "_C(C) when stressed"}
    cleaned = apply_stress_conditions(
        {
            "stages": ["ɾ", "∅"],
            "env": "V_V, when neither vowel is stressed",
        }
    )
    assert cleaned["env"] == "V_V"
    assert "when neither vowel is stressed" in cleaned["comment"]


def test_apply_trailing_glosses():
    assert apply_trailing_glosses(
        {"stages": ["j", "p (some Polynesian languages, such as Levei and Drehet)"]}
    ) == {
        "stages": ["j", "p"],
        "comment": "(some Polynesian languages, such as Levei and Drehet)",
    }


def test_apply_trailing_glosses_strips_field_wrapped_gloss_to_comment():
    assert apply_trailing_glosses({"stages": ["hhy", '"something like /ʒ/"']}) == {
        "stages": ["hhy", ""],
        "comment": '"something like /ʒ/"',
    }


def test_apply_trailing_glosses_keeps_unclosed_paren_on_env():
    """Env/exception unclosed parens stay paired for compile-time gloss strip."""
    assert apply_trailing_glosses(
        {
            "stages": ["Vn", "ṽ"],
            "env": "_# (seems to have been reverted in most dialects",
            "exception": "for Souletin)",
        }
    ) == {
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


def test_split_field_semicolon_comment():
    assert split_field_semicolon_comment(
        "depending on the environment; again, the article is unclear"
    ) == (
        "depending on the environment",
        "again, the article is unclear",
    )
    assert split_field_semicolon_comment("short only") == ("short only", None)


def test_split_line_semicolon_comment():
    assert split_line_semicolon_comment("a → b ; tail") == ("a → b", "tail")
    assert split_line_semicolon_comment("no semicolon") == ("no semicolon", None)
