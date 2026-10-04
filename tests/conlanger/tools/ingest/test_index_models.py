"""YAML round-trip and validation for parse-time IndexRule / IndexContext."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from conlanger.tools.ingest.index_models import (
    IndexContext,
    IndexRule,
    env_exception_input_to_string,
    resolve_index_context_to_string,
)

_SAMPLED_RULES_CSV = (
    Path(__file__).resolve().parents[3] / "fixtures" / "sound_change_rules.csv"
)


def _update_model_fields(raw: str) -> dict:
    rule = IndexRule(raw=raw, source="test").build()
    out: dict = {
        "stages": rule.stages,
    }
    if rule.env is not None:
        out["env"] = rule.env.model_dump(mode="python")
    if rule.exception is not None:
        out["exception"] = rule.exception.model_dump(mode="python")
    if rule.comment is not None:
        out["comment"] = rule.comment
    return out


def _load_sampled_html_rules() -> list[tuple]:
    df = pd.read_csv(_SAMPLED_RULES_CSV, dtype=str, keep_default_na=False)
    if "kind" in df.columns:
        df = df[df["kind"].isin(["", "html_extract"])]
    cases: list[tuple] = []
    for row in df.itertuples(index=False):
        if row.expect_none == "True":
            expected = None
        else:
            expected = _update_model_fields(row.raw)
        cases.append((row.id, row.raw, expected))
    return cases


@pytest.mark.parametrize(
    "yaml_doc, expected",
    [
        pytest.param(
            """
env:
  context: "#_"
  position:
    adjacent_to: C
  dialect: northern
""",
            {
                "context": "#_",
                "position": {"adjacent_to": "C"},
                "dialect": "northern",
            },
            id="context_position_dialect_scalar",
        ),
        pytest.param(
            """
env:
  position:
    adjacent_to:
      - N
      - V
    medial: true
  dialect:
    - west
    - gascon
""",
            {
                "position": {"adjacent_to": ["N", "V"], "medial": True},
                "dialect": ["west", "gascon"],
            },
            id="position_lists_and_dialect_list",
        ),
        pytest.param(
            """
env:
  dialect: true
