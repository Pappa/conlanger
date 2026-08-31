"""Failure-class cluster CSVs derived from the validation error inventory."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

GROUPING_ERRORS_CSV_NAME = "grouping_errors.csv"
CHARACTER_ERRORS_CSV_NAME = "character_errors.csv"
UNDERSCORE_ERRORS_CSV_NAME = "underscore_errors.csv"
NESTED_BRACKETS_ERRORS_CSV_NAME = "nested_brackets_errors.csv"
UNKNOWN_FEATURES_CSV_NAME = "unknown_features.csv"

CLUSTER_CSV_BY_FAILURE_CLASS: dict[str, str] = {
    "unknown_grouping": GROUPING_ERRORS_CSV_NAME,
    "unknown_character": CHARACTER_ERRORS_CSV_NAME,
    "expected_underscore": UNDERSCORE_ERRORS_CSV_NAME,
    "nested_brackets": NESTED_BRACKETS_ERRORS_CSV_NAME,
    "unknown_feature": UNKNOWN_FEATURES_CSV_NAME,
}

CLUSTER_SOURCE_COLUMNS = [
    "section_index",
    "rule_id",
    "error_token",
    "description",
]

CLUSTER_OUTPUT_COLUMNS = [
    "section_index",
    "rule_id",
    "error_token",
    "rule",
]


def filter_errors_by_failure_class(
    error_df: pd.DataFrame, failure_class: str
) -> pd.DataFrame:
    """Return error-inventory rows for one ``failure_class``."""
    if error_df.empty:
        return error_df.copy()
    return error_df.loc[error_df["failure_class"] == failure_class].reset_index(
        drop=True
    )


def cluster_errors_dataframe(
    error_df: pd.DataFrame, failure_class: str
) -> pd.DataFrame:
    """Build a cluster CSV frame with compiled rule text extracted from ``description``."""
    columns = CLUSTER_OUTPUT_COLUMNS
    if error_df.empty:
        return pd.DataFrame(columns=columns)
    filtered = filter_errors_by_failure_class(error_df, failure_class)
    if filtered.empty:
        return pd.DataFrame(columns=columns)
    clustered = filtered.loc[:, CLUSTER_SOURCE_COLUMNS].copy()
    clustered["rule"] = (
        clustered["description"].astype(str).str.split(" | ", n=1, regex=False).str[1]
    )
    return clustered.drop(columns=["description"]).reset_index(drop=True)


def write_error_cluster_csvs(error_df: pd.DataFrame, inventory_dir: Path) -> None:
    """Write grouping/character/underscore cluster CSVs under ``inventory_dir``."""
    inventory_dir.mkdir(parents=True, exist_ok=True)
    for failure_class, filename in CLUSTER_CSV_BY_FAILURE_CLASS.items():
        cluster_errors_dataframe(error_df, failure_class).to_csv(
            inventory_dir / filename, index=False
        )
