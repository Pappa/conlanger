from pathlib import Path

import pandas as pd

from conlanger.tools.inventory_error_clusters import (
    EXPECTED_UNDERSCORE_ERRORS_CSV_NAME,
    UNKNOWN_CHARACTER_ERRORS_CSV_NAME,
    UNKNOWN_GROUPING_ERRORS_CSV_NAME,
    cluster_errors_dataframe,
    filter_errors_by_failure_class,
    write_error_cluster_csvs,
)


def _error_row(
    failure_class: str,
    *,
    error_token: str = "M",
    description: str = "Syntax Error: bad | a > b / _",
) -> dict[str, str]:
    return {
        "section_index": "1.2.3",
        "section_name": "Section",
        "rule_id": "rule-1",
        "alt_idx": "",
        "source": "file:1",
        "ok": "False",
        "failure_class": failure_class,
        "reason": "asca-unrepresentable",
        "error_token": error_token,
        "suggested": "",
        "description": description,
    }


def test_filter_errors_by_failure_class():
    df = pd.DataFrame(
        [
            _error_row("unknown_grouping"),
            _error_row("unknown_character", error_token="+"),
            _error_row("syntax_other", error_token=""),
        ]
    )
    grouped = filter_errors_by_failure_class(df, "unknown_grouping")
    assert len(grouped) == 1
    assert grouped.iloc[0]["failure_class"] == "unknown_grouping"


def test_cluster_errors_dataframe_extracts_rule_text():
    df = pd.DataFrame(
        [
            _error_row(
                "unknown_grouping",
                description="Syntax Error: Unknown grouping 'M' | ∅ > ʉ / M_#",
            )
        ]
    )
    clustered = cluster_errors_dataframe(df, "unknown_grouping")
    assert list(clustered.columns) == [
        "section_index",
        "rule_id",
        "error_token",
        "rule",
    ]
    assert clustered.iloc[0]["rule"] == "∅ > ʉ / M_#"


def test_cluster_errors_dataframe_empty():
    clustered = cluster_errors_dataframe(pd.DataFrame(), "unknown_character")
    assert clustered.empty
    assert list(clustered.columns) == [
        "section_index",
        "rule_id",
        "error_token",
        "rule",
    ]


def test_write_error_cluster_csvs(tmp_path: Path):
    df = pd.DataFrame(
        [
            _error_row("unknown_grouping"),
            _error_row("unknown_character", error_token="+"),
            _error_row("expected_underscore", error_token=""),
        ]
    )
    write_error_cluster_csvs(df, tmp_path)
    assert (tmp_path / UNKNOWN_GROUPING_ERRORS_CSV_NAME).is_file()
    assert (tmp_path / UNKNOWN_CHARACTER_ERRORS_CSV_NAME).is_file()
    assert (tmp_path / EXPECTED_UNDERSCORE_ERRORS_CSV_NAME).is_file()
    grouping = pd.read_csv(tmp_path / UNKNOWN_GROUPING_ERRORS_CSV_NAME)
    assert len(grouping) == 1
    assert grouping.iloc[0]["rule"] == "a > b / _"
