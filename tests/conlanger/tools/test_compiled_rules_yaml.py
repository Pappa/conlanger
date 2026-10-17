"""Tests for compile diagnostic ``asca_rules.yml`` (ticket 159)."""

from __future__ import annotations

from pathlib import Path

import yaml

from conlanger.compile.models.rules import SoundChangeRule
from conlanger.ingest.models.mappings import CompilerConfig
from conlanger.tools.compiled_rules_yaml import (
    COMPILED_RULES_YAML_NAME,
    _skipped_rule_line,
    build_asca_rules_document,
    compiled_rule_entry_from_rows,
    write_compiled_rules_yaml,
)
from conlanger.tools.index_inventory import (
    OK_FALSE,
    OK_SKIPPED,
    OK_TRUE,
    RULE_SKIPPED_FAILURE_CLASS,
    IndexRuleInventoryBundle,
    ValidationRow,
    _InventoryTarget,
)
from tests.conlanger.tools.test_sporadic_sampling import _RecordingRandom

_SECTION = {"index": "1.0", "section": "Test"}


def _bundle(
    rule: dict,
    rows: list[ValidationRow],
    *,
    rule_id: str = "r0",
    targets: list[_InventoryTarget] | None = None,
) -> IndexRuleInventoryBundle:
    return IndexRuleInventoryBundle(
        section=_SECTION,
        rule=rule,
        rule_id=rule_id,
        rows=rows,
        targets=targets or [_InventoryTarget(None, None, None)],
    )


def test_compiled_rule_entry_single_form():
    rows = [
        ValidationRow(
            "1",
            "A",
            "r0",
            "s:1",
            OK_TRUE,
            rule="a > b",
        )
    ]
    entry = compiled_rule_entry_from_rows(
        {"stages": ["a", "b"]},
        rows,
        section=_SECTION,
        rule_id="r0",
    )
    assert entry == {"rule_id": "r0", "valid": True, "rule": "a > b"}


def test_compiled_rule_entry_alternatives_and_steps():
    alt_rows = [
        ValidationRow("1", "A", "r0", "s:1", OK_TRUE, rule="d > ∅ / V_V", alt_idx=0),
        ValidationRow(
            "1",
            "A",
            "r0",
            "s:1",
            OK_FALSE,
            rule="d > ð / V_V",
            alt_idx=1,
            failure_class="syntax_other",
        ),
    ]
    alt_entry = compiled_rule_entry_from_rows(
        {"stages": ["d", "{∅,ð}"], "env": "V_V"},
        alt_rows,
        section=_SECTION,
        rule_id="opt",
    )
    assert alt_entry["valid"] is False
    assert alt_entry["alternatives"] == [
        {"rule": "d > ∅ / V_V", "valid": True},
        {"rule": "d > ð / V_V", "valid": False},
    ]
    assert "rule" not in alt_entry

    step_rows = [
        ValidationRow("1", "A", "c", "s:2", OK_TRUE, rule="p > t", step_idx=0),
        ValidationRow("1", "A", "c", "s:2", OK_TRUE, rule="t > k", step_idx=1),
    ]
    step_entry = compiled_rule_entry_from_rows(
        {"stages": ["p", "t", "k"]},
        step_rows,
        section=_SECTION,
        rule_id="chain",
    )
    assert step_entry["valid"] is True
    assert step_entry["steps"] == [
        {"rule": "p > t", "valid": True},
        {"rule": "t > k", "valid": True},
    ]


def test_compiled_rule_entry_skipped_rule_line():
    rule = {
        "stages": ["x", "y"],
        "raw": "x → y",
        "status": "skipped",
    }
    entry = compiled_rule_entry_from_rows(
        rule,
        [
            ValidationRow(
                "1",
                "A",
                "hold",
                "s:1",
                OK_TRUE,
                rule="",
            )
        ],
        section=_SECTION,
        rule_id="hold",
    )
    assert entry["status"] == "skipped"
    assert entry["rule"] == "#\tx → y"
    assert "valid" not in entry


def test_build_document_omits_section_skipped():
    skipped_bundle = IndexRuleInventoryBundle(
        section={
            "index": "9",
            "section": "Skipped",
            "status": "skipped",
        },
        rule={"stages": ["a", "b"], "rule_id": "x"},
        rule_id="x",
        rows=[ValidationRow("9", "S", "x", "s:0", OK_TRUE, rule="")],
        targets=[_InventoryTarget(None, None, None)],
    )
    active = _bundle(
        {"stages": ["a", "b"], "rule_id": "active"},
        [ValidationRow("1", "A", "active", "s:1", OK_TRUE, rule="a > b")],
        rule_id="active",
    )
    doc = build_asca_rules_document([skipped_bundle, active])
    assert len(doc["sections"]) == 1
    assert doc["sections"][0]["rules"][0]["rule_id"] == "active"


def test_compiled_rule_entry_format_error_from_rows_only():
    entry = compiled_rule_entry_from_rows(
        {"stages": ["a", "b"]},
        [
            ValidationRow(
                "1",
                "A",
                "bad",
                "s:1",
                OK_FALSE,
                failure_class="format_error",
                description="format_error: missing stages",
            )
        ],
        section=_SECTION,
        rule_id="bad",
    )
    assert entry["valid"] is False
    assert entry["compile_error"] == "missing stages"


def test_skipped_rule_line_compiles_active_rule_shape():
    line = _skipped_rule_line(
        _SECTION,
        {"stages": ["a", "b"], "raw": "a → b"},
        "r0",
        compiler_config=None,
    )
    assert line == "a > b"


