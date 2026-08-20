import csv
from pathlib import Path
from unittest.mock import patch

import pytest

from conlanger.appliers.asca import ASCAValidationError
from conlanger.tools.corpus_inventory import (
    CHANGELOG_CSV_COLUMNS,
    SECTION_SKIPPED_FAILURE_CLASS,
    FieldIsolationRow,
    ValidationRow,
    append_ok_flip_changelog,
    build_field_isolation_row,
    classify_error,
    derive_blame,
    field_isolation_rows_for_validation_rows,
    field_isolation_rows_to_dataframe,
    filter_field_isolation_error,
    filter_field_isolation_success,
    filter_inventory_by_ok,
    iter_validation_rows,
    load_inventory_csv,
    ok_flip_changelog_rows,
    parse_unknown_token_error,
    reason_for_failure,
    section_all_ok_stats,
    section_all_ok_stats_from_dataframe,
    summarize_inventory,
    top_error_tokens,
    top_error_tokens_with_suggested_from_dataframe,
    validate_corpus_rule,
    validate_corpus_rule_with_targets,
    validation_rows_to_dataframe,
    write_field_isolation_csvs,
    write_filtered_inventory_csvs,
    write_validation_csv,
)
from conlanger.tools.rules import SoundChangeRule
from tests.conftest import ASCA_VALIDATE_INSTALLED

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
        rule_id="Test-2",
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
        "rule_id": "Test-2",
        "alt_idx": "",
        "source": "sample.html:10",
        "ok": False,
        "failure_class": "syntax_other",
        "reason": "broken-syntax",
        "error_token": "",
        "suggested": "",
        "description": "Syntax Error: …",
    }


def test_validate_corpus_rule_skipped_section():
    section = {"index": "9.9.9", "section": "Skipped", "skipped": True}
    with patch("conlanger.tools.corpus_inventory.DiachronicSeries") as mock_series:
        (row,) = validate_corpus_rule(
            section,
            {"stages": ["a", "b"], "raw": "a → b", "source": "sample.html:1"},
            "r0",
            probe_words=None,
        )
    mock_series.assert_not_called()
    assert row.ok is True
    assert row.failure_class == SECTION_SKIPPED_FAILURE_CLASS


def test_validate_corpus_rule_skipped_quoted_prose_uses_comment():
    (row,) = validate_corpus_rule(
        _SECTION,
        {
            "stages": [],
            "status": "skipped",
            "comment": "quoted prose paragraph",
            "raw": "hhy → gloss",
            "source": "sample.html:9",
        },
        "r0",
        probe_words=None,
    )
    assert row.ok is False
    assert row.failure_class == "missing_arrow"
    assert row.description == "quoted prose paragraph"


def test_validate_corpus_rule_skipped_parse_diagnostic():
    (row,) = validate_corpus_rule(
        _SECTION,
        {
            "stages": [],
            "raw": "no arrow",
            "source": "sample.html:1",
            "status": "skipped",
        },
        "r0",
        probe_words=None,
    )
    assert row.ok is False
    assert row.failure_class == "missing_arrow"
    assert row.reason == "broken-syntax"


@patch(
    "conlanger.tools.corpus_inventory.DiachronicSeries",
    side_effect=ValueError("bad compile"),
)
def test_validate_corpus_rule_diachronic_compile_format_error(_mock_prs):
    (row,) = validate_corpus_rule(
        _SECTION,
        {"stages": ["a", "b"], "raw": "a → b", "source": "sample.html:8"},
        "r0",
        probe_words=None,
    )
    assert row.ok is False
    assert row.failure_class == "format_error"
    assert "bad compile" in row.description


def test_validate_corpus_rule_format_error_no_compile_steps():
    (row,) = validate_corpus_rule(
        _SECTION,
        {"stages": ["a"], "raw": "a →", "source": "sample.html:7"},
        "r0",
        probe_words=None,
    )
    assert row.ok is False
    assert row.failure_class == "format_error"
    assert "no compile steps" in row.description


def test_validate_corpus_rule_format_error():
    (row,) = validate_corpus_rule(
        _SECTION,
        {"output": "b", "raw": "→ b", "source": "sample.html:2"},
        "r1",
        probe_words=None,
    )
    assert row.ok is False
    assert row.failure_class == "format_error"


