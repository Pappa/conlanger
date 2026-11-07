"""Reclassify ``expected_underscore`` inventory rows after syllable compile (0046–0048).

Reads ``rule-inventory-error.csv`` and joins the 0045 triplet CSV. Syllable families
F1–F4 are **overridden** to U2–U4 when the compiled rule no longer contains a bare
``U[±F]`` / ``%[±F]`` host (underline-scope projection already applied).

Writes ``0050-expected-underscore-post-syllable-summary.json`` beside this script.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INVENTORY_ERROR = ROOT / "diagnostics/inventory/rule-inventory-error.csv"
TRIPLETS = Path(__file__).resolve().parent / "0045-expected-underscore-triplets.csv"
OUT_JSON = Path(__file__).resolve().parent / (
    "0050-expected-underscore-post-syllable-summary.json"
)

_BARE_SYLLABLE_HOST_RE = re.compile(
    r"(?<![<(])(?:U|%)(?:\[[^\]]+\])+",
)


def _base_rule_id(rule_id: str) -> str:
    return rule_id.split(",")[0].strip()


def _load_triplets() -> dict[str, dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    with TRIPLETS.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rid = row["rule_id"].strip()
            by_id[_base_rule_id(rid)] = row
            if "," not in rid:
                by_id[rid] = row
    return by_id


def post_syllable_fix_family(
    *,
    original: str,
    compiled_rule: str,
    error_token: str | None,
) -> str:
    """Map legacy F-family labels to U-families when syllable compile is no longer the gap."""
    if not original.startswith("F"):
        return original
    if _BARE_SYLLABLE_HOST_RE.search(compiled_rule):
        return original
    if original.startswith("F4") or "//" in compiled_rule or error_token == "//":
        return "U3-double-slash-index"
    if error_token == "}:" or original.startswith("F3"):
        return "U4-env-set-prose-delimiter"
    if " else" in compiled_rule or compiled_rule.rstrip().endswith("else"):
        return "U1-bare-else-prose"
    return "U2-index-prose-env"


def main() -> None:
    triplets = _load_triplets()
    rows = [
        row
        for row in csv.DictReader(INVENTORY_ERROR.open(encoding="utf-8"))
        if row.get("failure_class") == "expected_underscore"
    ]
    by_original: Counter[str] = Counter()
    by_post: Counter[str] = Counter()
    syllable_family_remaining = 0
    detail: list[dict[str, str]] = []

    for row in rows:
        rule_id = row["rule_id"]
        trip = triplets.get(rule_id) or triplets.get(_base_rule_id(rule_id))
        original = (trip or {}).get("fix_family", "unknown")
        compiled = row.get("rule", "")
        error_token = row.get("error_token") or ""
        post = post_syllable_fix_family(
            original=original,
            compiled_rule=compiled,
            error_token=error_token,
        )
        by_original[original] += 1
        by_post[post] += 1
        if post.startswith("F"):
            syllable_family_remaining += 1
        detail.append(
            {
                "rule_id": rule_id,
                "fix_family_0045": original,
                "fix_family_post_syllable": post,
                "error_token": error_token,
            }
        )

    payload = {
        "expected_underscore_rows": len(rows),
        "syllable_family_F1_F4_remaining": syllable_family_remaining,
        "by_fix_family_0045": dict(sorted(by_original.items())),
        "by_fix_family_post_syllable": dict(sorted(by_post.items())),
        "rows": detail,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)} rows={len(rows)} F-remaining={syllable_family_remaining}")


if __name__ == "__main__":
    main()
