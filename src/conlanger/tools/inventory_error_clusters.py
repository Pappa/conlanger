"""Failure-class cluster CSVs derived from the validation error inventory."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

UNKNOWN_GROUPING_ERRORS_CSV_NAME = "unknown_grouping_errors.csv"
UNKNOWN_CHARACTER_ERRORS_CSV_NAME = "unknown_character_errors.csv"
UNKNOWN_REFERENCE_ERRORS_CSV_NAME = "unknown_reference_errors.csv"
EXPECTED_UNDERSCORE_ERRORS_CSV_NAME = "expected_underscore_errors.csv"
NESTED_BRACKETS_ERRORS_CSV_NAME = "nested_brackets_errors.csv"
UNKNOWN_FEATURES_ERRORS_CSV_NAME = "unknown_features_errors.csv"
SYNTAX_OTHER_ERRORS_CSV_NAME = "syntax_other_errors.csv"
RUNTIME_OTHER_ERRORS_CSV_NAME = "runtime_other_errors.csv"
EXPECTED_NUMBER_ERRORS_CSV_NAME = "expected_number_errors.csv"
PROSE_OR_EXPECTED_ARROW_ERRORS_CSV_NAME = "prose_or_expected_arrow_errors.csv"
INVALID_IPA_ERRORS_CSV_NAME = "invalid_ipa_errors.csv"
EXPECTED_IPA_ERRORS_CSV_NAME = "expected_ipa_errors.csv"
EXPECTED_RANGE_DOTS_ERRORS_CSV_NAME = "expected_range_dots_errors.csv"
MISSING_SLASH_OUTPUT_ENV_ERRORS_CSV_NAME = "missing_slash_output_env_errors.csv"
FLOATING_DIACRITIC_ERRORS_CSV_NAME = "floating_diacritic_errors.csv"
MULTIPLE_UNDERLINES_ENV_ERRORS_CSV_NAME = "multiple_underlines_env_errors.csv"
SEGMENTS_BEFORE_WORD_ERRORS_CSV_NAME = "segments_before_word_errors.csv"
STUFF_AFTER_WORD_BOUND_ERRORS_CSV_NAME = "stuff_after_word_bound_errors.csv"
DIACRITIC_PREREQ_ERRORS_CSV_NAME = "diacritic_prereq_errors.csv"
EMPTY_IO_PANIC_ERRORS_CSV_NAME = "empty_io_panic_errors.csv"
INCOMPLETE_MATRIX_ERRORS_CSV_NAME = "incomplete_matrix_errors.csv"
GROUPED_ENV_INSERTION_ERRORS_CSV_NAME = "grouped_env_insertion_errors.csv"
UNEVEN_PARALLEL_SETS_ERRORS_CSV_NAME = "uneven_parallel_sets_errors.csv"
WORD_BOUNDARY_IN_IO_ERRORS_CSV_NAME = "word_boundary_in_io_errors.csv"

CLUSTER_CSV_BY_FAILURE_CLASS: dict[str, str] = {
    "syntax_other": SYNTAX_OTHER_ERRORS_CSV_NAME,
    "runtime_other": RUNTIME_OTHER_ERRORS_CSV_NAME,
    "unknown_character": UNKNOWN_CHARACTER_ERRORS_CSV_NAME,
    "unknown_grouping": UNKNOWN_GROUPING_ERRORS_CSV_NAME,
    "unknown_reference": UNKNOWN_REFERENCE_ERRORS_CSV_NAME,
    "expected_underscore": EXPECTED_UNDERSCORE_ERRORS_CSV_NAME,
    "nested_brackets": NESTED_BRACKETS_ERRORS_CSV_NAME,
    "unknown_feature": UNKNOWN_FEATURES_ERRORS_CSV_NAME,
    "expected_number": EXPECTED_NUMBER_ERRORS_CSV_NAME,
    "prose_or_expected_arrow": PROSE_OR_EXPECTED_ARROW_ERRORS_CSV_NAME,
    "invalid_ipa": INVALID_IPA_ERRORS_CSV_NAME,
    "expected_ipa": EXPECTED_IPA_ERRORS_CSV_NAME,
    "expected_range_dots": EXPECTED_RANGE_DOTS_ERRORS_CSV_NAME,
    "missing_slash_output_env": MISSING_SLASH_OUTPUT_ENV_ERRORS_CSV_NAME,
    "floating_diacritic": FLOATING_DIACRITIC_ERRORS_CSV_NAME,
    "multiple_underlines_env": MULTIPLE_UNDERLINES_ENV_ERRORS_CSV_NAME,
    "segments_before_word": SEGMENTS_BEFORE_WORD_ERRORS_CSV_NAME,
    "stuff_after_word_bound": STUFF_AFTER_WORD_BOUND_ERRORS_CSV_NAME,
    "diacritic_prereq": DIACRITIC_PREREQ_ERRORS_CSV_NAME,
    "empty_io_panic": EMPTY_IO_PANIC_ERRORS_CSV_NAME,
    "incomplete_matrix": INCOMPLETE_MATRIX_ERRORS_CSV_NAME,
    "grouped_env_insertion": GROUPED_ENV_INSERTION_ERRORS_CSV_NAME,
    "uneven_parallel_sets": UNEVEN_PARALLEL_SETS_ERRORS_CSV_NAME,
    "word_boundary_in_io": WORD_BOUNDARY_IN_IO_ERRORS_CSV_NAME,
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
    """Write failure-class cluster CSVs under ``inventory_dir``."""
    inventory_dir.mkdir(parents=True, exist_ok=True)
    for failure_class, filename in CLUSTER_CSV_BY_FAILURE_CLASS.items():
        failures_df = cluster_errors_dataframe(error_df, failure_class)
        failures_df.to_csv(inventory_dir / filename, index=False)