def test_validate_corpus_rule_held_out_comment():
    (row,) = validate_corpus_rule(
        _SECTION,
        {
            "skip": True,
            "stages": ["a", "b"],
            "raw": "a → b",
            "source": "sample.html:3",
        },
        "r2",
        probe_words=None,
    )
    assert row.ok is True
    assert row.description == "held-out (commented rule)"


@patch("conlanger.tools.corpus_inventory.validate_asca", return_value=True)
def test_validate_corpus_rule_ok(_mock_validate):
    (row,) = validate_corpus_rule(
        _SECTION,
        {"stages": ["a", "b"], "raw": "a → b", "source": "sample.html:4"},
        "r0",
        probe_words=Path("/probe.wsca"),
    )
    assert row.ok is True
    assert row.failure_class == ""


@patch(
    "conlanger.tools.corpus_inventory.validate_asca",
    side_effect=ASCAValidationError("Syntax Error: Expected '_'"),
)
def test_validate_corpus_rule_asca_failure(_mock_validate):
    (row,) = validate_corpus_rule(
        _SECTION,
        {"stages": ["a", "b"], "env": "bad", "raw": "a → b", "source": "s:5"},
        "r0",
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
    (row,) = validate_corpus_rule(
        _SECTION,
        {
            "stages": ["e", "i"],
            "env": "#l_{P,C[+voiced]}",
            "raw": "e → i",
            "source": "s:6",
        },
        "r0",
        probe_words=None,
    )
    assert row.failure_class == "unknown_feature"
    assert row.error_token == "voiced"
    assert row.suggested == "voice"


@patch("conlanger.tools.corpus_inventory.validate_asca", return_value=True)
def test_validate_corpus_rule_emits_alternative_rows(_mock_validate):
    rows = validate_corpus_rule(
        _SECTION,
        {
            "stages": ["d", "{∅,ð}"],
            "env": "V_V",
            "raw": "d → {∅,ð} / V_V",
            "source": "s:1",
        },
        "r0",
        probe_words=None,
    )
    assert [row.alt_idx for row in rows] == [0, 1]
    assert all(row.ok for row in rows)
    assert all(row.source == "s:1" for row in rows)
    assert _mock_validate.call_count == 2


@patch("conlanger.tools.corpus_inventory.validate_asca", return_value=True)
def test_validate_corpus_rule_non_optional_has_empty_alt_idx(_mock_validate):
    (row,) = validate_corpus_rule(
        _SECTION,
        {"stages": ["a", "b"], "raw": "a → b", "source": "s:1"},
        "r0",
        probe_words=None,
    )
    assert row.alt_idx is None


def test_ok_flip_changelog_rows_keys_on_source_and_alt_idx():
    previous = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "file:1", True, "", "", "", "", "", 0),
            ValidationRow("1", "A", "r0", "file:1", True, "", "", "", "", "", 1),
        ]
    )
    # alt_idx 0 unchanged; alt_idx 1 flips to failing under the same source
    current = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "file:1", True, "", "", "", "", "", 0),
            ValidationRow(
                "1",
                "A",
                0,
                "file:1",
                False,
                "syntax_other",
                "broken-syntax",
                "",
                "",
                "err",
                1,
            ),
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-12T00:00:00Z")
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS
    assert list(flips["source"]) == ["file:1"]
    assert list(flips["alt_idx"]) == ["1"]
    assert list(flips["ok"]) == [False]


