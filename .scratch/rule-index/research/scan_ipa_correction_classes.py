"""Scan expected_ipa, invalid_ipa, expected_range_dots failure classes (spike 114).

Run: uv run python .scratch/rule-index/research/scan_ipa_correction_classes.py
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
INVENTORY_DIR = ROOT / ".scratch/rule-index/inventory"
PARSER_CONFIG = ROOT / "config/parser/parser_config.yml"
OUT_CSV = Path(__file__).with_name("ipa-correction-classes.csv")
OUT_BUCKETS_CSV = Path(__file__).with_name("ipa-correction-buckets.csv")

TARGET_CLASSES = frozenset({"expected_ipa", "invalid_ipa", "expected_range_dots"})
KHOSAN_SECTION_PREFIX = "20."


@dataclass
class Row:
    section_index: str
    section_name: str
    rule_id: str
    failure_class: str
    subcluster: str
    blame: str
    error_token: str
    description: str
    rule: str
    mono_class_section: bool
    section_tag: str
    section_fail_count: int
    section_rule_count: int


def _load_inventory() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for name in (
        "rule-inventory-success.csv",
        "rule-inventory-error.csv",
    ):
        path = INVENTORY_DIR / name
        with path.open(encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def _load_lookup(
    name: str, key_cols: tuple[str, ...]
) -> dict[tuple[str, ...], dict[str, str]]:
    path = INVENTORY_DIR / name
    if not path.is_file():
        return {}
    lookup: dict[tuple[str, ...], dict[str, str]] = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            lookup[tuple(row[col] for col in key_cols)] = row
    return lookup


def _load_skip_sections() -> set[str]:
    if not PARSER_CONFIG.is_file():
        return set()
    data = yaml.safe_load(PARSER_CONFIG.read_text(encoding="utf-8"))
    return {entry["id"] for entry in data.get("skip_sections", []) if "id" in entry}


def _syntax_from_description(description: str) -> str:
    parts = description.split("|")
    return parts[1].strip() if len(parts) > 1 else ""


def classify_expected_ipa(
    description: str,
    error_token: str,
    *,
    aux: dict[str, str] | None,
    blame: str,
) -> str:
    rule = (aux or {}).get("rule", _syntax_from_description(description))
    tok = error_token or "?"
    if tok == "(" or ("(" in rule and tok in ("(", "ʼ", "ʷ", "ʲ", "ˀ")):
        if re.search(r"\([^\)]*[ʷʲʼˀʰʱ]", rule):
            return "paren_optional_modifier"
        if re.search(r"\([^\)]*,", rule) or re.search(r"\{[^}]*\([^)]*\)", rule):
            return "paren_optional_io"
        return "paren_in_segment"
    if tok == "//" or " // " in rule or rule.strip().startswith("//"):
        return "prose_double_slash_env"
    if tok == "/" or re.search(r"\s/\s|/\s*[a-z]", rule):
        return "editorial_slash_gloss"
    if tok == ">":
        return "malformed_chain_or_prose"
    if tok == "∅":
        return "null_in_io_residual"
    if tok in ("ʷ", "ʲ"):
        return "optional_modifier_unwrapped"
    if tok == "ʼ":
        return "ejective_paren_modifier"
    if tok == "…":
        return "ellipsis_prose_comment"
    if tok == "_":
        return "underscore_in_segment"
    if tok == ",":
        return "comma_in_segment"
    if "but received ''" in description:
        return "empty_token_position"
    return f"ipa_received_other:{tok}"


def classify_invalid_ipa(
    description: str,
    error_token: str,
    *,
    section_index: str,
    aux: dict[str, str] | None,
) -> str:
    rule = (aux or {}).get("rule", _syntax_from_description(description))
    match = re.search(r"IPA '([^']*)'", description)
    ipa_tok = match.group(1) if match else error_token or "?"
    if ipa_tok == "ⁿ" or "ⁿ" in rule:
        return "prenasal_prefix"
    if ipa_tok in ("ǃ", "ǀ", "ǁ", "ǂ") or section_index.startswith(
        KHOSAN_SECTION_PREFIX
    ):
        return f"khoisan_click:{ipa_tok}"
    if "!" in rule or ipa_tok.startswith("!"):
        return "khoisan_bang_notation"
    return f"invalid_ipa_other:{ipa_tok}"


def classify_expected_range_dots(
    description: str,
    error_token: str,
    *,
    aux: dict[str, str] | None,
    section_index: str,
) -> str:
    rule = (aux or {}).get("rule", _syntax_from_description(description))
    if section_index.startswith("24."):
        return "yupik_geminate_dot_range"
    if re.search(r"[a-zA-Z]\.[a-zA-Zɕʂʃʒ]", rule) or re.search(
        r"[ptk][.][sʃʂɕʒ]", rule
    ):
        return "european_dot_affricate"
    if re.search(r"\{[^}]*\.[^}]*\}", rule):
        return "dot_inside_set"
    if re.search(r"[a-z]\.[a-z]", rule):
        return "dot_vowel_or_consonant"
    if section_index.startswith(("17.10", "36.3")):
        return "european_dot_affricate"
    return f"range_dots_other:{error_token or '?'}"


def classify(
    failure_class: str,
    description: str,
    *,
    error_token: str = "",
    section_index: str = "",
    aux: dict[str, str] | None = None,
    blame: str = "",
) -> str:
    if failure_class == "expected_ipa":
        return classify_expected_ipa(description, error_token, aux=aux, blame=blame)
    if failure_class == "invalid_ipa":
        return classify_invalid_ipa(
            description, error_token, section_index=section_index, aux=aux
        )
    if failure_class == "expected_range_dots":
        return classify_expected_range_dots(
            description,
            error_token,
            aux=aux,
            section_index=section_index,
        )
    return failure_class


def section_tag(
    section_index: str,
    *,
    fail_count: int,
    rule_count: int,
    skipped: bool,
) -> str:
    if skipped:
        return "skipped"
    if rule_count > 10 and fail_count / rule_count >= 0.5:
        return "heavy-section"
    if 1 <= fail_count <= 3:
        return "near-miss"
    return "other"


def main() -> int:
    rows = _load_inventory()
    skip_sections = _load_skip_sections()
    blame_lookup = _load_lookup(
        "field-isolation-error.csv",
        ("section_index", "rule_id", "alt_idx"),
    )
    expected_ipa_lookup = _load_lookup(
        "expected_ipa_errors.csv",
        ("section_index", "rule_id"),
    )
    invalid_ipa_lookup = _load_lookup(
        "invalid_ipa_errors.csv",
        ("section_index", "rule_id"),
    )
    range_dots_lookup = _load_lookup(
        "expected_range_dots_errors.csv",
        ("section_index", "rule_id"),
    )

    section_rules: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("failure_class") == "section_skipped":
            continue
        section_rules[row["section_index"]].append(row)

    section_fail_count = {
        sec: sum(1 for rule in rules if rule["ok"] == "False")
        for sec, rules in section_rules.items()
    }
    section_rule_count = {sec: len(rules) for sec, rules in section_rules.items()}

    active_sections = {
        sec
        for sec, rules in section_rules.items()
        if sec not in skip_sections
        and not any(r.get("failure_class") == "section_skipped" for r in rules)
    }

    def mono_class_sections_for(target: tuple[str, str]) -> set[str]:
        completed: set[str] = set()
        for sec in active_sections:
            fails = [rule for rule in section_rules[sec] if rule["ok"] == "False"]
            if not fails:
                continue
            keys = set()
            for rule in fails:
                fc = rule["failure_class"]
                aux = None
                if fc == "expected_ipa":
                    aux = expected_ipa_lookup.get(
                        (rule["section_index"], rule["rule_id"])
                    )
                elif fc == "invalid_ipa":
                    aux = invalid_ipa_lookup.get(
                        (rule["section_index"], rule["rule_id"])
                    )
                elif fc == "expected_range_dots":
                    aux = range_dots_lookup.get(
                        (rule["section_index"], rule["rule_id"])
                    )
                key = (
                    fc,
                    classify(
                        fc,
                        rule.get("description", ""),
                        error_token=rule.get("error_token", ""),
                        section_index=rule["section_index"],
                        aux=aux,
                        blame=blame_lookup.get(
                            (
                                rule["section_index"],
                                rule["rule_id"],
                                rule.get("alt_idx", ""),
                            ),
                            {},
                        ).get("blame", ""),
                    ),
                )
                keys.add(key)
            if keys == {target}:
                completed.add(sec)
        return completed

    classified: list[Row] = []
    for row in rows:
        failure_class = row.get("failure_class", "")
        if failure_class not in TARGET_CLASSES or row.get("ok") != "False":
            continue
        sec = row["section_index"]
        key = (row["section_index"], row["rule_id"], row.get("alt_idx", ""))
        blame_row = blame_lookup.get(key, {})
        aux = None
        if failure_class == "expected_ipa":
            aux = expected_ipa_lookup.get((row["section_index"], row["rule_id"]))
        elif failure_class == "invalid_ipa":
            aux = invalid_ipa_lookup.get((row["section_index"], row["rule_id"]))
        elif failure_class == "expected_range_dots":
            aux = range_dots_lookup.get((row["section_index"], row["rule_id"]))
        subcluster = classify(
            failure_class,
            row.get("description", ""),
            error_token=row.get("error_token", ""),
            section_index=sec,
            aux=aux,
            blame=blame_row.get("blame", ""),
        )
        fail_count = section_fail_count.get(sec, 0)
        rule_count = section_rule_count.get(sec, 0)
        skipped = sec in skip_sections
        classified.append(
            Row(
                section_index=sec,
                section_name=row["section_name"],
                rule_id=row["rule_id"],
                failure_class=failure_class,
                subcluster=subcluster,
                blame=blame_row.get("blame", ""),
                error_token=row.get("error_token", ""),
                description=row.get("description", ""),
                rule=(aux or {}).get(
                    "rule", _syntax_from_description(row.get("description", ""))
                ),
                mono_class_section=False,
                section_tag=section_tag(
                    sec,
                    fail_count=fail_count,
                    rule_count=rule_count,
                    skipped=skipped,
                ),
                section_fail_count=fail_count,
                section_rule_count=rule_count,
            )
        )

    mono_class_all: set[str] = set()
    for sec in active_sections:
        fails = [rule for rule in section_rules[sec] if rule["ok"] == "False"]
        if not fails:
            continue
        classes = {rule["failure_class"] for rule in fails}
        if len(classes) == 1 and classes.pop() in TARGET_CLASSES:
            mono_class_all.add(sec)

    for row in classified:
        row.mono_class_section = row.section_index in mono_class_all

    by_bucket: dict[tuple[str, str], list[Row]] = defaultdict(list)
    for row in classified:
        by_bucket[(row.failure_class, row.subcluster)].append(row)

    bucket_stats: list[dict[str, object]] = []
    for (failure_class, subcluster), items in by_bucket.items():
        complete_secs = mono_class_sections_for((failure_class, subcluster))
        near_miss_secs = {
            item.section_index for item in items if item.section_tag == "near-miss"
        }
        heavy_secs = {
            item.section_index for item in items if item.section_tag == "heavy-section"
        }
        bucket_stats.append(
            {
                "sections_complete": len(complete_secs),
                "sections_touched": len({item.section_index for item in items}),
                "rules": len(items),
                "failure_class": failure_class,
                "subcluster": subcluster,
                "near_miss_sections": len(near_miss_secs),
                "heavy_sections": len(heavy_secs),
                "complete_section_ids": ";".join(sorted(complete_secs)),
            }
        )
    bucket_stats.sort(
        key=lambda item: (
            item["sections_complete"],
            item["rules"],
        ),
        reverse=True,
    )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "section_index",
                "section_name",
                "rule_id",
                "failure_class",
                "subcluster",
                "blame",
                "error_token",
                "mono_class_section",
                "section_tag",
                "section_fail_count",
                "section_rule_count",
                "rule",
                "description",
            ]
        )
        for row in classified:
            writer.writerow(
                [
                    row.section_index,
                    row.section_name,
                    row.rule_id,
                    row.failure_class,
                    row.subcluster,
                    row.blame,
                    row.error_token,
                    row.mono_class_section,
                    row.section_tag,
                    row.section_fail_count,
                    row.section_rule_count,
                    row.rule,
                    row.description,
                ]
            )

    with OUT_BUCKETS_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sections_complete",
                "sections_touched",
                "rules",
                "failure_class",
                "subcluster",
                "near_miss_sections",
                "heavy_sections",
                "complete_section_ids",
            ],
        )
        writer.writeheader()
        writer.writerows(bucket_stats)

    mono_by_class: dict[str, int] = defaultdict(int)
    for sec in mono_class_all:
        fails = [r for r in section_rules[sec] if r["ok"] == "False"]
        if fails:
            mono_by_class[fails[0]["failure_class"]] += 1

    print(f"wrote {OUT_CSV} ({len(classified)} rows)")
    print(f"wrote {OUT_BUCKETS_CSV} ({len(bucket_stats)} buckets)")
    print(
        "mono_class_sections:",
        {cls: mono_by_class[cls] for cls in sorted(TARGET_CLASSES)},
    )
    print("top_buckets:")
    for item in bucket_stats[:30]:
        print(
            f"  {item['sections_complete']:3d} complete | "
            f"{item['sections_touched']:3d} secs | "
            f"{item['rules']:3d} rules | "
            f"nm={item['near_miss_sections']} heavy={item['heavy_sections']} | "
            f"{item['failure_class']} :: {item['subcluster']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
