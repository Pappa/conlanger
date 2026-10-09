"""CSV I/O helpers for inventory and debug outputs (no config loading)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from conlanger.ingest.models.mappings import ManualMappingMatch

MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS = [
    "section_index",
    "section_name",
    "rule_id",
    "source",
    "from_text",
    "to_text",
]
MANUAL_MAPPINGS_MATCHED_CSV_NAME = "manual_mappings_matched_rules.csv"


_RULE_COMMENT_QUALIFIER_PHRASES = (
    "short only",
    "long only",
    "when unstressed",
    "when stressed",
    "except as below",
    "sporadic",
    "sometimes",
    "not sure",
    "not universal",
    "short vowel",
    "unstressed",
)


def write_rule_comment_phrase_summary(doc: dict[str, Any], path: Path) -> int:
    """Write qualifier-phrase counts from index rule ``comment`` fields."""
    comments: list[str] = []
    for section in doc.get("sections") or []:
        for rule in section.get("rules") or []:
            comment = rule.get("comment")
            if comment:
                comments.append(str(comment))

    phrase_counts: dict[str, int] = {}
    for phrase in _RULE_COMMENT_QUALIFIER_PHRASES:
        count = sum(1 for comment in comments if phrase.lower() in comment.lower())
        if count:
            phrase_counts[phrase] = count

    semicolon_count = sum(1 for comment in comments if ";" in comment)

    lines = [
        "# Rule comment phrase summary",
        "",
        f"- Corpus rules with **`comment`**: **{len(comments)}**",
        f"- Comments containing ``; `` (semicolon tails): **{semicolon_count}**",
        "",
        "## Qualifier phrases",
        "",
        "| phrase | rules |",
        "| --- | ---: |",
    ]
    for phrase, count in sorted(
        phrase_counts.items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"| `{phrase}` | {count} |")

    if not phrase_counts:
        lines.append("| _(none matched)_ | 0 |")

    lines.extend(
        [
            "",
            "## Sample comments (first 10)",
            "",
        ]
    )
    for comment in comments[:10]:
        lines.append(f"- {comment}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(comments)


def write_csv_rows(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    """Write string rows to CSV with an explicit column order."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(path, index=False)


def write_manual_mappings_matched_csv(
    matches: list[ManualMappingMatch],
    path: Path,
) -> Path:
    """Rewrite debug CSV of manual mapping hits (one row per applied pattern)."""
    rows = [match.model_dump() for match in matches]
    write_csv_rows(path, rows, MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS)
    return Path(path)