def test_write_validation_csv(tmp_path: Path):
    rows = [
        ValidationRow(
            section_index="1.0",
            section_name="A",
            rule_id="r0",
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
            rule_id="r1",
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
                        "stages": ["", ""],
                        "raw": "x",
                        "source": "s:1",
                        "status": "skipped",
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
        ValidationRow("1", "A", "r0", "s:1", True, "", "", "", "", ""),
        ValidationRow("1", "A", "r1", "s:2", True, "", "", "", "", ""),
        ValidationRow("2", "B", "r0", "s:3", True, "", "", "", "", ""),
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
        ValidationRow("1", "A", "r0", "s:1", True, "", "", "", "", ""),
        ValidationRow("1", "A", "r1", "s:2", True, "", "", "", "", ""),
        ValidationRow("2", "B", "r0", "s:3", True, "", "", "", "", ""),
        ValidationRow(
            "2", "B", 1, "s:4", False, "syntax_other", "broken-syntax", "", "", ""
        ),
    ]
    df = validation_rows_to_dataframe(rows)
    assert section_all_ok_stats_from_dataframe(df) == (1, 2, 50.0)


def test_section_all_ok_stats_from_dataframe_empty():
    import pandas as pd

    empty = pd.DataFrame(columns=validation_rows_to_dataframe([]).columns)
    assert section_all_ok_stats_from_dataframe(empty) == (0, 0, 0.0)


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
        ValidationRow("1", "A", "r0", "s:1", True, "", "", "", "", ""),
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
    assert "Skipped: **0** (0.0%)" in text
    assert "Sections all OK: **0 / 1** (0.0%)" in text
    assert "Sections skipped: **0 / 1** (0.0%)" in text
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
    assert "Skipped: **0** (0.0%)" in text
    assert "Sections all OK: **0 / 0** (0.0%)" in text
    assert "Sections skipped: **0 / 0** (0.0%)" in text
    assert "### unknown_character" in text
    assert "| — | _(none)_ |" in text


def test_summarize_inventory_section_skipped():
    rows = [
        ValidationRow(
            "9.9.9",
            "Skipped",
            "r0",
            "s:1",
            True,
            SECTION_SKIPPED_FAILURE_CLASS,
            "",
            "",
            "",
            "section skipped",
        ),
        ValidationRow("1", "A", "r0", "s:2", True, "", "", "", "", ""),
        ValidationRow(
            "1",
            "A",
            1,
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
    )
    assert "Rows: **3**" in text
    assert "OK: **1** (33.3%)" in text
    assert "Fail: **1** (33.3%)" in text
    assert "Skipped: **1** (33.3%)" in text
    assert "Sections all OK: **0 / 1** (0.0%)" in text
    assert "Sections skipped: **1 / 2** (50.0%)" in text


def test_filter_inventory_by_ok_splits_success_and_error():
    rows = [
        ValidationRow("1", "A", "r0", "file:1", True, "", "", "", "", ""),
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
        ValidationRow("1", "A", "r2", "file:3", True, "", "", "", "", ""),
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
            ValidationRow("1", "A", "r0", "file:1", True, "", "", "", "", ""),
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
            ValidationRow("1", "A", "r2", "file:3", True, "", "", "", "", ""),
        ]
    )
    # rule_id changed; file:3 ok unchanged; file:1 and file:2 flip
    current = validation_rows_to_dataframe(
        [
            ValidationRow(
                "1",
                "A",
                "r5",
                "file:1",
                False,
                "syntax_other",
                "broken-syntax",
                "",
                "",
                "err",
            ),
            ValidationRow("1", "A", "r6", "file:2", True, "", "", "", "", ""),
            ValidationRow("1", "A", "r7", "file:3", True, "", "", "", "", ""),
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-06T12:00:00Z")
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS
    assert list(flips["source"]) == ["file:1", "file:2"]
    assert list(flips["ok"]) == [False, True]
    assert list(flips["rule_id"]) == ["r5", "r6"]
    assert list(flips["timestamp"]) == [
        "2026-08-06T12:00:00Z",
        "2026-08-06T12:00:00Z",
    ]


def test_ok_flip_changelog_rows_tolerates_previous_without_alt_idx():
    # Inventories written before ticket 66 have no ``alt_idx`` column.
    previous = validation_rows_to_dataframe(
        [ValidationRow("1", "A", "r0", "file:1", True, "", "", "", "", "")]
    ).drop(columns=["alt_idx"])
    current = validation_rows_to_dataframe(
        [
            ValidationRow(
                "1",
                "A",
                0,
                "file:1",
                False,
                "syntax_other",
                "broken-syntax",
                "",
                "",
                "err",
            )
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-12T00:00:00Z")
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS
    assert list(flips["source"]) == ["file:1"]
    assert list(flips["ok"]) == [False]


def test_ok_flip_changelog_rows_empty_when_ok_unchanged():
    df = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "file:1", True, "", "", "", "", ""),
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
        [ValidationRow("1", "A", "r0", "file:1", True, "", "", "", "", "")]
    )
    flips = ok_flip_changelog_rows(None, current, timestamp="2026-08-06T12:00:00Z")
    assert flips.empty
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS


def test_load_inventory_csv_returns_none_when_missing(tmp_path: Path):
    assert load_inventory_csv(tmp_path / "missing.csv") is None


def test_load_inventory_csv_reads_existing_file(tmp_path: Path):
    path = tmp_path / "inventory.csv"
    write_validation_csv(
        [
            ValidationRow("1", "A", "r0", "s:1", True, "", "", "", "", ""),
        ],
        path,
    )
    loaded = load_inventory_csv(path)
    assert loaded is not None
    assert len(loaded) == 1


def test_write_filtered_inventory_csvs(tmp_path: Path):
    df = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "s:1", True, "", "", "", "", ""),
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
        ]
    )
    write_filtered_inventory_csvs(df, tmp_path)
    success = tmp_path / "asca-rule-inventory-success.csv"
    error = tmp_path / "asca-rule-inventory-error.csv"
    assert success.is_file()
    assert error.is_file()


