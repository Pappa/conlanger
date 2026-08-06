import csv
from pathlib import Path
from unittest.mock import patch

import pytest

from conlanger.tools.asca_validator import ASCAValidationError
from conlanger.tools.corpus_inventory import (
    CHANGELOG_CSV_COLUMNS,
    ValidationRow,
    classify_error,
    filter_inventory_by_ok,
    iter_validation_rows,
    ok_flip_changelog_rows,
    parse_unknown_token_error,
    reason_for_failure,
    section_all_ok_stats,
    section_all_ok_stats_from_dataframe,
    summarize_inventory,
    top_error_tokens,
    top_error_tokens_with_suggested_from_dataframe,
    validate_corpus_rule,
    validation_rows_to_dataframe,
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
    ("error", "expected_token", "expected_suggested"),
    [
        ("", "", ""),
        (
            "Syntax Error: Unknown character '₁' | dz ʃ tʃ > ʒ s₁ s₂",
            "₁",
            "",
        ),
        (
            "Syntax Error: Unknown grouping 'Z'. Known groupings are (C)onsonant",
            "Z",
            "",
        ),
        (
            "Syntax Error: Unknown feature 'voiced'. Did you mean voice? | e > i",
            "voiced",
            "voice",
        ),
        (
            "Syntax Error: Expected '_'",
            "",
            "",
        ),
    ],
)
def test_parse_unknown_token_error(error, expected_token, expected_suggested):
    assert parse_unknown_token_error(error) == (
        expected_token,
        expected_suggested,
    )


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
        error_token="",
        suggested="",
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
        "error_token": "",
        "suggested": "",
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
    assert row.error_token == ""
    assert row.suggested == ""


@patch(
    "conlanger.tools.corpus_inventory.validate_asca",
    side_effect=ASCAValidationError(
        "Syntax Error: Unknown feature 'voiced'. Did you mean voice? | e > i"
    ),
)
def test_validate_corpus_rule_unknown_token_fields(_mock_validate):
    row = validate_corpus_rule(
        _SECTION,
        {
            "input": "e",
            "output": "i",
            "env": "#l_{P,C[+voiced]}",
            "raw": "e → i",
            "source": "s:6",
        },
        0,
        probe_words=None,
    )
    assert row.failure_class == "unknown_feature"
    assert row.error_token == "voiced"
    assert row.suggested == "voice"


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
            error_token="",
            suggested="",
            description="",
        ),
        ValidationRow(
            section_index="1.0",
            section_name="A",
            rule_idx=1,
            source="s:2",
            ok=False,
            failure_class="unknown_feature",
            reason="asca-unrepresentable",
            error_token="voiced",
            suggested="voice",
            description="Syntax Error: Unknown feature 'voiced'. Did you mean voice?",
        ),
    ]
    out = tmp_path / "nested" / "inventory.csv"
    write_validation_csv(rows, out)
    with out.open(encoding="utf-8") as handle:
        parsed = list(csv.DictReader(handle))
    assert parsed[0]["ok"] == "True"
    assert parsed[0]["section_index"] == "1.0"
    assert parsed[1]["error_token"] == "voiced"
    assert parsed[1]["suggested"] == "voice"
    assert list(parsed[0].keys())[-1] == "description"


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


def test_top_error_tokens():
    rows = [
        ValidationRow(
            "1",
            "A",
            0,
            "s:1",
            False,
            "unknown_character",
            "asca-unrepresentable",
            "→",
            "",
            "err",
        ),
        ValidationRow(
            "1",
            "A",
            1,
            "s:2",
            False,
            "unknown_character",
            "asca-unrepresentable",
            "→",
            "",
            "err",
        ),
        ValidationRow(
            "1",
            "A",
            2,
            "s:3",
            False,
            "unknown_character",
            "asca-unrepresentable",
            "ː",
            "",
            "err",
        ),
        ValidationRow(
            "1",
            "A",
            3,
            "s:4",
            False,
            "unknown_feature",
            "asca-unrepresentable",
            "voiced",
            "voice",
            "err",
        ),
        ValidationRow(
            "1",
            "A",
            4,
            "s:5",
            False,
            "unknown_feature",
            "asca-unrepresentable",
            "voiced",
            "voice",
            "err",
        ),
        ValidationRow(
            "1",
            "A",
            5,
            "s:6",
            False,
            "unknown_feature",
            "asca-unrepresentable",
            "sibilant",
            "sonorant",
            "err",
        ),
    ]
    assert top_error_tokens(rows, "unknown_character") == [("→", 2), ("ː", 1)]
    assert top_error_tokens(rows, "unknown_feature") == [("voiced", 2), ("sibilant", 1)]
    assert top_error_tokens(rows, "unknown_grouping") == []


