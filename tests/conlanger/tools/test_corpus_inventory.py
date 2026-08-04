import csv
from pathlib import Path
from unittest.mock import patch

import pytest

from conlanger.tools.asca_validator import ASCAValidationError
from conlanger.tools.corpus_inventory import (
    ValidationRow,
    classify_error,
    iter_validation_rows,
    reason_for_failure,
    summarize_inventory,
    validate_corpus_rule,
    write_validation_csv,
)

_SECTION = {"index": "1.0", "section": "Test Section"}


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        ("", ""),
        ("nested brackets in rule", "nested_brackets"),
        ("Unknown feature foo", "unknown_feature"),
        ("Unknown grouping X", "unknown_grouping"),
        ("Expected '>' but got foo", "prose_or_expected_arrow"),
        ("Expected '_'", "expected_underscore"),
        ("after the end of a word", "stuff_after_word_bound"),
        ("prerequisite properties for diacritic", "diacritic_prereq"),
        ("Input is empty", "empty_io_panic"),
        ("Can't delete a word's only segment", "runtime_delete_only_segment"),
        ("Expected number", "expected_number"),
        ("Unknown character x", "unknown_character"),
        ("Malformed Comment: bad", "malformed_comment"),
        ("missing separator '→'", "missing_arrow"),
        ("format_error: input is required", "format_error"),
        ("Syntax Error: something else", "syntax_other"),
        ("Runtime Error: boom", "runtime_other"),
        ("the compiler panicked", "panic_other"),
        ("something entirely different", "other"),
    ],
)
def test_classify_error(error, expected):
    assert classify_error(error) == expected


@pytest.mark.parametrize(
    ("failure_class", "expected_reason"),
    [
        ("malformed_comment", "trailing-comment"),
        ("trailing-comment", "trailing-comment"),
        ("missing_arrow", "broken-syntax"),
        ("format_error", "broken-syntax"),
        ("prose_or_expected_arrow", "asca-unrepresentable"),
        ("unknown_character", "asca-unrepresentable"),
        ("valid-but-inaccurate", "valid-but-inaccurate"),
        ("syntax_other", "broken-syntax"),
        ("runtime_other", "broken-syntax"),
        ("panic_other", "broken-syntax"),
        ("other", "broken-syntax"),
        ("unknown_feature", "asca-unrepresentable"),
        ("nested_brackets", "asca-unrepresentable"),
        ("weird_unmapped_class", "other"),
    ],
)
def test_reason_for_failure(failure_class, expected_reason):
    assert reason_for_failure(failure_class, "detail") == expected_reason


def test_validation_row_as_csv_dict():
    row = ValidationRow(
        section_index="1.0",
        section_name="Test",
        rule_idx=2,
        source="sample.html:10",
        ok=False,
        failure_class="syntax_other",
        reason="broken-syntax",
        description="Syntax Error: …",
    )
    assert row.as_csv_dict() == {
        "section_index": "1.0",
        "section_name": "Test",
        "rule_idx": 2,
        "source": "sample.html:10",
        "ok": False,
        "failure_class": "syntax_other",
        "reason": "broken-syntax",
        "description": "Syntax Error: …",
    }


def test_validate_corpus_rule_skipped_parse_diagnostic():
    row = validate_corpus_rule(
        _SECTION,
        {
            "input": "",
            "output": "",
            "raw": "no arrow",
            "source": "sample.html:1",
            "skipped": "missing separator '→'",
        },
        0,
        probe_words=None,
    )
    assert row.ok is False
    assert row.failure_class == "missing_arrow"
    assert row.reason == "broken-syntax"


def test_validate_corpus_rule_format_error():
    row = validate_corpus_rule(
        _SECTION,
        {"output": "b", "raw": "→ b", "source": "sample.html:2"},
        1,
        probe_words=None,
    )
    assert row.ok is False
    assert row.failure_class == "format_error"


def test_validate_corpus_rule_held_out_comment():
    row = validate_corpus_rule(
        _SECTION,
        {
            "skip": True,
            "input": "a",
            "output": "b",
            "raw": "a → b",
            "source": "sample.html:3",
        },
        2,
        probe_words=None,
    )
    assert row.ok is True
    assert row.description == "held-out (commented rule)"


@patch("conlanger.tools.corpus_inventory.validate_asca", return_value=True)
def test_validate_corpus_rule_ok(_mock_validate):
    row = validate_corpus_rule(
        _SECTION,
        {"input": "a", "output": "b", "raw": "a → b", "source": "sample.html:4"},
        0,
        probe_words=Path("/probe.wsca"),
    )
    assert row.ok is True
    assert row.failure_class == ""


@patch(
    "conlanger.tools.corpus_inventory.validate_asca",
    side_effect=ASCAValidationError("Syntax Error: Expected '_'"),
)
def test_validate_corpus_rule_asca_failure(_mock_validate):
    row = validate_corpus_rule(
        _SECTION,
        {"input": "a", "output": "b", "env": "bad", "raw": "a → b", "source": "s:5"},
        0,
        probe_words=None,
    )
    assert row.ok is False
    assert row.failure_class == "expected_underscore"
    assert row.reason == "asca-unrepresentable"


def test_iter_validation_rows():
    doc = {
        "sections": [
            {
                "index": "1.0",
                "section": "A",
                "rules": [
                    {
                        "input": "",
                        "output": "",
                        "raw": "x",
                        "source": "s:1",
                        "skipped": "missing separator '→'",
                    }
                ],
            }
        ]
    }
    rows = list(iter_validation_rows(doc, probe_words=None))
    assert len(rows) == 1
    assert rows[0].section_name == "A"


def test_write_validation_csv(tmp_path: Path):
    rows = [
        ValidationRow(
            section_index="1.0",
            section_name="A",
            rule_idx=0,
            source="s:1",
            ok=True,
            failure_class="",
            reason="",
            description="",
        )
    ]
    out = tmp_path / "nested" / "inventory.csv"
    write_validation_csv(rows, out)
    with out.open(encoding="utf-8") as handle:
        parsed = list(csv.DictReader(handle))
    assert parsed[0]["ok"] == "True"
    assert parsed[0]["section_index"] == "1.0"


def test_summarize_inventory():
    rows = [
        ValidationRow("1", "A", 0, "s:1", True, "", "", ""),
        ValidationRow(
            "1",
            "A",
            1,
            "s:2",
            False,
            "syntax_other",
            "broken-syntax",
            "err",
        ),
        ValidationRow(
            "1",
            "A",
            2,
            "s:3",
            False,
            "syntax_other",
            "broken-syntax",
            "err",
        ),
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        asca_version="0.10.x",
    )
    assert "Rows: **3**" in text
    assert "OK: **1** (33.3%)" in text
    assert "Fail: **2** (66.7%)" in text
    assert "| 2 | `syntax_other` |" in text


def test_summarize_inventory_empty():
    text = summarize_inventory(
        [],
        source_yaml="out.yml",
        probe_words="probe.wsca",
    )
    assert "Rows: **0**" in text
    assert "OK: **0** (0.0%)" in text