def test_append_ok_flip_changelog_writes_and_appends(tmp_path: Path):
    flips = ok_flip_changelog_rows(
        None,
        validation_rows_to_dataframe(
            [ValidationRow("1", "A", "r0", "s:1", True, "", "", "", "", "")]
        ),
        timestamp="2026-08-06T12:00:00Z",
    )
    path = tmp_path / "changelog.csv"
    assert append_ok_flip_changelog(flips, path) == 0

    flips = ok_flip_changelog_rows(
        validation_rows_to_dataframe(
            [ValidationRow("1", "A", "r0", "s:1", True, "", "", "", "", "")]
        ),
        validation_rows_to_dataframe(
            [
                ValidationRow(
                    "1",
                    "A",
                    0,
                    "s:1",
                    False,
                    "syntax_other",
                    "broken-syntax",
                    "",
                    "",
                    "err",
                )
            ],
        ),
        timestamp="2026-08-06T13:00:00Z",
    )
    assert append_ok_flip_changelog(flips, path) == 1


def test_filter_inventory_by_ok_empty_dataframe():
    import pandas as pd

    empty = pd.DataFrame(columns=validation_rows_to_dataframe([]).columns)
    assert filter_inventory_by_ok(empty, ok=True).empty


@pytest.mark.parametrize(
    (
        "whole_ok",
        "input_ok",
        "output_ok",
        "env_ok",
        "exception_ok",
        "expected",
    ),
    [
        (True, True, True, True, True, "none"),
        (True, False, True, None, None, "input"),
        (False, False, True, None, None, "input"),
        (False, True, False, None, None, "output"),
        (False, True, True, False, None, "env"),
        (False, True, True, None, False, "exception"),
        (False, False, False, False, False, "input|output|env|exception"),
        (False, False, True, False, None, "input|env"),
        (False, True, True, True, True, "multi"),
        (False, None, None, None, None, "multi"),
    ],
)
def test_derive_blame(
    whole_ok,
    input_ok,
    output_ok,
    env_ok,
    exception_ok,
    expected,
):
    assert (
        derive_blame(
            whole_ok,
            input_ok=input_ok,
            output_ok=output_ok,
            env_ok=env_ok,
            exception_ok=exception_ok,
        )
        == expected
    )


def test_filter_field_isolation_splits_success_and_error():
    rows = [
        FieldIsolationRow(
            "1",
            "A",
            "r0",
            "s:1",
            True,
            True,
            True,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "none",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r1",
            "s:2",
            False,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r2",
            "s:3",
            True,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
        FieldIsolationRow(
            "9",
            "Skipped",
            "r3",
            "s:4",
            True,
            None,
            None,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "none",
            failure_class=SECTION_SKIPPED_FAILURE_CLASS,
        ),
    ]
    df = field_isolation_rows_to_dataframe(rows)
    success = filter_field_isolation_success(df)
    error = filter_field_isolation_error(df)
    assert list(success["source"]) == ["s:1"]
    assert set(error["source"]) == {"s:2", "s:3"}
    assert "s:4" not in set(success["source"]) | set(error["source"])
    assert list(success.columns) == list(df.columns)


def test_build_field_isolation_row_without_field_rule():
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        False,
        "format_error",
        "broken-syntax",
        "",
        "",
        "bad",
    )
    row = build_field_isolation_row(validation_row, None)
    assert row.whole_ok is False
    assert row.input_ok is None
    assert row.blame == "multi"


def test_write_field_isolation_csvs_default_fails_only(tmp_path: Path):
    rows = [
        FieldIsolationRow(
            "1",
            "A",
            "r0",
            "s:1",
            True,
            True,
            True,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "none",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r1",
            "s:2",
            False,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
    ]
    write_field_isolation_csvs(rows, tmp_path)
    main = list(csv.DictReader((tmp_path / "asca-field-isolation.csv").open()))
    success = list(
        csv.DictReader((tmp_path / "asca-field-isolation-success.csv").open())
    )
    error = list(csv.DictReader((tmp_path / "asca-field-isolation-error.csv").open()))
    assert len(main) == 1
    assert main[0]["source"] == "s:2"
    assert len(success) == 1
    assert success[0]["source"] == "s:1"
    assert len(error) == 1
    assert error[0]["source"] == "s:2"


def test_summarize_inventory_links_field_isolation_csvs():
    validation_rows = [
        ValidationRow("1", "A", "r0", "s:1", True, "", "", "", "", ""),
    ]
    field_rows = [
        FieldIsolationRow(
            "1",
            "A",
            "r1",
            "s:2",
            False,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
    ]
    text = summarize_inventory(
        validation_rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        field_isolation_rows=field_rows,
    )
    assert "asca-field-isolation.csv" in text
    assert "asca-field-isolation-success.csv" in text
    assert "asca-field-isolation-error.csv" in text
    assert "## Field isolation blame (error rows)" in text
    assert "| 1 | `input` |" in text


@patch("conlanger.tools.corpus_inventory.validate_asca_part", return_value=True)
def test_build_field_isolation_row_unknown_feature_on_input(mock_validate_part):
    def side_effect(part, fragment, **kwargs):
        if part == "input":
            raise ASCAValidationError("Syntax Error: Unknown feature 'voiced'")
        return True

    mock_validate_part.side_effect = side_effect

    field_rule = SoundChangeRule(
        {
            "input": "C:[+voiced]",
            "output": "e",
        }
    )
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        False,
        "unknown_feature",
        "asca-unrepresentable",
        "voiced",
        "voice",
        "whole fail",
    )
    row = build_field_isolation_row(validation_row, field_rule)
    assert row.blame == "input"
    assert row.input_ok is False
    assert row.input_class == "unknown_feature"
    assert row.output_ok is True


@patch("conlanger.tools.corpus_inventory.validate_asca_part")
def test_build_field_isolation_row_missing_underscore_on_env(mock_validate_part):
    def side_effect(part, fragment, **kwargs):
        if part == "env":
            raise ASCAValidationError("Syntax Error: Expected '_'")
        return True

    mock_validate_part.side_effect = side_effect

    field_rule = SoundChangeRule(
        {
            "input": "a",
            "output": "e",
            "env": "word-initially",
        }
    )
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        False,
        "expected_underscore",
        "asca-unrepresentable",
        "",
        "",
        "whole fail",
    )
    row = build_field_isolation_row(validation_row, field_rule)
    assert row.blame == "env"
    assert row.env_ok is False
    assert row.env_class == "expected_underscore"
    assert row.input_ok is True
    assert row.output_ok is True


@patch("conlanger.tools.corpus_inventory.validate_asca_part")
def test_build_field_isolation_row_two_fields_fail(mock_validate_part):
    def side_effect(part, _fragment, **kwargs):
        if part in {"input", "env"}:
            raise ASCAValidationError(f"Syntax Error: bad {part}")
        return True

    mock_validate_part.side_effect = side_effect

    field_rule = SoundChangeRule(
        {
            "input": "bad",
            "output": "e",
            "env": "bad-env",
        }
    )
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        False,
        "syntax_other",
        "broken-syntax",
        "",
        "",
        "whole fail",
    )
    row = build_field_isolation_row(validation_row, field_rule)
    assert row.blame == "input|env"


@pytest.mark.skipif(not ASCA_VALIDATE_INSTALLED, reason="asca validate not available")
def test_field_isolation_integration_multi_blame():
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        False,
        "runtime_other",
        "broken-syntax",
        "",
        "",
        "uneven set",
    )
    field_rule = SoundChangeRule(
        {
            "input": "{p,t}",
            "output": "{b}",
        }
    )
    row = build_field_isolation_row(validation_row, field_rule)
    assert row.input_ok is True
    assert row.output_ok is True
    assert row.blame == "multi"

    rows, targets = validate_corpus_rule_with_targets(
        _SECTION,
        {"stages": ["{p,t}", "{b}"], "raw": "{p,t} → {b}", "source": "s:multi"},
        "r0",
        probe_words=None,
    )
    assert len(rows) == 1
    assert rows[0].ok is False
    field_rows = field_isolation_rows_for_validation_rows(rows, targets)
    assert field_rows[0].blame == "multi"