def test_top_error_tokens_with_suggested_from_dataframe():
    df = validation_rows_to_dataframe(
        [
            ValidationRow(
                "1",
                "A",
                0,
                "s:1",
                False,
                "unknown_feature",
                "asca-unrepresentable",
                "voiced",
                "voice",
                "err",
            ),
            ValidationRow(
                "1",
                "A",
                1,
                "s:2",
                False,
                "unknown_feature",
                "asca-unrepresentable",
                "voiced",
                "voice",
                "err",
            ),
            ValidationRow(
                "1",
                "A",
                2,
                "s:3",
                False,
                "unknown_feature",
                "asca-unrepresentable",
                "sibilant",
                "sonorant",
                "err",
            ),
        ]
    )
    assert top_error_tokens_with_suggested_from_dataframe(df, "unknown_feature") == [
        ("voiced", 2, "voice"),
        ("sibilant", 1, "sonorant"),
    ]


def test_top_error_tokens_unlimited():
    rows = [
        ValidationRow(
            "1",
            "A",
            i,
            f"s:{i}",
            False,
            "unknown_grouping",
            "asca-unrepresentable",
            token,
            "",
            "err",
        )
        for i, token in enumerate(("R", "E", "U", "H", "B", "X"))
    ]
    assert top_error_tokens(rows, "unknown_grouping", limit=5) == [
        ("R", 1),
        ("E", 1),
        ("U", 1),
        ("H", 1),
        ("B", 1),
    ]
    assert len(top_error_tokens(rows, "unknown_grouping", limit=None)) == 6


def test_section_all_ok_stats():
    rows = [
        ValidationRow("1", "A", 0, "s:1", True, "", "", "", "", ""),
        ValidationRow("1", "A", 1, "s:2", True, "", "", "", "", ""),
        ValidationRow("2", "B", 0, "s:3", True, "", "", "", "", ""),
        ValidationRow(
            "2", "B", 1, "s:4", False, "syntax_other", "broken-syntax", "", "", ""
        ),
        ValidationRow(
            "3", "C", 0, "s:5", False, "syntax_other", "broken-syntax", "", "", ""
        ),
    ]
    assert section_all_ok_stats(rows) == (1, 3, 100.0 / 3)


def test_section_all_ok_stats_empty():
    assert section_all_ok_stats([]) == (0, 0, 0.0)


def test_section_all_ok_stats_from_dataframe():
    rows = [
        ValidationRow("1", "A", 0, "s:1", True, "", "", "", "", ""),
        ValidationRow("1", "A", 1, "s:2", True, "", "", "", "", ""),
        ValidationRow("2", "B", 0, "s:3", True, "", "", "", "", ""),
        ValidationRow(
            "2", "B", 1, "s:4", False, "syntax_other", "broken-syntax", "", "", ""
        ),
    ]
    df = validation_rows_to_dataframe(rows)
    assert section_all_ok_stats_from_dataframe(df) == (1, 2, 50.0)


def test_summarize_inventory_common_errors():
    rows = [
        ValidationRow(
            "1",
            "A",
            0,
            "s:1",
            False,
            "unknown_character",
            "asca-unrepresentable",
            "→",
            "",
            "err",
        ),
        ValidationRow(
            "1",
            "A",
            1,
            "s:2",
            False,
            "unknown_feature",
            "asca-unrepresentable",
            "voiced",
            "voice",
            "err",
        ),
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
    )
    assert "## Common Errors" in text
    assert "### unknown_character" in text
    assert "| 1 | `→` |" in text
    assert "### unknown_feature" in text
    assert "| 1 | `voiced` | `voice` |" in text
    assert "### unknown_grouping" in text
    assert "| — | _(none)_ |" in text
    assert text.index("## Failure classes") < text.index("## Common Errors")
    assert text.index("## Common Errors") < text.index("## Notes")


