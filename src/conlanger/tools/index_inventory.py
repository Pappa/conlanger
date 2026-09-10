"""Validation inventory for cleaned rule index (ticket 12).

Whole-rule ``ok`` uses ``validate_asca`` (syntax + baseline probe run). Per-field
checks (ticket 36) use ``validate_asca_part`` on compiled ``SoundChangeRule``
field strings — Tier 1–2 / field-local syntax only. ``blame=multi`` means the
whole rule failed while every present field passed in isolation (uneven sets,
cross-field coupling, Tier-4 runtime, etc.); ticket 10 probe synthesis is out
of scope.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from conlanger.appliers.asca import (
    ASCARulePart,
    ASCAValidationError,
    validate_asca,
    validate_asca_part,
)
from conlanger.tools.inventory_error_clusters import (
    CLUSTER_CSV_BY_FAILURE_CLASS,
)
from conlanger.tools.rules import DiachronicSeries, RuleTitle, SoundChangeRule
from conlanger.utils.mappings import CompilerConfig

ERROR_CLASS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("nested_brackets", re.compile(r"nested brackets", re.IGNORECASE)),
    ("unknown_feature", re.compile(r"Unknown feature", re.IGNORECASE)),
    ("unknown_grouping", re.compile(r"Unknown grouping", re.IGNORECASE)),
    ("unknown_reference", re.compile(r"Unknown reference", re.IGNORECASE)),
    ("invalid_ipa", re.compile(r"Could not get value of IPA", re.IGNORECASE)),
    ("unknown_character", re.compile(r"Unknown character", re.IGNORECASE)),
    (
        "prose_or_expected_arrow",
        re.compile(
            r"Expected '>'|Expected '->'|Expected '=>'",
            re.IGNORECASE,
        ),
    ),
    ("expected_underscore", re.compile(r"Expected '_'", re.IGNORECASE)),
    ("expected_number", re.compile(r"Expected number", re.IGNORECASE)),
    (
        "expected_ipa",
        re.compile(
            r"Expected an IPA character|Primative or Matrix, but received",
            re.IGNORECASE,
        ),
    ),
    ("expected_range_dots", re.compile(r"Expected '\.\.'", re.IGNORECASE)),
    (
        "missing_slash_output_env",
        re.compile(r"forget a '/' between the output and environment", re.IGNORECASE),
    ),
    (
        "floating_diacritic",
        re.compile(r"Floating diacritic", re.IGNORECASE),
    ),
    (
        "multiple_underlines_env",
        re.compile(r"Cannot have multiple underlines in an environment", re.IGNORECASE),
    ),
    (
        "segments_before_word",
        re.compile(r"before the beginning of a word", re.IGNORECASE),
    ),
    ("stuff_after_word_bound", re.compile(r"after the end of a word", re.IGNORECASE)),
    (
        "diacritic_prereq",
        re.compile(r"prerequisite properties.*diacritic", re.IGNORECASE),
    ),
    (
        "empty_io_panic",
        re.compile(
            r"Output is not empty|Input is empty|Output is empty|"
            r"deletion rule must only contain|insertion rule must only contain",
            re.IGNORECASE,
        ),
    ),
    (
        "runtime_delete_only_segment",
        re.compile(r"Can't delete a word's only segment", re.IGNORECASE),
    ),
    (
        "incomplete_matrix",
        re.compile(r"An incomplete matrix cannot be inserted", re.IGNORECASE),
    ),
    (
        "grouped_env_insertion",
        re.compile(
            r"Grouped Environments cannot \(yet\) be used in insertion rules",
            re.IGNORECASE,
        ),
    ),
    (
        "uneven_parallel_sets",
        re.compile(
            r"Two matched sets must have the same number of elements",
            re.IGNORECASE,
        ),
    ),
    (
        "word_boundary_in_io",
        re.compile(
            r"Word Boundaries cannot be in the input or output",
            re.IGNORECASE,
        ),
    ),
    ("malformed_comment", re.compile(r"Malformed Comment", re.IGNORECASE)),
    ("missing_arrow", re.compile(r"missing separator", re.IGNORECASE)),
    ("format_error", re.compile(r"format_error", re.IGNORECASE)),
]

_UNKNOWN_TOKEN_RE = re.compile(
    r"Unknown (?:feature|grouping|character|reference) '([^']+)'",
    re.IGNORECASE,
)
_EXPECTED_IPA_RECEIVED_RE = re.compile(
    r"Expected an IPA character.*?but received (?:\.)?'([^']*)'",
    re.IGNORECASE,
)
_EXPECTED_NUMBER_RECEIVED_RE = re.compile(
    r"Expected number, but received (\S)",
    re.IGNORECASE,
)
_EXPECTED_END_OF_LINE_RECEIVED_RE = re.compile(
    r"Expected end of line, received '([^']*)'",
    re.IGNORECASE,
)
_EXPECTED_RANGE_DOTS_RECEIVED_RE = re.compile(
    r"Expected '\.\.', but received \.'([^']*)'",
    re.IGNORECASE,
)
_EXPECTED_QUOTED_RECEIVED_RE = re.compile(
    r"Expected '([^']*)', but received '([^']*)'",
    re.IGNORECASE,
)
_EXPECTED_QUOTED_UNQUOTED_RECEIVED_RE = re.compile(
    r"Expected '([^']*)', but received (\S)",
    re.IGNORECASE,
)
_EXPECTED_UNQUOTED_RECEIVED_RE = re.compile(
    r"Expected ([^,]+), but received (?:\.)?'([^']*)'",
    re.IGNORECASE,
)
_EXPECTED_UNQUOTED_UNQUOTED_RECEIVED_RE = re.compile(
    r"Expected ([^,]+), but received (\S)",
    re.IGNORECASE,
)
_DID_YOU_MEAN_RE = re.compile(r"Did you mean ([^?]+)\?", re.IGNORECASE)
_THREAD_PANICKED_RE = re.compile(r"^(thread) .+ (panicked at [^.]+\.rs)", re.IGNORECASE)
VALIDATION_CSV_COLUMNS = [
    "section_index",
    "section_name",
    "rule_id",
    "alt_idx",
    "source",
    "ok",
    "failure_class",
    "error_token",
    "suggested",
    "expected",
    "description",
]

CHANGELOG_CSV_COLUMNS = [
    "section_index",
    "rule_id",
    "alt_idx",
    "source",
    "ok",
    "timestamp",
]

INVENTORY_SUCCESS_CSV_NAME = "rule-inventory-success.csv"
INVENTORY_ERROR_CSV_NAME = "rule-inventory-error.csv"
INVENTORY_SKIPPED_CSV_NAME = "rule-inventory-skipped.csv"
INVENTORY_CHANGELOG_CSV_NAME = "rule-inventory-changelog.csv"
FIELD_ISOLATION_SUCCESS_CSV_NAME = "field-isolation-success.csv"
FIELD_ISOLATION_ERROR_CSV_NAME = "field-isolation-error.csv"
FIELD_ISOLATION_SKIPPED_CSV_NAME = "field-isolation-skipped.csv"
SECTION_SKIPPED_FAILURE_CLASS = "section_skipped"
RULE_SKIPPED_FAILURE_CLASS = "rule_skipped"
SKIPPED_FAILURE_CLASSES = frozenset(
    {SECTION_SKIPPED_FAILURE_CLASS, RULE_SKIPPED_FAILURE_CLASS}
)

OK_FALSE = 0
OK_TRUE = 1
OK_SKIPPED = 2

BLAME_FIELD_ORDER: tuple[ASCARulePart, ...] = ("input", "output", "env", "exception")

FIELD_ISOLATION_CSV_COLUMNS = [
    "section_index",
    "section_name",
    "rule_id",
    "alt_idx",
    "source",
    "whole_ok",
    "failure_class",
    "input_ok",
    "output_ok",
    "env_ok",
    "exception_ok",
    "input_class",
    "output_class",
    "env_class",
    "exception_class",
    "input_description",
    "output_description",
    "env_description",
    "exception_description",
    "blame",
]


def _coerce_ok_value(value: object) -> int:
    """Map a cell value to ``OK_FALSE`` (0), ``OK_TRUE`` (1), or ``OK_SKIPPED`` (2)."""
    if value in (OK_SKIPPED, 2, 2.0, "2"):
        return OK_SKIPPED
    if value is None or value is pd.NA:
        return OK_SKIPPED
    if isinstance(value, bool):
        return OK_TRUE if value else OK_FALSE
    if isinstance(value, float) and pd.isna(value):
        return OK_SKIPPED
    if value in (OK_TRUE, 1, 1.0):
        return OK_TRUE
    if value in (OK_FALSE, 0, 0.0):
        return OK_FALSE
    text = str(value).strip().lower()
    if text in {"", "nan", "none"}:
        return OK_SKIPPED
    if text in {"true", "1"}:
        return OK_TRUE
    if text in {"false", "0"}:
        return OK_FALSE
    if text == "2":
        return OK_SKIPPED
    return OK_SKIPPED


def _coerce_ok_column(series: pd.Series) -> pd.Series:
    """Return an int8 series for inventory ``ok`` / ``whole_ok`` columns."""
    return series.map(_coerce_ok_value).astype("int8")


def _alt_idx_key(series: pd.Series) -> pd.Series:
    """Normalize ``alt_idx`` (int / empty / NaN / CSV float) into a string key."""

    def _norm(value: object) -> str:
        if (
            value is None
            or value == ""
            or (isinstance(value, float) and pd.isna(value))
        ):
            return ""
        try:
            return str(int(float(value)))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return str(value)

    return series.map(_norm)


def validation_rows_to_dataframe(rows: list[ValidationRow]) -> pd.DataFrame:
    """Return validation rows as a DataFrame with a stable column order."""
    if not rows:
        df = pd.DataFrame(columns=VALIDATION_CSV_COLUMNS)
        df["ok"] = pd.Series(dtype="int8")
        return df
    df = pd.DataFrame(
        [row.as_csv_dict() for row in rows], columns=VALIDATION_CSV_COLUMNS
    )
    df["ok"] = _coerce_ok_column(df["ok"])
    return df


def filter_inventory_by_ok(df: pd.DataFrame, *, ok: bool) -> pd.DataFrame:
    """Return inventory rows whose ``ok`` column matches ``ok``.

    Skipped rows (``ok=2``) are excluded from both success and error filtered CSVs.
    """
    if df.empty:
        return df.copy()
    column = _coerce_ok_column(df["ok"])
    target = OK_TRUE if ok else OK_FALSE
    return df.loc[column == target].reset_index(drop=True)


def filter_inventory_skipped(df: pd.DataFrame) -> pd.DataFrame:
    """Return config hold-out rows (``ok=2``) for the skipped inventory CSV."""
    if df.empty:
        return df.copy()
    return df.loc[_coerce_ok_column(df["ok"]) == OK_SKIPPED].reset_index(drop=True)


def ok_flip_changelog_rows(
    previous: pd.DataFrame | None,
    current: pd.DataFrame,
    *,
    timestamp: str,
) -> pd.DataFrame:
    """Return changelog rows for rules whose ``ok`` flipped vs ``previous``.

    Matching is by ``(source, alt_idx)`` so optional-output alternatives are
    tracked independently. When ``previous`` is missing or empty, no flips are
    emitted (first-run behaviour). ``timestamp`` is copied onto every row.
    """
    empty = pd.DataFrame(columns=CHANGELOG_CSV_COLUMNS)
    if previous is None or previous.empty or current.empty:
        return empty
    # Prior inventories predating ``alt_idx`` have no such column — treat as empty.
    previous = (
        previous if "alt_idx" in previous.columns else previous.assign(alt_idx="")
    )
    prev = previous.loc[:, ["source", "alt_idx", "ok"]].copy()
    prev["_alt_key"] = _alt_idx_key(prev["alt_idx"])
    prev["ok"] = _coerce_ok_column(prev["ok"])
    prev = prev.drop_duplicates(subset=["source", "_alt_key"], keep="last")
    prev = prev.set_index(["source", "_alt_key"])["ok"]
    cur = current.loc[
        :,
        ["section_index", "rule_id", "alt_idx", "source", "ok"],
    ].copy()
    cur["_alt_key"] = _alt_idx_key(cur["alt_idx"])
    cur["ok"] = _coerce_ok_column(cur["ok"])
    cur = cur.drop_duplicates(subset=["source", "_alt_key"], keep="last")
    merged = cur.join(prev.rename("_prev_ok"), on=["source", "_alt_key"], how="inner")
    flipped = merged.loc[merged["ok"] != merged["_prev_ok"]].copy()
    if flipped.empty:
        return empty
    flipped["alt_idx"] = _alt_idx_key(flipped["alt_idx"])
    flipped["timestamp"] = timestamp
    return flipped.loc[:, CHANGELOG_CSV_COLUMNS].reset_index(drop=True)


def top_error_tokens(
    rows: list[ValidationRow],
    failure_class: str,
    *,
    limit: int | None = 5,
) -> list[tuple[str, int]]:
    """Return the most frequent ``error_token`` values for a failure class."""
    return top_error_tokens_from_dataframe(
        validation_rows_to_dataframe(rows),
        failure_class,
        limit=limit,
    )


def top_error_tokens_from_dataframe(
    df: pd.DataFrame,
    failure_class: str,
    *,
    limit: int | None = 10,
) -> list[tuple[str, int]]:
    """Return the most frequent ``error_token`` values for a failure class."""
    if df.empty:
        return []
    tokens = df.loc[
        (df["failure_class"] == failure_class) & (df["error_token"].astype(str) != ""),
        "error_token",
    ]
    if tokens.empty:
        return []
    counts = tokens.value_counts()
    if limit is not None:
        counts = counts.head(limit)
    return [(str(token), int(count)) for token, count in counts.items()]


def top_error_descriptions_from_dataframe(
    df: pd.DataFrame,
    failure_class: str,
    *,
    limit: int | None = 10,
) -> list[tuple[str, int]]:
    """Return top ``description`` counts for a failure class."""
    if df.empty:
        return []
    descriptions = (
        df.loc[
            (df["failure_class"] == failure_class)
            & (df["error_token"].astype(str) == ""),
            "description",
        ]
        .str.replace(r"(?:Syntax|Runtime) Error: ", "", regex=True)
        .str.split(" | ", n=1, regex=False)
        .str[0]
    )
    if descriptions.empty:
        return []
    counts = descriptions.value_counts()
    if limit is not None:
        counts = counts.head(limit)
    return [(str(description), int(count)) for description, count in counts.items()]


def top_error_tokens_with_suggested_from_dataframe(
    df: pd.DataFrame,
    failure_class: str,
    *,
    limit: int | None = 10,
) -> list[tuple[str, int, str]]:
    """Return top ``error_token`` counts with the modal ASCA ``suggested`` hint."""
    if df.empty:
        return []
    subset = df.loc[
        (df["failure_class"] == failure_class) & (df["error_token"].astype(str) != "")
    ]
    if subset.empty:
        return []
    counts = subset["error_token"].value_counts()
    if limit is not None:
        counts = counts.head(limit)
    results: list[tuple[str, int, str]] = []
    for token, count in counts.items():
        suggested = subset.loc[subset["error_token"] == token, "suggested"]
        modal = suggested.mode()
        suggestion = str(modal.iloc[0]) if not modal.empty else ""
        results.append((str(token), int(count), suggestion))
    return results


def format_common_errors_section(rows: list[ValidationRow]) -> list[str]:
    """Markdown lines for top ``error_token`` counts per unknown-token failure class."""
    df = validation_rows_to_dataframe(rows)
    lines = ["", "## Common Errors", ""]
    for failure_class in CLUSTER_CSV_BY_FAILURE_CLASS:
        if failure_class == "unknown_feature":
            lines.extend(
                [
                    f"### {failure_class} (error_token)",
                    "",
                    "| count | error_token | suggested |",
                    "|------:|-------------|-----------|",
                ]
            )
            top_errors_with_suggested = top_error_tokens_with_suggested_from_dataframe(
                df, failure_class
            )
            if top_errors_with_suggested:
                for token, count, suggested in top_errors_with_suggested:
                    suggested_cell = f"`{suggested}`" if suggested else "—"
                    lines.append(f"| {count} | `{token}` | {suggested_cell} |")
            else:
                lines.append("| — | _(none)_ | — |")
        else:
            lines.extend(
                [
                    f"### {failure_class} (error_token)",
                    "",
                    "| count | error_token |",
                    "|------:|-------------|",
                ]
            )
            top_errors = top_error_tokens_from_dataframe(df, failure_class)
            if top_errors:
                for value, count in top_errors:
                    lines.append(f"| {count} | `{value}` |")
            else:
                lines.append("| — | _(none)_ |")

            top_errors_with_description = top_error_descriptions_from_dataframe(
                df, failure_class
            )
            lines.extend(
                [
                    f"### {failure_class} (description)",
                    "",
                    "| count | description |",
                    "|------:|-------------|",
                ]
            )
            if top_errors_with_description:
                for description, count in top_errors_with_description:
                    lines.append(f"| {count} | `{description}` |")
            else:
                lines.append("| — | _(none)_ |")
        lines.append("")
    return lines


def parse_unknown_token_error(error: str) -> tuple[str, str, str]:
    """Extract received token, ASCA suggestion, and expected token from an error."""
    suggest_match = _DID_YOU_MEAN_RE.search(error)
    suggested = suggest_match.group(1).strip() if suggest_match else ""

    unknown_token_match = _UNKNOWN_TOKEN_RE.search(error)
    if unknown_token_match:
        return unknown_token_match.group(1), suggested, ""

    match = _EXPECTED_IPA_RECEIVED_RE.search(error)
    if match:
        return match.group(1), suggested, "IPA character"

    match = _EXPECTED_NUMBER_RECEIVED_RE.search(error)
    if match:
        return match.group(1), suggested, "number"

    match = _EXPECTED_END_OF_LINE_RECEIVED_RE.search(error)
    if match:
        return match.group(1), suggested, "end of line"

    match = _EXPECTED_RANGE_DOTS_RECEIVED_RE.search(error)
    if match:
        return match.group(1), suggested, ".."

    match = _EXPECTED_QUOTED_RECEIVED_RE.search(error)
    if match:
        return match.group(2), suggested, match.group(1)

    match = _EXPECTED_QUOTED_UNQUOTED_RECEIVED_RE.search(error)
    if match:
        return match.group(2), suggested, match.group(1)

    match = _EXPECTED_UNQUOTED_RECEIVED_RE.search(error)
    if match:
        return match.group(2), suggested, match.group(1).strip()

    match = _EXPECTED_UNQUOTED_UNQUOTED_RECEIVED_RE.search(error)
    if match:
        return match.group(2), suggested, match.group(1).strip()

    return "", suggested, ""


def parse_error_description(error: str, failure_class: str) -> str:
    """Extract description from a validation error string."""
    if failure_class == "panic_other":
        match = _THREAD_PANICKED_RE.search(error)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return "panicked"
    return error


def classify_error(error: str) -> str:
    if not error:
        return ""
    for name, pat in ERROR_CLASS_PATTERNS:
        if pat.search(error):
            return name
    lower = error.lower()
    if lower.startswith("syntax error"):
        return "syntax_other"
    if lower.startswith("runtime error"):
        return "runtime_other"
    if "panicked" in lower:
        return "panic_other"
    return "other"


@dataclass(frozen=True)
class ValidationRow:
    section_index: str
    section_name: str
    rule_id: str
    source: str
    ok: int
    failure_class: str = ""
    error_token: str = ""
    suggested: str = ""
    expected: str = ""
    description: str = ""
    alt_idx: int | None = None

    def as_csv_dict(self) -> dict[str, str | int | bool]:
        return {
            "section_index": self.section_index,
            "section_name": self.section_name,
            "rule_id": self.rule_id,
            "alt_idx": "" if self.alt_idx is None else self.alt_idx,
            "source": self.source,
            "ok": self.ok,
            "failure_class": self.failure_class,
            "error_token": self.error_token,
            "suggested": self.suggested,
            "expected": self.expected,
            "description": self.description,
        }


@dataclass(frozen=True)
class FieldIsolationRow:
    section_index: str
    section_name: str
    rule_id: str
    source: str
    whole_ok: int
    input_ok: bool | None
    output_ok: bool | None
    env_ok: bool | None
    exception_ok: bool | None
    input_class: str
    output_class: str
    env_class: str
    exception_class: str
    input_description: str
    output_description: str
    env_description: str
    exception_description: str
    blame: str
    failure_class: str = ""
    alt_idx: int | None = None

    def as_csv_dict(self) -> dict[str, str | int | bool]:
        def _field(value: bool | None) -> str | bool:
            if value is None:
                return ""
            return value

        return {
            "section_index": self.section_index,
            "section_name": self.section_name,
            "rule_id": self.rule_id,
            "alt_idx": "" if self.alt_idx is None else self.alt_idx,
            "source": self.source,
            "whole_ok": self.whole_ok,
            "failure_class": self.failure_class,
            "input_ok": _field(self.input_ok),
            "output_ok": _field(self.output_ok),
            "env_ok": _field(self.env_ok),
            "exception_ok": _field(self.exception_ok),
            "input_class": self.input_class,
            "output_class": self.output_class,
            "env_class": self.env_class,
            "exception_class": self.exception_class,
            "input_description": self.input_description,
            "output_description": self.output_description,
            "env_description": self.env_description,
            "exception_description": self.exception_description,
            "blame": self.blame,
        }


def derive_blame(
    whole_ok: int,
    *,
    input_ok: bool | None,
    output_ok: bool | None,
    env_ok: bool | None,
    exception_ok: bool | None,
) -> str:
    """Derive the ``blame`` column from whole-rule and per-field ok flags."""
    if whole_ok == OK_SKIPPED:
        return "none"
    field_ok: dict[ASCARulePart, bool | None] = {
        "input": input_ok,
        "output": output_ok,
        "env": env_ok,
        "exception": exception_ok,
    }
    failing = [name for name in BLAME_FIELD_ORDER if field_ok[name] is False]
    if failing:
        return "|".join(failing)
    if whole_ok == OK_TRUE:
        return "none"
    return "multi"


def _field_isolation_field_failure_mask(df: pd.DataFrame) -> pd.Series:
    mask = pd.Series(False, index=df.index)
    for column in ("input_ok", "output_ok", "env_ok", "exception_ok"):
        mask = mask | (df[column].astype(str).str.lower() == "false")
    return mask


def filter_field_isolation_success(df: pd.DataFrame) -> pd.DataFrame:
    """Return clean field-isolation rows (whole ok, fields ok, not skipped)."""
    if df.empty:
        return df.copy()
    whole_ok = _coerce_ok_column(df["whole_ok"])
    field_fail = _field_isolation_field_failure_mask(df)
    return df.loc[(whole_ok == OK_TRUE) & ~field_fail].reset_index(drop=True)


def filter_field_isolation_error(df: pd.DataFrame) -> pd.DataFrame:
    """Return field-isolation error rows (whole fail or field fail, not skipped)."""
    if df.empty:
        return df.copy()
    whole_ok = _coerce_ok_column(df["whole_ok"])
    field_fail = _field_isolation_field_failure_mask(df)
    return df.loc[
        ((whole_ok == OK_FALSE) | field_fail) & (whole_ok != OK_SKIPPED)
    ].reset_index(drop=True)


def filter_field_isolation_skipped(df: pd.DataFrame) -> pd.DataFrame:
    """Return field-isolation rows for config hold-outs (``whole_ok=2``)."""
    if df.empty:
        return df.copy()
    return df.loc[_coerce_ok_column(df["whole_ok"]) == OK_SKIPPED].reset_index(
        drop=True
    )


def filter_field_isolation_by_whole_ok(
    df: pd.DataFrame, *, whole_ok: bool
) -> pd.DataFrame:
    """Return field-isolation rows whose ``whole_ok`` column matches ``whole_ok``.

    Skipped rows (``whole_ok=2``) are excluded from both outcomes.
    Prefer :func:`filter_field_isolation_success` / :func:`filter_field_isolation_error`
    for the regen sidecar splits.
    """
    if df.empty:
        return df.copy()
    column = _coerce_ok_column(df["whole_ok"])
    target = OK_TRUE if whole_ok else OK_FALSE
    return df.loc[column == target].reset_index(drop=True)


def _field_rule_from_series(scr: DiachronicSeries) -> SoundChangeRule | None:
    """Return the sole ``SoundChangeRule`` in *scr*, or ``None`` for chains."""
    parts = [part for part in scr._parts if isinstance(part, SoundChangeRule)]
    if len(parts) == 1:
        return parts[0]
    return None


@dataclass(frozen=True)
class _InventoryTarget:
    alt_idx: int | None
    series: DiachronicSeries | None
    field_rule: SoundChangeRule | None
    format_error: str | None = None


def _resolve_inventory_targets(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_id: str,
    *,
    compiler_config: CompilerConfig | None = None,
) -> list[_InventoryTarget]:
    """Compile paths shared by whole-rule inventory and field isolation."""
    mini = _mini_section(section, rule, rule_id)
    try:
        scr = DiachronicSeries(
            mini,
            compiler_config=compiler_config,
            sample_sporadic=False,
        )
    except (KeyError, ValueError) as exc:
        return [
            _InventoryTarget(
                None,
                None,
                None,
                format_error=f"format_error: {exc}",
            )
        ]

    sound_change_parts = [
        part for part in scr._parts if isinstance(part, SoundChangeRule)
    ]
    if not sound_change_parts:
        return [
            _InventoryTarget(
                None,
                None,
                None,
                format_error="format_error: no compile steps from stages",
            )
        ]

    if len(sound_change_parts) == 1 and sound_change_parts[0].alternatives:
        return [
            _InventoryTarget(
                alt_idx,
                _series_for_alternative(
                    section, rule, rule_id, alternative, compiler_config
                ),
                alternative,
            )
            for alt_idx, alternative in enumerate(sound_change_parts[0].alternatives)
        ]

    return [_InventoryTarget(None, scr, _field_rule_from_series(scr))]


def _validate_field_part(
    part: ASCARulePart,
    fragment: str,
    *,
    asca_bin: str | None = None,
) -> tuple[bool, str, str]:
    """Validate one compiled field; return ``(ok, failure_class, description)``."""
    try:
        validate_asca_part(part, fragment, asca_bin=asca_bin)
    except ASCAValidationError as exc:
        err = str(exc)
        return False, classify_error(err), err
    return True, "", ""


def _field_isolation_checks(
    field_rule: SoundChangeRule,
    *,
    asca_bin: str | None = None,
) -> tuple[
    bool | None,
    bool | None,
    bool | None,
    bool | None,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
]:
    """Run per-field ``validate_asca_part`` on compiled ``SoundChangeRule`` strings."""
    results: dict[ASCARulePart, tuple[bool | None, str, str]] = {}
    for part in BLAME_FIELD_ORDER:
        fragment = getattr(field_rule, part)
        if fragment is None:
            results[part] = (None, "", "")
            continue
        if hasattr(fragment, "compiled"):
            fragment = fragment.compiled or fragment.raw
        ok, failure_class, description = _validate_field_part(
            part, fragment, asca_bin=asca_bin
        )
        results[part] = (ok, failure_class, description)

    input_ok, input_class, input_description = results["input"]
    output_ok, output_class, output_description = results["output"]
    env_ok, env_class, env_description = results["env"]
    exception_ok, exception_class, exception_description = results["exception"]
    return (
        input_ok,
        output_ok,
        env_ok,
        exception_ok,
        input_class,
        output_class,
        env_class,
        exception_class,
        input_description,
        output_description,
        env_description,
        exception_description,
    )


def build_field_isolation_row(
    validation_row: ValidationRow,
    field_rule: SoundChangeRule | None,
    *,
    asca_bin: str | None = None,
) -> FieldIsolationRow:
    """Build one field-isolation sidecar row for an inventory ``ValidationRow``."""
    base = {
        "section_index": validation_row.section_index,
        "section_name": validation_row.section_name,
        "rule_id": validation_row.rule_id,
        "alt_idx": validation_row.alt_idx,
        "source": validation_row.source,
        "whole_ok": validation_row.ok,
        "failure_class": validation_row.failure_class,
    }
    if field_rule is None:
        return FieldIsolationRow(
            **base,
            input_ok=None,
            output_ok=None,
            env_ok=None,
            exception_ok=None,
            input_class="",
            output_class="",
            env_class="",
            exception_class="",
            input_description="",
            output_description="",
            env_description="",
            exception_description="",
            blame=derive_blame(
                validation_row.ok,
                input_ok=None,
                output_ok=None,
                env_ok=None,
                exception_ok=None,
            ),
        )

    (
        input_ok,
        output_ok,
        env_ok,
        exception_ok,
        input_class,
        output_class,
        env_class,
        exception_class,
        input_description,
        output_description,
        env_description,
        exception_description,
    ) = _field_isolation_checks(field_rule, asca_bin=asca_bin)
    return FieldIsolationRow(
        **base,
        input_ok=input_ok,
        output_ok=output_ok,
        env_ok=env_ok,
        exception_ok=exception_ok,
        input_class=input_class,
        output_class=output_class,
        env_class=env_class,
        exception_class=exception_class,
        input_description=input_description,
        output_description=output_description,
        env_description=env_description,
        exception_description=exception_description,
        blame=derive_blame(
            validation_row.ok,
            input_ok=input_ok,
            output_ok=output_ok,
            env_ok=env_ok,
            exception_ok=exception_ok,
        ),
    )


def field_isolation_rows_for_validation_rows(
    validation_rows: list[ValidationRow],
    targets: list[_InventoryTarget],
    *,
    asca_bin: str | None = None,
) -> list[FieldIsolationRow]:
    """Pair inventory rows with compile targets and build field-isolation rows."""
    if len(validation_rows) != len(targets):
        msg = (
            "validation row count does not match compile target count: "
            f"{len(validation_rows)} vs {len(targets)}"
        )
        raise ValueError(msg)
    return [
        build_field_isolation_row(row, target.field_rule, asca_bin=asca_bin)
        for row, target in zip(validation_rows, targets, strict=True)
    ]


def field_isolation_rows_to_dataframe(rows: list[FieldIsolationRow]) -> pd.DataFrame:
    """Return field-isolation rows as a DataFrame with stable column order."""
    if not rows:
        df = pd.DataFrame(columns=FIELD_ISOLATION_CSV_COLUMNS)
        df["whole_ok"] = pd.Series(dtype="int8")
        return df
    df = pd.DataFrame(
        [row.as_csv_dict() for row in rows], columns=FIELD_ISOLATION_CSV_COLUMNS
    )
    df["whole_ok"] = _coerce_ok_column(df["whole_ok"])
    return df


def write_field_isolation_csvs(
    rows: list[FieldIsolationRow],
    inventory_dir: Path,
) -> None:
    """Write field-isolation success/error/skipped CSVs under ``inventory_dir``."""
    inventory_dir.mkdir(parents=True, exist_ok=True)
    df = field_isolation_rows_to_dataframe(rows)
    filter_field_isolation_success(df).to_csv(
        inventory_dir / FIELD_ISOLATION_SUCCESS_CSV_NAME, index=False
    )
    filter_field_isolation_error(df).to_csv(
        inventory_dir / FIELD_ISOLATION_ERROR_CSV_NAME, index=False
    )
    filter_field_isolation_skipped(df).to_csv(
        inventory_dir / FIELD_ISOLATION_SKIPPED_CSV_NAME, index=False
    )


def count_field_blame_categories(df: pd.DataFrame) -> Counter[str]:
    """Count rows per individual blame field (pipe-separated values split)."""
    counts: Counter[str] = Counter()
    for blame in df["blame"].astype(str):
        if blame == "multi":
            counts["multi"] += 1
            continue
        for part in blame.split("|"):
            if part:
                counts[part] += 1
    return counts


def format_field_isolation_blame_section(rows: list[FieldIsolationRow]) -> list[str]:
    """Markdown lines for individual blame category counts on whole-rule failure rows."""
    error_df = filter_field_isolation_by_whole_ok(
        field_isolation_rows_to_dataframe(rows), whole_ok=False
    )
    if error_df.empty:
        return []
    counts = count_field_blame_categories(error_df)
    lines = [
        "",
        "## Field isolation blame (error rows)",
        "",
        "| count | blame |",
        "|------:|-------|",
    ]
    for blame, count in counts.most_common():
        lines.append(f"| {count} | `{blame}` |")
    lines.append("")
    return lines


def _mini_section(
    section: dict[str, Any], rule: dict[str, Any], rule_id: str
) -> dict[str, Any]:
    return {
        "index": section.get("index", ""),
        "section": f"{section.get('section', '')}#{rule_id}",
        "rules": [rule],
    }


def _series_for_alternative(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_id: str,
    alternative: SoundChangeRule,
    compiler_config: CompilerConfig | None,
) -> DiachronicSeries:
    """Build a standalone series for one already-compiled alternative."""
    del rule, compiler_config  # alternative carries compiled fields; no re-parse
    section_index = str(section.get("index", ""))
    section_name = f"{section.get('section', '')}#{rule_id}"
    return DiachronicSeries.from_parts(
        [
            RuleTitle(section_index, section_name),
            alternative,
        ]
    )


def _asca_validation_row(
    scr: DiachronicSeries,
    *,
    section_index: str,
    section_name: str,
    rule_id: str,
    alt_idx: int | None,
    source: str,
    probe_words: Path | None,
    asca_bin: str | None = None,
) -> ValidationRow:
    """Validate an already-compiled series and build its ``ValidationRow``."""
    try:
        validate_asca(scr, probe_words=probe_words, asca_bin=asca_bin)
    except ASCAValidationError as exc:
        err = str(exc)
        failure_class = classify_error(err)
        error_token, suggested, expected = parse_unknown_token_error(err)
        description = parse_error_description(err, failure_class)

        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            alt_idx=alt_idx,
            source=source,
            ok=OK_FALSE,
            failure_class=failure_class,
            error_token=error_token,
            suggested=suggested,
            expected=expected,
            description=description,
        )

    return ValidationRow(
        section_index=section_index,
        section_name=section_name,
        rule_id=rule_id,
        alt_idx=alt_idx,
        source=source,
        ok=OK_TRUE,
    )


def validate_index_rule_with_targets(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_id: str,
    *,
    probe_words: Path | None,
    compiler_config: CompilerConfig | None = None,
    asca_bin: str | None = None,
) -> tuple[list[ValidationRow], list[_InventoryTarget]]:
    """Validate one index rule and return inventory rows with compile targets."""
    section_index = str(section.get("index", ""))
    section_name = str(section.get("section", ""))
    source = str(rule.get("source", ""))

    if section.get("status") == "skipped":
        row = ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            source=source,
            ok=OK_SKIPPED,
            failure_class=SECTION_SKIPPED_FAILURE_CLASS,
            description="section skipped at compile (parser_config skip_sections)",
        )
        return [row], [_InventoryTarget(None, None, None)]

    if rule.get("status") == "skipped":
        row = ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            source=source,
            ok=OK_SKIPPED,
            failure_class=RULE_SKIPPED_FAILURE_CLASS,
            description="held-out (commented rule)",
        )
        return [row], [_InventoryTarget(None, None, None)]

    targets = _resolve_inventory_targets(
        section, rule, rule_id, compiler_config=compiler_config
    )
    rows: list[ValidationRow] = []
    for target in targets:
        if target.format_error is not None:
            err = target.format_error
            failure_class = "format_error"
            error_token, suggested, expected = parse_unknown_token_error(err)
            rows.append(
                ValidationRow(
                    section_index=section_index,
                    section_name=section_name,
                    rule_id=rule_id,
                    source=source,
                    ok=OK_FALSE,
                    failure_class=failure_class,
                    error_token=error_token,
                    suggested=suggested,
                    expected=expected,
                    description=err,
                )
            )
            continue

        assert target.series is not None
        rows.append(
            _asca_validation_row(
                target.series,
                section_index=section_index,
                section_name=section_name,
                rule_id=rule_id,
                alt_idx=target.alt_idx,
                source=source,
                probe_words=probe_words,
                asca_bin=asca_bin,
            )
        )
    return rows, targets


def validate_index_rule(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_id: str,
    *,
    probe_words: Path | None,
    compiler_config: CompilerConfig | None = None,
    asca_bin: str | None = None,
) -> list[ValidationRow]:
    """Validate one index rule.

    Returns one row per optional-output alternative (0-based ``alt_idx``) when the
    rule has alternatives; otherwise a single row with an empty ``alt_idx``.
    """
    rows, _ = validate_index_rule_with_targets(
        section,
        rule,
        rule_id,
        probe_words=probe_words,
        compiler_config=compiler_config,
        asca_bin=asca_bin,
    )
    return rows


def iter_inventory_with_field_isolation(
    doc: dict[str, Any],
    *,
    field_isolation: bool = False,
    probe_words: Path | None,
    compiler_config: CompilerConfig | None = None,
    asca_bin: str | None = None,
) -> tuple[list[ValidationRow], list[FieldIsolationRow]]:
    """Validate the index and build matching field-isolation sidecar rows."""
    validation_rows: list[ValidationRow] = []
    field_rows: list[FieldIsolationRow] = []
    for section in doc.get("sections") or []:
        rules = section.get("rules") or []
        for rule in rules:
            rule_id = str(rule.get("rule_id", ""))
            rows, targets = validate_index_rule_with_targets(
                section,
                rule,
                rule_id,
                probe_words=probe_words,
                compiler_config=compiler_config,
                asca_bin=asca_bin,
            )
            validation_rows.extend(rows)
            if field_isolation:
                field_rows.extend(
                    field_isolation_rows_for_validation_rows(
                        rows, targets, asca_bin=asca_bin
                    )
                )
    return validation_rows, field_rows


def write_validation_csv(rows: list[ValidationRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    validation_rows_to_dataframe(rows).to_csv(path, index=False)


def load_inventory_csv(inventory_dir: Path) -> pd.DataFrame | None:
    """Load prior inventory rows from success/error/skipped split CSVs.

    Returns ``None`` when no split file exists (first-run behaviour).
    """
    frames: list[pd.DataFrame] = []
    for name in (
        INVENTORY_SUCCESS_CSV_NAME,
        INVENTORY_ERROR_CSV_NAME,
        INVENTORY_SKIPPED_CSV_NAME,
    ):
        path = inventory_dir / name
        if path.is_file():
            frame = pd.read_csv(path)
            frame["ok"] = _coerce_ok_column(frame["ok"])
            frames.append(frame)
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


def write_filtered_inventory_csvs(df: pd.DataFrame, inventory_dir: Path) -> None:
    """Rewrite success/error/skipped filtered inventory CSVs under ``inventory_dir``."""
    inventory_dir.mkdir(parents=True, exist_ok=True)
    filter_inventory_by_ok(df, ok=True).to_csv(
        inventory_dir / INVENTORY_SUCCESS_CSV_NAME, index=False
    )
    filter_inventory_by_ok(df, ok=False).to_csv(
        inventory_dir / INVENTORY_ERROR_CSV_NAME, index=False
    )
    filter_inventory_skipped(df).to_csv(
        inventory_dir / INVENTORY_SKIPPED_CSV_NAME, index=False
    )


def append_ok_flip_changelog(flips: pd.DataFrame, path: Path) -> int:
    """Append ``ok``-flip rows to the changelog CSV. Returns rows written."""
    if flips.empty:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.is_file()
    flips.to_csv(path, mode="a", header=write_header, index=False)
    return len(flips)


def write_ok_flip_changelog(
    flips: pd.DataFrame,
    path: Path,
    *,
    reset: bool = False,
) -> int:
    """Write changelog rows, overwriting when ``reset`` is set."""
    if reset:
        path.parent.mkdir(parents=True, exist_ok=True)
        if flips.empty:
            pd.DataFrame(columns=CHANGELOG_CSV_COLUMNS).to_csv(path, index=False)
            return 0
        flips.to_csv(path, index=False)
        return len(flips)
    return append_ok_flip_changelog(flips, path)


@dataclass(frozen=True)
class CorrectionsStats:
    """Per-rule rollup for matched Index Diachronica correction overlays."""

    total: int
    ok: int
    fail: int
    skipped: int
    failed_rules: tuple[tuple[str, str], ...]


def matched_correction_rule_ids(
    rows: list[ValidationRow],
    corrections: dict[str, str],
) -> frozenset[str]:
    """Return correction rule ids that appear in inventory rows."""
    inventory_ids = {row.rule_id for row in rows}
    return frozenset(rule_id for rule_id in corrections if rule_id in inventory_ids)


def _correction_rule_bucket(
    rule_rows: list[ValidationRow],
) -> tuple[str, str]:
    """Return ``(bucket, failure_class)`` for one corrected rule id."""
    if any(row.ok == OK_FALSE for row in rule_rows):
        failing = [row for row in rule_rows if row.ok == OK_FALSE]
        classes = [row.failure_class for row in failing if row.failure_class]
        if classes:
            counts = Counter(classes)
            max_count = max(counts.values())
            modal = [cls for cls, count in counts.items() if count == max_count]
            failure_class = (
                modal[0] if len(modal) == 1 else (failing[0].failure_class or "other")
            )
        else:
            failure_class = failing[0].failure_class or "other"
        return "fail", failure_class
    if all(row.ok == OK_SKIPPED for row in rule_rows):
        return "skipped", ""
    return "ok", ""


def corrections_outcome_stats(
    rows: list[ValidationRow],
    correction_rule_ids: frozenset[str],
) -> CorrectionsStats | None:
    """Return matched correction rollup stats, or ``None`` when ``N`` is zero."""
    if not correction_rule_ids:
        return None
    by_rule: dict[str, list[ValidationRow]] = {}
    for row in rows:
        if row.rule_id in correction_rule_ids:
            by_rule.setdefault(row.rule_id, []).append(row)
    total = len(by_rule)
    if total == 0:
        return None
    ok = fail = skipped = 0
    failed_rules: list[tuple[str, str]] = []
    for rule_id in sorted(by_rule):
        bucket, failure_class = _correction_rule_bucket(by_rule[rule_id])
        if bucket == "ok":
            ok += 1
        elif bucket == "fail":
            fail += 1
            failed_rules.append((rule_id, failure_class))
        else:
            skipped += 1
    return CorrectionsStats(
        total=total,
        ok=ok,
        fail=fail,
        skipped=skipped,
        failed_rules=tuple(failed_rules),
    )


def format_corrections_section(stats: CorrectionsStats | None) -> list[str]:
    """Markdown lines for the ``## Corrections`` summary section."""
    if stats is None or stats.total == 0:
        return []
    lines = ["", "## Corrections", ""]
    if stats.ok:
        lines.append(f"OK: **{stats.ok}/{stats.total}**")
    if stats.fail:
        lines.append(f"Fail: **{stats.fail}/{stats.total}**")
    if stats.skipped:
        lines.append(f"Skipped: **{stats.skipped}/{stats.total}**")
    if stats.fail:
        lines.extend(["", "### Failed corrections", ""])
        for rule_id, failure_class in stats.failed_rules:
            lines.append(f"- `{rule_id}` — `{failure_class}`")
    lines.append("")
    return lines


@dataclass(frozen=True)
class SectionOutcomeStats:
    """Per-section outcome counts (mutually exclusive buckets)."""

    total: int
    all_ok: int
    some_ok: int
    none_ok: int
    skipped: int


def _rows_by_section(
    rows: list[ValidationRow],
) -> dict[tuple[str, str], list[ValidationRow]]:
    by_section: dict[tuple[str, str], list[ValidationRow]] = {}
    for row in rows:
        key = (row.section_index, row.section_name)
        by_section.setdefault(key, []).append(row)
    return by_section


def section_outcome_stats(rows: list[ValidationRow]) -> SectionOutcomeStats:
    """Return mutually exclusive section outcome counts.

    - **skipped** — every rule in the section has ``failure_class=section_skipped``.
    - **all_ok** — not skipped; every rule has ``ok=1``.
    - **none_ok** — not skipped; every rule has ``ok=0``.
    - **some_ok** — not skipped; mix of validated outcomes.
    """
    by_section = _rows_by_section(rows)
    all_ok = some_ok = none_ok = skipped = 0
    for section_rows in by_section.values():
        if not section_rows:
            continue
        if all(
            row.failure_class == SECTION_SKIPPED_FAILURE_CLASS for row in section_rows
        ):
            skipped += 1
            continue
        if all(row.ok == OK_TRUE for row in section_rows):
            all_ok += 1
        elif all(row.ok == OK_FALSE for row in section_rows):
            none_ok += 1
        else:
            some_ok += 1
    return SectionOutcomeStats(
        total=len(by_section),
        all_ok=all_ok,
        some_ok=some_ok,
        none_ok=none_ok,
        skipped=skipped,
    )


def section_all_ok_stats(rows: list[ValidationRow]) -> tuple[int, int, float]:
    """Return count of sections with every rule ok, active total, and percentage.

    Sections with ``status: skipped`` are excluded from the denominator.
    """
    outcomes = section_outcome_stats(rows)
    active_total = outcomes.total - outcomes.skipped
    pct = (100.0 * outcomes.all_ok / active_total) if active_total else 0.0
    return outcomes.all_ok, active_total, pct


def section_skip_stats(rows: list[ValidationRow]) -> tuple[int, int, float]:
    """Return skipped section count, total sections (including skipped), and pct."""
    outcomes = section_outcome_stats(rows)
    pct = (100.0 * outcomes.skipped / outcomes.total) if outcomes.total else 0.0
    return outcomes.skipped, outcomes.total, pct


def summarize_inventory(
    rows: list[ValidationRow],
    *,
    source_yaml: str,
    probe_words: str,
    asca_version: str = "0.10.x",
    field_isolation_rows: list[FieldIsolationRow] | None = None,
    correction_rule_ids: frozenset[str] | None = None,
) -> str:
    total = len(rows)
    skipped_n = sum(1 for row in rows if row.ok == OK_SKIPPED)
    ok_n = sum(1 for row in rows if row.ok == OK_TRUE)
    fail_n = sum(1 for row in rows if row.ok == OK_FALSE)
    ok_pct = (100.0 * ok_n / total) if total else 0.0
    fail_pct = (100.0 * fail_n / total) if total else 0.0
    skipped_pct = (100.0 * skipped_n / total) if total else 0.0
    section_outcomes = section_outcome_stats(rows)
    section_total = section_outcomes.total

    def _section_pct(count: int) -> float:
        return (100.0 * count / section_total) if section_total else 0.0

    class_counts = Counter(
        row.failure_class for row in rows if row.ok == OK_FALSE and row.failure_class
    )

    lines = [
        "# Cleaned rule index — ASCA validation inventory",
        "",
        f"- Source YAML: `{source_yaml}`",
        f"- Probe words: `{probe_words}`",
        f"- Checker: `validate_asca` / asca **{asca_version}**",
        (
            f"- Rows: **{total}** (one per inventory row; optional-output "
            "alternatives emit extra rows with distinct `alt_idx`)"
        ),
        "",
        "## Rules",
        f"- OK: **{ok_n}** ({ok_pct:.1f}%)",
        f"- Fail: **{fail_n}** ({fail_pct:.1f}%)",
        f"- Skipped: **{skipped_n}** ({skipped_pct:.1f}%)",
        "",
    ]
    lines.extend(
        format_corrections_section(
            corrections_outcome_stats(rows, correction_rule_ids)
            if correction_rule_ids is not None
            else None
        )
    )
    lines.extend(
        [
            "## Sections",
            "",
            (
                f"- All OK: **{section_outcomes.all_ok} / {section_total}** "
                f"({_section_pct(section_outcomes.all_ok):.1f}%)"
            ),
            (
                f"- Some OK: **{section_outcomes.some_ok} / {section_total}** "
                f"({_section_pct(section_outcomes.some_ok):.1f}%)"
            ),
            (
                f"- None OK: **{section_outcomes.none_ok} / {section_total}** "
                f"({_section_pct(section_outcomes.none_ok):.1f}%)"
            ),
            (
                f"- Sections skipped: **{section_outcomes.skipped} / {section_total}** "
                f"({_section_pct(section_outcomes.skipped):.1f}%)"
            ),
            "",
            "## Failure classes",
            "",
            "| count | failure_class |",
            "|------:|---------------|",
        ]
    )
    for failure_class, count in class_counts.most_common():
        lines.append(f"| {count} | `{failure_class}` |")
    lines.extend(format_common_errors_section(rows))
    if field_isolation_rows is not None:
        lines.extend(format_field_isolation_blame_section(field_isolation_rows))
    lines.extend(
        [
            "## Notes",
            "",
            "- Inventory runs per index rule via `DiachronicSeries` + `validate_asca`.",
            f"- OK rows: [{INVENTORY_SUCCESS_CSV_NAME}]({INVENTORY_SUCCESS_CSV_NAME})",
            f"- Fail rows: [{INVENTORY_ERROR_CSV_NAME}]({INVENTORY_ERROR_CSV_NAME})",
            (
                f"- Skipped rows: "
                f"[{INVENTORY_SKIPPED_CSV_NAME}]({INVENTORY_SKIPPED_CSV_NAME})"
            ),
            (
                f"- `ok` flips (append-only): "
                f"[{INVENTORY_CHANGELOG_CSV_NAME}]({INVENTORY_CHANGELOG_CSV_NAME})"
            ),
            (
                f"- Field blame OK rows: "
                f"[{FIELD_ISOLATION_SUCCESS_CSV_NAME}]({FIELD_ISOLATION_SUCCESS_CSV_NAME})"
            ),
            (
                f"- Field blame fail rows: "
                f"[{FIELD_ISOLATION_ERROR_CSV_NAME}]({FIELD_ISOLATION_ERROR_CSV_NAME})"
            ),
            (
                f"- Field blame skipped rows: "
                f"[{FIELD_ISOLATION_SKIPPED_CSV_NAME}]"
                f"({FIELD_ISOLATION_SKIPPED_CSV_NAME})"
            ),
        ]
    )
    lines.extend(
        [
            f"- {failure_class}: [{csv_name}]({csv_name})"
            for failure_class, csv_name in CLUSTER_CSV_BY_FAILURE_CLASS.items()
        ]
    )
    lines.append("")
    return "\n".join(lines)