def test_compiled_rule_entry_compile_error_and_prefix_strip():
    entry = compiled_rule_entry_from_rows(
        {"stages": ["a", "b"]},
        [],
        section=_SECTION,
        rule_id="bad",
        compile_error="format_error: input is required",
    )
    assert entry == {
        "rule_id": "bad",
        "valid": False,
        "compile_error": "input is required",
    }


def test_build_document_target_format_error():
    bundle = IndexRuleInventoryBundle(
        section=_SECTION,
        rule={"stages": ["a", "b"], "rule_id": "bad"},
        rule_id="bad",
        rows=[
            ValidationRow(
                "1",
                "A",
                "bad",
                "s:1",
                OK_FALSE,
                failure_class="format_error",
                description="format_error: no compile steps",
            )
        ],
        targets=[
            _InventoryTarget(
                None,
                None,
                None,
                format_error="format_error: no compile steps",
            )
        ],
    )
    doc = build_asca_rules_document([bundle])
    rule = doc["sections"][0]["rules"][0]
    assert rule["valid"] is False
    assert rule["compile_error"] == "no compile steps"


def test_compiled_rule_entry_hold_out_and_sporadic_skip():
    hold_out = compiled_rule_entry_from_rows(
        {"stages": ["x", "y"], "raw": "x → y", "status": "skipped"},
        [
            ValidationRow(
                "1",
                "A",
                "hold",
                "s:1",
                OK_SKIPPED,
                failure_class=RULE_SKIPPED_FAILURE_CLASS,
            )
        ],
        section=_SECTION,
        rule_id="hold",
    )
    assert hold_out == {"rule_id": "hold", "status": "skipped", "rule": "#\tx → y"}

    sporadic_rule = SoundChangeRule(
        input="p",
        output="h",
        env="V_V",
        sporadic=True,
        compiler_config=CompilerConfig(sample_sporadic=True, sample_dialect=True),
        rng=_RecordingRandom(random_values=[0.9]),
    )
    bundle = IndexRuleInventoryBundle(
        section=_SECTION,
        rule={"stages": ["p", "h"], "env": "V_V", "sporadic": True, "rule_id": "sp"},
        rule_id="sp",
        rows=[ValidationRow("1", "A", "sp", "s:2", OK_TRUE, rule="p > h / V_V")],
        targets=[_InventoryTarget(None, None, sporadic_rule)],
    )
    doc = build_asca_rules_document([bundle])
    skipped = doc["sections"][0]["rules"][0]
    assert skipped["status"] == "compile_skipped"
    assert skipped["rule"] == "#\tp > h / V_V"


def test_compiled_rule_entry_empty_rows_and_fallback_steps():
    empty = compiled_rule_entry_from_rows(
        {"stages": ["a", "b"]},
        [],
        section=_SECTION,
        rule_id="empty",
    )
    assert empty["valid"] is False
    assert empty["compile_error"] == "no validation rows"

    fallback = compiled_rule_entry_from_rows(
        {"stages": ["a", "b"]},
        [
            ValidationRow("1", "A", "m", "s:1", OK_TRUE, rule="a > b"),
            ValidationRow("1", "A", "m", "s:1", OK_FALSE, rule="b > c"),
        ],
        section=_SECTION,
        rule_id="m",
    )
    assert fallback["valid"] is False
    assert fallback["steps"] == [
        {"rule": "a > b", "valid": True},
        {"rule": "b > c", "valid": False},
    ]


def test_build_document_multiple_sections():
    other_section = {"index": "2.0", "section": "Other"}
    doc = build_asca_rules_document(
        [
            _bundle(
                {"stages": ["a", "b"], "rule_id": "r0"},
                [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, rule="a > b")],
            ),
            IndexRuleInventoryBundle(
                section=other_section,
                rule={"stages": ["c", "d"], "rule_id": "r1"},
                rule_id="r1",
                rows=[ValidationRow("2", "O", "r1", "s:2", OK_TRUE, rule="c > d")],
                targets=[_InventoryTarget(None, None, None)],
            ),
        ]
    )
    assert [section["index"] for section in doc["sections"]] == ["1.0", "2.0"]


def test_bundles_for_row_prefix_truncates_mid_rule():
    from conlanger.tools.compiled_rules_yaml import bundles_for_row_prefix

    bundles = [
        _bundle(
            {"stages": ["a", "b", "c"]},
            [
                ValidationRow("1", "A", "c", "s:1", OK_TRUE, rule="a > b", step_idx=0),
                ValidationRow("1", "A", "c", "s:1", OK_TRUE, rule="b > c", step_idx=1),
            ],
            rule_id="chain",
        )
    ]
    trimmed = bundles_for_row_prefix(bundles, bundles[0].rows[:1])
    assert len(trimmed) == 1
    assert len(trimmed[0].rows) == 1
    assert trimmed[0].rows[0].step_idx == 0
    assert bundles_for_row_prefix(bundles, []) == []


def test_write_compiled_rules_yaml_smoke(tmp_path: Path):
    doc = build_asca_rules_document(
        [
            _bundle(
                {"stages": ["a", "b"], "rule_id": "r0"},
                [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, rule="a > b")],
            )
        ]
    )
    path = tmp_path / COMPILED_RULES_YAML_NAME
    write_compiled_rules_yaml(doc, path)
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert loaded["sections"][0]["rules"][0]["rule"] == "a > b"
