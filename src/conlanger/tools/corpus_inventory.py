"""Validation inventory for cleaned rule corpus (ticket 12)."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from conlanger.appliers.asca import ASCAValidationError, validate_asca
from conlanger.tools.rules import DiachronicSeries, SoundChangeRule
from conlanger.utils.parsing import ARROW

ERROR_CLASS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("nested_brackets", re.compile(r"nested brackets", re.IGNORECASE)),
    ("unknown_feature", re.compile(r"Unknown feature", re.IGNORECASE)),
    ("unknown_grouping", re.compile(r"Unknown grouping", re.IGNORECASE)),
    (
        "prose_or_expected_arrow",
        re.compile(r"Expected '>|Expected '->'|Expected '=>'", re.IGNORECASE),
    ),
    ("expected_underscore", re.compile(r"Expected '_'", re.IGNORECASE)),
    ("stuff_after_word_bound", re.compile(r"after the end of a word", re.IGNORECASE)),
    (
        "diacritic_prereq",
        re.compile(r"prerequisite properties.*diacritic", re.IGNORECASE),
    ),
    (
        "empty_io_panic",
        re.compile(
            r"Output is not empty|Input is empty|Output is empty", re.IGNORECASE
        ),
    ),
    (
        "runtime_delete_only_segment",
        re.compile(r"Can't delete a word's only segment", re.IGNORECASE),
    ),
    ("expected_number", re.compile(r"Expected number", re.IGNORECASE)),
    ("unknown_character", re.compile(r"Unknown character", re.IGNORECASE)),
    ("malformed_comment", re.compile(r"Malformed Comment", re.IGNORECASE)),
    ("missing_arrow", re.compile(r"missing separator", re.IGNORECASE)),
    ("format_error", re.compile(r"format_error", re.IGNORECASE)),
]

REASON_VOCABULARY = (
    "trailing-comment",
    "broken-syntax",
    "asca-unrepresentable",
    "valid-but-inaccurate",
    "other",
)

_UNKNOWN_TOKEN_RE = re.compile(
    r"Unknown (?:feature|grouping|character) '([^']+)'",
    re.IGNORECASE,
)
_DID_YOU_MEAN_RE = re.compile(r"Did you mean ([^?]+)\?", re.IGNORECASE)

COMMON_ERROR_CLASSES = (
    "unknown_character",
    "unknown_feature",
    "unknown_grouping",
)

VALIDATION_CSV_COLUMNS = [
    "section_index",
    "section_name",
    "rule_idx",
    "source",
    "ok",
    "failure_class",
    "reason",
    "error_token",
    "suggested",
    "description",
]

CHANGELOG_CSV_COLUMNS = [
    "section_index",
    "rule_idx",
    "source",
    "ok",
    "timestamp",
]

INVENTORY_CSV_NAME = "asca-rule-inventory.csv"
INVENTORY_SUCCESS_CSV_NAME = "asca-rule-inventory-success.csv"
INVENTORY_ERROR_CSV_NAME = "asca-rule-inventory-error.csv"
INVENTORY_CHANGELOG_CSV_NAME = "asca-rule-inventory-changelog.csv"
OMITTED_DESCRIPTIONS = {"panic_other"}


def _ok_as_bool(series: pd.Series) -> pd.Series:
    """Normalize inventory ``ok`` values (bool or CSV strings) to bool."""
    return series.astype(str).str.lower().isin({"true", "1"})


def validation_rows_to_dataframe(rows: list[ValidationRow]) -> pd.DataFrame:
    """Return validation rows as a DataFrame with a stable column order."""
    if not rows:
        return pd.DataFrame(columns=VALIDATION_CSV_COLUMNS)
    return pd.DataFrame(
        [row.as_csv_dict() for row in rows], columns=VALIDATION_CSV_COLUMNS
    )


def filter_inventory_by_ok(df: pd.DataFrame, *, ok: bool) -> pd.DataFrame:
    """Return inventory rows whose ``ok`` column matches ``ok``."""
    if df.empty:
        return df.copy()
    mask = _ok_as_bool(df["ok"])
    if not ok:
        mask = ~mask
    return df.loc[mask].reset_index(drop=True)


def ok_flip_changelog_rows(
    previous: pd.DataFrame | None,
    current: pd.DataFrame,
    *,
    timestamp: str,
) -> pd.DataFrame:
    """Return changelog rows for rules whose ``ok`` flipped vs ``previous``.

    Matching is by ``source``. When ``previous`` is missing or empty, no flips
    are emitted (first-run behaviour). ``timestamp`` is copied onto every row.
    """
    empty = pd.DataFrame(columns=CHANGELOG_CSV_COLUMNS)
    if previous is None or previous.empty or current.empty:
        return empty
    prev = previous.loc[:, ["source", "ok"]].drop_duplicates(
        subset=["source"], keep="last"
    )
    prev = prev.assign(ok=_ok_as_bool(prev["ok"])).set_index("source")["ok"]
    cur = current.loc[:, ["section_index", "rule_idx", "source", "ok"]].copy()
    cur["ok"] = _ok_as_bool(cur["ok"])
    cur = cur.drop_duplicates(subset=["source"], keep="last")
    merged = cur.join(prev.rename("prev_ok"), on="source", how="inner")
    flipped = merged.loc[merged["ok"] != merged["prev_ok"]].copy()
    if flipped.empty:
        return empty
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
    limit: int | None = 5,
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


def top_error_tokens_with_suggested_from_dataframe(
    df: pd.DataFrame,
    failure_class: str,
    *,
    limit: int | None = 5,
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
    for failure_class in COMMON_ERROR_CLASSES:
        show_all = failure_class in {"unknown_feature", "unknown_grouping"}
        token_limit = None if show_all else 5
        if failure_class == "unknown_feature":
            lines.extend(
                [
                    f"### {failure_class}",
                    "",
                    "| count | error_token | suggested |",
                    "|------:|-------------|-----------|",
                ]
            )
            top = top_error_tokens_with_suggested_from_dataframe(
                df, failure_class, limit=token_limit
            )
            if top:
                for token, count, suggested in top:
                    suggested_cell = f"`{suggested}`" if suggested else "—"
                    lines.append(f"| {count} | `{token}` | {suggested_cell} |")
            else:
                lines.append("| — | _(none)_ | — |")
        else:
            lines.extend(
                [
                    f"### {failure_class}",
                    "",
                    "| count | error_token |",
                    "|------:|-------------|",
                ]
            )
            top = top_error_tokens_from_dataframe(df, failure_class, limit=token_limit)
            if top:
                for token, count in top:
                    lines.append(f"| {count} | `{token}` |")
            else:
                lines.append("| — | _(none)_ |")
        lines.append("")
    return lines


def parse_unknown_token_error(error: str) -> tuple[str, str]:
    """Extract unknown token and ASCA suggestion from a validation error string."""
    token_match = _UNKNOWN_TOKEN_RE.search(error)
    error_token = token_match.group(1) if token_match else ""
    suggest_match = _DID_YOU_MEAN_RE.search(error)
    suggested = suggest_match.group(1).strip() if suggest_match else ""
    return error_token, suggested


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


def reason_for_failure(failure_class: str, error: str) -> str:
    if failure_class in {"malformed_comment", "trailing-comment"}:
        return "trailing-comment"
    if failure_class in {"missing_arrow", "format_error"}:
        return "broken-syntax"
    if failure_class in {"prose_or_expected_arrow", "unknown_character"}:
        return "asca-unrepresentable"
    if failure_class == "valid-but-inaccurate":
        return "valid-but-inaccurate"
    if failure_class.startswith(("syntax_", "runtime_", "panic_", "other")):
        return "broken-syntax"
    if failure_class in {
        "unknown_feature",
        "unknown_grouping",
        "nested_brackets",
        "expected_underscore",
        "stuff_after_word_bound",
        "diacritic_prereq",
        "empty_io_panic",
        "runtime_delete_only_segment",
        "expected_number",
    }:
        return "asca-unrepresentable"
    return "other"


@dataclass(frozen=True)
class ValidationRow:
    section_index: str
    section_name: str
    rule_idx: int
    source: str
    ok: bool
    failure_class: str
    reason: str
    error_token: str
    suggested: str
    description: str

    def as_csv_dict(self) -> dict[str, str | int | bool]:
        return {
            "section_index": self.section_index,
            "section_name": self.section_name,
            "rule_idx": self.rule_idx,
            "source": self.source,
            "ok": self.ok,
            "failure_class": self.failure_class,
            "reason": self.reason,
            "error_token": self.error_token,
            "suggested": self.suggested,
            "description": "thread panicked"
            if self.failure_class in OMITTED_DESCRIPTIONS
            else self.description,
        }


def _mini_section(
    section: dict[str, Any], rule: dict[str, Any], rule_idx: int
) -> dict[str, Any]:
    return {
        "index": section.get("index", ""),
        "section": f"{section.get('section', '')}#{rule_idx}",
        "rules": [rule],
    }


def validate_corpus_rule(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_idx: int,
    *,
    probe_words: Path | None,
    group_mappings: dict[str, str] | None = None,
) -> ValidationRow:
    section_index = str(section.get("index", ""))
    section_name = str(section.get("section", ""))
    source = str(rule.get("source", ""))

    if rule.get("status") == "skipped":
        raw = str(rule.get("raw", ""))
        if "→" not in raw and ARROW not in raw:
            err = f"missing separator {ARROW!r}"
        else:
            err = str(rule.get("comment") or "quoted prose paragraph")
        failure_class = "missing_arrow"
        error_token, suggested = parse_unknown_token_error(err)
        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_idx=rule_idx,
            source=source,
            ok=False,
            failure_class=failure_class,
            reason=reason_for_failure(failure_class, err),
            error_token=error_token,
            suggested=suggested,
            description=err,
        )

    mini = _mini_section(section, rule, rule_idx)
    try:
        scr = DiachronicSeries(mini, group_mappings=group_mappings)
    except (KeyError, ValueError) as exc:
        err = f"format_error: {exc}"
        failure_class = "format_error"
        error_token, suggested = parse_unknown_token_error(err)
        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_idx=rule_idx,
            source=source,
            ok=False,
            failure_class=failure_class,
            reason=reason_for_failure(failure_class, err),
            error_token=error_token,
            suggested=suggested,
            description=err,
        )

    if not any(isinstance(part, SoundChangeRule) for part in scr._parts):
        err = "format_error: no compile steps from stages"
        failure_class = "format_error"
        error_token, suggested = parse_unknown_token_error(err)
        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_idx=rule_idx,
            source=source,
            ok=False,
            failure_class=failure_class,
            reason=reason_for_failure(failure_class, err),
            error_token=error_token,
            suggested=suggested,
            description=err,
        )

    if rule.get("skip"):
        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_idx=rule_idx,
            source=source,
            ok=True,
            failure_class="",
            reason="",
            error_token="",
            suggested="",
            description="held-out (commented rule)",
        )

    try:
        validate_asca(
            scr,
            probe_words=probe_words,
        )
    except ASCAValidationError as exc:
        err = str(exc)
        failure_class = classify_error(err)
        error_token, suggested = parse_unknown_token_error(err)
        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_idx=rule_idx,
            source=source,
            ok=False,
            failure_class=failure_class,
            reason=reason_for_failure(failure_class, err),
            error_token=error_token,
            suggested=suggested,
            description=err,
        )

    return ValidationRow(
        section_index=section_index,
        section_name=section_name,
        rule_idx=rule_idx,
        source=source,
        ok=True,
        failure_class="",
        reason="",
        error_token="",
        suggested="",
        description="",
    )


def iter_validation_rows(
    doc: dict[str, Any],
    *,
    probe_words: Path | None,
    group_mappings: dict[str, str] | None = None,
) -> Iterator[ValidationRow]:
    for section in doc.get("sections") or []:
        rules = section.get("rules") or []
        for rule_idx, rule in enumerate(rules):
            yield validate_corpus_rule(
                section,
                rule,
                rule_idx,
                probe_words=probe_words,
                group_mappings=group_mappings,
            )


def write_validation_csv(rows: list[ValidationRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    validation_rows_to_dataframe(rows).to_csv(path, index=False)


def load_inventory_csv(path: Path) -> pd.DataFrame | None:
    """Load a prior inventory CSV, or ``None`` when the file is absent."""
    if not path.is_file():
        return None
    return pd.read_csv(path)


def write_filtered_inventory_csvs(df: pd.DataFrame, inventory_dir: Path) -> None:
    """Rewrite success/error filtered inventory CSVs under ``inventory_dir``."""
    inventory_dir.mkdir(parents=True, exist_ok=True)
    filter_inventory_by_ok(df, ok=True).to_csv(
        inventory_dir / INVENTORY_SUCCESS_CSV_NAME, index=False
    )
    filter_inventory_by_ok(df, ok=False).to_csv(
        inventory_dir / INVENTORY_ERROR_CSV_NAME, index=False
    )


def append_ok_flip_changelog(flips: pd.DataFrame, path: Path) -> int:
    """Append ``ok``-flip rows to the changelog CSV. Returns rows written."""
    if flips.empty:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.is_file()
    flips.to_csv(path, mode="a", header=write_header, index=False)
    return len(flips)


def section_all_ok_stats(rows: list[ValidationRow]) -> tuple[int, int, float]:
    """Return count of sections with every rule ok, total sections, and percentage."""
    by_section: dict[tuple[str, str], list[bool]] = {}
    for row in rows:
        key = (row.section_index, row.section_name)
        by_section.setdefault(key, []).append(row.ok)
    total_sections = len(by_section)
    sections_all_ok = sum(1 for oks in by_section.values() if oks and all(oks))
    pct = (100.0 * sections_all_ok / total_sections) if total_sections else 0.0
    return sections_all_ok, total_sections, pct


def section_all_ok_stats_from_dataframe(df: pd.DataFrame) -> tuple[int, int, float]:
    """Return section all-ok stats from an inventory CSV dataframe."""
    if df.empty:
        return 0, 0, 0.0
    grouped = df.groupby(["section_index", "section_name"], sort=False)["ok"]
    total_sections = grouped.ngroups
    sections_all_ok = int(grouped.all().sum())
    pct = (100.0 * sections_all_ok / total_sections) if total_sections else 0.0
    return sections_all_ok, total_sections, pct


def summarize_inventory(
    rows: list[ValidationRow],
    *,
    source_yaml: str,
    probe_words: str,
    asca_version: str = "0.10.x",
) -> str:
    total = len(rows)
    ok_n = sum(1 for row in rows if row.ok)
    fail_n = total - ok_n
    ok_pct = (100.0 * ok_n / total) if total else 0.0
    fail_pct = (100.0 * fail_n / total) if total else 0.0
    sections_all_ok, section_total, section_ok_pct = section_all_ok_stats(rows)

    class_counts = Counter(
        row.failure_class for row in rows if not row.ok and row.failure_class
    )

    lines = [
        "# Cleaned rule corpus — ASCA validation inventory",
        "",
        f"- Source YAML: `{source_yaml}`",
        f"- Probe words: `{probe_words}`",
        f"- Checker: `validate_asca` / asca **{asca_version}**",
        f"- Rows: **{total}** (one per corpus rule)",
        f"- OK: **{ok_n}** ({ok_pct:.1f}%)",
        f"- Fail: **{fail_n}** ({fail_pct:.1f}%)",
        f"- Sections all OK: **{sections_all_ok} / {section_total}** ({section_ok_pct:.1f}%)",
        "",
        "## Failure classes",
        "",
        "| count | failure_class |",
        "|------:|---------------|",
    ]
    for failure_class, count in class_counts.most_common():
        lines.append(f"| {count} | `{failure_class}` |")
    lines.extend(format_common_errors_section(rows))
    lines.extend(
        [
            "## Notes",
            "",
            "- Inventory runs per corpus rule via `DiachronicSeries` + `validate_asca`.",
            f"- Full rows: [{INVENTORY_CSV_NAME}]({INVENTORY_CSV_NAME})",
            f"- OK rows: [{INVENTORY_SUCCESS_CSV_NAME}]({INVENTORY_SUCCESS_CSV_NAME})",
            f"- Fail rows: [{INVENTORY_ERROR_CSV_NAME}]({INVENTORY_ERROR_CSV_NAME})",
            (
                f"- `ok` flips (append-only): "
                f"[{INVENTORY_CHANGELOG_CSV_NAME}]({INVENTORY_CHANGELOG_CSV_NAME})"
            ),
            "",
        ]
    )
    return "\n".join(lines)