def test_summarize_inventory():
    rows = [
        ValidationRow("1", "A", 0, "s:1", True, "", "", "", "", ""),
        ValidationRow(
            "1",
            "A",
            1,
            "s:2",
            False,
            "syntax_other",
            "broken-syntax",
            "",
            "",
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
            "",
            "",
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
    assert "Sections all OK: **0 / 1** (0.0%)" in text
    assert "| 2 | `syntax_other` |" in text
    assert "## Common Errors" in text
    assert "asca-rule-inventory.csv" in text
    assert "asca-rule-inventory-success.csv" in text
    assert "asca-rule-inventory-error.csv" in text
    assert "asca-rule-inventory-changelog.csv" in text


def test_summarize_inventory_empty():
    text = summarize_inventory(
        [],
        source_yaml="out.yml",
        probe_words="probe.wsca",
    )
    assert "Rows: **0**" in text
    assert "OK: **0** (0.0%)" in text
    assert "Sections all OK: **0 / 0** (0.0%)" in text
    assert "### unknown_character" in text
    assert "| — | _(none)_ |" in text


def test_filter_inventory_by_ok_splits_success_and_error():
    rows = [
        ValidationRow("1", "A", 0, "file:1", True, "", "", "", "", ""),
        ValidationRow(
            "1",
            "A",
            1,
            "file:2",
            False,
            "syntax_other",
            "broken-syntax",
            "",
            "",
            "err",
        ),
        ValidationRow("1", "A", 2, "file:3", True, "", "", "", "", ""),
    ]
    df = validation_rows_to_dataframe(rows)
    success = filter_inventory_by_ok(df, ok=True)
    error = filter_inventory_by_ok(df, ok=False)
    assert list(success["source"]) == ["file:1", "file:3"]
    assert list(error["source"]) == ["file:2"]
    assert list(success.columns) == list(df.columns)
    assert list(error.columns) == list(df.columns)


def test_ok_flip_changelog_rows_emits_flips_by_source():
    previous = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", 0, "file:1", True, "", "", "", "", ""),
            ValidationRow(
                "1",
                "A",
                1,
                "file:2",
                False,
                "syntax_other",
                "broken-syntax",
                "",
                "",
                "err",
            ),
            ValidationRow("1", "A", 2, "file:3", True, "", "", "", "", ""),
        ]
    )
    # rule_idx renumbered; file:3 ok unchanged; file:1 and file:2 flip
    current = validation_rows_to_dataframe(
        [
            ValidationRow(
                "1",
                "A",
                5,
                "file:1",
                False,
                "syntax_other",
                "broken-syntax",
                "",
                "",
                "err",
            ),
            ValidationRow("1", "A", 6, "file:2", True, "", "", "", "", ""),
            ValidationRow("1", "A", 7, "file:3", True, "", "", "", "", ""),
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-06T12:00:00Z")
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS
    assert list(flips["source"]) == ["file:1", "file:2"]
    assert list(flips["ok"]) == [False, True]
    assert list(flips["rule_idx"]) == [5, 6]
    assert list(flips["timestamp"]) == [
        "2026-08-06T12:00:00Z",
        "2026-08-06T12:00:00Z",
    ]


def test_ok_flip_changelog_rows_empty_when_ok_unchanged():
    df = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", 0, "file:1", True, "", "", "", "", ""),
            ValidationRow(
                "1",
                "A",
                1,
                "file:2",
                False,
                "syntax_other",
                "broken-syntax",
                "",
                "",
                "err",
            ),
        ]
    )
    flips = ok_flip_changelog_rows(df, df, timestamp="2026-08-06T12:00:00Z")
    assert flips.empty
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS


def test_ok_flip_changelog_rows_empty_without_previous_inventory():
    current = validation_rows_to_dataframe(
        [ValidationRow("1", "A", 0, "file:1", True, "", "", "", "", "")]
    )
    flips = ok_flip_changelog_rows(None, current, timestamp="2026-08-06T12:00:00Z")
    assert flips.empty
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS
