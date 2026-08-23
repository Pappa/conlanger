"""Ingest reporting helpers for cleaned-index regeneration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