""",
            {
                "dialect": True,
            },
            id="dialect_bool",
        ),
    ],
)
def test_index_context_yaml_round_trip(yaml_doc, expected):
    loaded = yaml.safe_load(yaml_doc)
    ctx = IndexContext.model_validate(loaded["env"])
    assert ctx.model_dump(exclude_none=True) == expected
    round_trip = yaml.safe_load(
        yaml.safe_dump({"env": ctx.model_dump(exclude_none=True)})
    )
    assert round_trip["env"] == expected


def test_index_context_with_dialects_extracted_bare_dialectal():
    ctx = IndexContext(context="dialectal").with_dialects_extracted()
    assert ctx == IndexContext(dialect=True)
    assert ctx.model_dump(exclude_none=True, mode="python") == {"dialect": True}


def test_index_context_with_dialects_extracted_preserves_position():
    ctx = IndexContext(
        context="in northern dialects",
        position={"adjacent_to": "C"},
    ).with_dialects_extracted()
    assert ctx == IndexContext(
        position={"adjacent_to": "C"},
        dialect="northern",
    )


def test_index_rule_string_env_round_trip():
    rule = IndexRule(
        stages=["a", "b"],
        env="_#",
        raw="a → b / _#",
        source="index.html:1",
    )
    dumped = rule.to_index_dict()
    assert dumped == {
        "stages": ["a", "b"],
        "env": "_#",
        "raw": "a → b / _#",
        "source": "index.html:1",
    }
    restored = IndexRule.model_validate(dumped)
    assert restored.env == IndexContext(context="_#")
    assert restored == rule


def test_index_rule_structured_env_to_index_dict():
    rule = IndexRule(
        stages=["x", "y"],
        env=IndexContext(
            context="#_",
            position={"adjacent_to": "C"},
            dialect="northern",
        ),
        raw="x → y",
        source="index.html:2",
        sporadic=True,
        rule_id="Test-id",
    )
    dumped = rule.to_index_dict()
    assert dumped["env"] == {
        "context": "#_",
        "position": {"adjacent_to": "C"},
        "dialect": "northern",
    }
    assert dumped["sporadic"] is True
    assert dumped["rule_id"] == "Test-id"
    assert IndexRule.model_validate(dumped) == rule


def test_index_rule_working_text_initialised_from_raw():
    rule = IndexRule(raw="a → b", source="index.html:1")
    assert rule.text == "a → b"


def test_index_rule_update_rule_replaces_working_text_not_raw():
    rule = IndexRule(raw="original", source="index.html:1")
    rule.text = "a → b"
    assert rule.text == "a → b"
    assert rule.raw == "original"


def test_build_peels_first_semicolon_comment():
    rule = IndexRule(raw="a → b ; tail", source="test").build()
    assert rule.stages == ["a", "b"]
    assert rule.comment == "tail"


def test_build_semicolon_peel_no_comment_when_absent():
    rule = IndexRule(raw="no semicolon", source="test").build()
    assert rule.comment is None
    assert rule.stages == ["no semicolon"]


def test_build_strips_leading_list_marker():
    rule = IndexRule(raw="— j w → i u / #_CV", source="test").build()
    assert rule.stages == ["j w", "i u"]
    assert rule.env == IndexContext(context="#_CV")


def test_build_splits_chain_into_stages():
    rule = IndexRule(raw="dʒ → tʃ → ʃ", source="test").build()
    assert rule.stages == ["dʒ", "tʃ", "ʃ"]


def test_build_applies_symbol_normalization():
    raw = "a → b / _$%oː"
    rule = IndexRule(raw=raw, source="test").build()
    assert rule.stages == ["a", "b"]
    assert rule.env == IndexContext(context="_$$oː")


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            "w → ∅ / _# ! k(ː)_",
            {"stages": ["w", "∅"], "env": "_#", "exception": "k(ː)_"},
        ),
        (
            "s → ʃ / !V_",
            {"stages": ["s", "ʃ"], "exception": "V_"},
        ),
        ("ɬ → l", {"stages": ["ɬ", "l"]}),
        ("no arrow here", {"stages": ["no arrow here"]}),
        (
            "ʔ → ∅/ _#",
            {"stages": ["ʔ", "∅"], "env": "_#"},
        ),
        (
            "{i,u} → ∅/ _# ! V[-long]C_#",
            {
                "stages": ["{i,u}", "∅"],
                "env": "_#",
                "exception": "V[-long]C_#",
            },
        ),
        (
            "ə → ∅ VC_CV",
            {"stages": ["ə", "∅ VC_CV"]},
        ),
        (
            "χ → h #_",
            {"stages": ["χ", "h #_"]},
        ),
        (
            "∅ → dz → î_V",
            {"stages": ["∅", "dz", "î_V"]},
        ),
        (
            "rt → š (Alex Fink says that the realization of /š/ “is unclear”)",
            {
                "stages": [
                    "rt",
                    "š (Alex Fink says that the realization of /š/ “is unclear”)",
                ]
            },
        ),
        ("r…r → r…∅", {"stages": ["r…r", "r…∅"]}),
    ],
)
def test_build_structural_split(raw, expected):
    assert _update_model_fields(raw) == expected


_SAMPLED_HTML_RULE_CASES = _load_sampled_html_rules()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param(raw, expected, id=case_id)
        for case_id, raw, expected in _SAMPLED_HTML_RULE_CASES
    ],
)
def test_build_sampled_html_rules(raw, expected):
    assert _update_model_fields(raw) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        pytest.param("_#", "_#", id="passthrough"),
        pytest.param(IndexContext(context="_#"), "_#", id="index_context"),
    ],
)
def test_env_exception_input_to_string(input, expected):
    assert env_exception_input_to_string(input) == expected


@pytest.mark.parametrize(
    "ctx, expected",
    [
        pytest.param(
            IndexContext(position={"adjacent_to": "C"}),
            "C_, _C",
            id="adjacent_to_single_char",
        ),
        pytest.param(
            IndexContext(position={"adjacent_to": ["C"]}),
            "C_, _C",
            id="adjacent_to_single_char_list",
        ),
        pytest.param(IndexContext(position={"medial": True}), "", id="medial"),
        pytest.param(
            IndexContext(context="#_", position={"adjacent_to": "C"}),
            "#_",
            id="uses_context_string",
        ),
        # TODO: handle multi-char adjacent_to if it appears in the index
        pytest.param(
            IndexContext(position={"adjacent_to": "CV"}),
            "",
            id="ignores_multi_char_adjacent_to",
        ),
    ],
)
def test_resolve_index_context(ctx, expected):
    assert resolve_index_context_to_string(ctx) == expected
