"""Validation inventory for cleaned rule corpus (ticket 12)."""

from __future__ import annotations

import csv
import re
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from conlanger.tools.asca_validator import ASCAValidationError, validate_asca
from conlanger.tools.rules import RuleChange, SoundChangeRuleSet

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
            "description": self.description,
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
    asca_bin: Path | None,
) -> ValidationRow:
    section_index = str(section.get("index", ""))
    section_name = str(section.get("section", ""))
    source = str(rule.get("source", ""))

    if rule.get("skipped"):
        err = str(rule["skipped"])
        failure_class = "missing_arrow"
        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_idx=rule_idx,
            source=source,
            ok=False,
            failure_class=failure_class,
            reason=reason_for_failure(failure_class, err),
            description=err,
        )

    try:
        RuleChange(rule, format="asca")
    except (KeyError, ValueError) as exc:
        err = f"format_error: {exc}"
        failure_class = "format_error"
        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_idx=rule_idx,
            source=source,
            ok=False,
            failure_class=failure_class,
            reason=reason_for_failure(failure_class, err),
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
            description="held-out (commented rule)",
        )

    mini = _mini_section(section, rule, rule_idx)
    try:
        validate_asca(
            SoundChangeRuleSet(mini),
            probe_words=probe_words,
            asca_bin=asca_bin,
        )
    except ASCAValidationError as exc:
        err = str(exc)
        failure_class = classify_error(err)
        return ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_idx=rule_idx,
            source=source,
            ok=False,
            failure_class=failure_class,
            reason=reason_for_failure(failure_class, err),
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
        description="",
    )


def iter_validation_rows(
    doc: dict[str, Any],
    *,
    probe_words: Path | None,
    asca_bin: Path | None,
) -> Iterator[ValidationRow]:
    for section in doc.get("sections") or []:
        rules = section.get("rules") or []
        for rule_idx, rule in enumerate(rules):
            yield validate_corpus_rule(
                section,
                rule,
                rule_idx,
                probe_words=probe_words,
                asca_bin=asca_bin,
            )


def write_validation_csv(rows: list[ValidationRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "section_index",
        "section_name",
        "rule_idx",
        "source",
        "ok",
        "failure_class",
        "reason",
        "description",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_csv_dict())


def summarize_inventory(
    rows: list[ValidationRow],
    *,
    source_yaml: str,
    probe_words: str,
    asca_version: str = "0.10.2",
) -> str:
    total = len(rows)
    ok_n = sum(1 for row in rows if row.ok)
    fail_n = total - ok_n
    ok_pct = (100.0 * ok_n / total) if total else 0.0
    fail_pct = (100.0 * fail_n / total) if total else 0.0

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
        "",
        "## Failure classes",
        "",
        "| count | failure_class |",
        "|------:|---------------|",
    ]
    for failure_class, count in class_counts.most_common():
        lines.append(f"| {count} | `{failure_class}` |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.",
            "- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)",
            "",
        ]
    )
    return "\n".join(lines)
