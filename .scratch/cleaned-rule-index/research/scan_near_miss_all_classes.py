"""Scan all failure classes in ≤3-fail sections (spike 106).

Run: uv run python .scratch/cleaned-rule-index/research/scan_near_miss_all_classes.py
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INVENTORY_DIR = ROOT / ".scratch/cleaned-rule-index/inventory"
OUT_CSV = Path(__file__).with_name("near-miss-all-classes.csv")


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
    mono_class_section: bool


def _load_inventory() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for name in (
        "asca-rule-inventory-success.csv",
        "asca-rule-inventory-error.csv",
    ):
        path = INVENTORY_DIR / name
        with path.open(encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def _load_lookup(name: str, key_cols: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
    path = INVENTORY_DIR / name
    if not path.is_file():
        return {}
    lookup: dict[tuple[str, ...], dict[str, str]] = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            lookup[tuple(row[col] for col in key_cols)] = row
    return lookup


def _syntax_from_description(description: str) -> str:
    parts = description.split("|")
    return parts[1].strip() if len(parts) > 1 else ""


def classify_syntax_other(description: str) -> str:
    syntax = _syntax_from_description(description)
    if "insertion rule must only contain" in description:
        return "insertion_wildcard_input"
    if "Cannot have segments before the beginning" in description:
        if "%#" in syntax or "#%" in syntax:
            return "word_edge_percent_hash"
        return "segments_before_word_beg_other"
    if "Expected end of line" in description and "forget a '/'" in description:
        return "missing_slash_output_env"
    if "Floating diacritic" in description:
        return "floating_glottal_diacritic"
    if "Could not get value of IPA" in description:
        tok = re.search(r"IPA '([^']*)'", description)
        return f"click_or_exotic_ipa:{tok.group(1) if tok else '?'}"
    if "Expected '..'" in description:
        return "expected_range_dots"
    if "Cannot have multiple underlines" in description:
        return "multiple_underlines_env"
    if "Negation cannot be used in the output" in description:
        return "negation_in_output"
    if "Tones cannot be ±" in description:
        return "tone_negation"

    match = re.search(r"Expected an IPA character.*received '([^']*)'", description)
    if match:
        tok = match.group(1)
        if tok == "∅":
            if "{∅" in syntax or ",∅" in syntax:
                return "null_in_parallel_output_set"
            return "null_other_position"
        if tok == "*":
            return "wildcard_in_correspondence_set"
        if tok == "_":
            if "_{}" in syntax or "{i_" in syntax or "C_" in syntax:
                return "underscore_env_shorthand"
            return "underscore_other"
        if tok in ("ʷ", "ʲ", "ʰ", "ʱ"):
            return "superscript_segment_modifier"
        if tok == "(":
            return "paren_in_segment_residual"
        if tok == "ʼ":
            return "ejective_modifier_residual"
        if tok == ">":
            return "chain_in_wrong_position"
        if tok == "/":
            return "slash_in_segment"
        return f"ipa_received_other:{tok}"
    return "other_syntax"


def classify_expected_underscore(description: str, aux: dict[str, str] | None) -> str:
    if "Cannot have multiple underlines" in description:
        return "multiple_underlines"
    rule = (aux or {}).get("rule", _syntax_from_description(description))
    if " // " in rule or rule.strip().startswith("//"):
        return "double_slash_no_underscore"
    lower = rule.lower()
    if " else" in lower or lower.endswith("else"):
        return "prose_else_env"
    if any(
        phrase in lower
        for phrase in (
            "medial",
            "syllable-final",
            "monosyllab",
            "odd syllable",
            "adjacent",
            "typically near",
            "not universal",
        )
    ):
        return "prose_position_env"
    if re.search(r":\{[^}]*\}:", rule):
        return "env_set_no_underscore"
    if "received ''" in description:
        return "missing_underscore_other"
    return "other_underscore"


def classify_unknown_character(error_token: str, aux: dict[str, str] | None) -> str:
    tok = error_token or (aux or {}).get("error_token", "") or "?"
    if tok in ("₂", "₁", "₃", "₄", "₅"):
        return f"subscript_digit:{tok}"
    if tok in ("̊", "̥", "̌", "̂", "̀", "̚", "̼", "̺", "̣"):
        return f"diacritic:{tok}"
    if tok in ("ː", "ˑ"):
        return f"length_mark:{tok}"
    if len(tok) == 1 and tok.isalpha():
        return f"letter:{tok}"
    return f"token:{tok}"


def classify_prose_or_expected_arrow(description: str) -> str:
    match = re.search(r"received '([^']*)'", description)
    tok = match.group(1) if match else "?"
    if tok in ("ˀ", "̥", "̊"):
        return f"tone_or_voice_mark_as_arrow:{tok}"
    if tok in (">", "→", "=>"):
        return "arrow_token_misplaced"
    return f"received_other:{tok}"


def classify_nested_brackets(description: str, aux: dict[str, str] | None) -> str:
    rule = (aux or {}).get("rule", _syntax_from_description(description))
    if re.search(r"\{\{", rule):
        return "true_nested_braces"
    if re.search(r"\{[^{}]*\{[^{}]*\}[^{}]*\}", rule):
        return "segment_template_parallel_set"
    if re.search(r"\([^)]+\)\{", rule) or re.search(r"\)\{", rule):
        return "optional_prefix_parallel_column"
    if re.search(r"\{[^{}]*\([^)]*\)[^{}]*\}", rule):
        return "paren_inside_set"
    return "other_nested"


def classify_expected_number(description: str) -> str:
    match = re.search(r"received ([^|]+) \|", description)
    tok = match.group(1).strip() if match else "?"
    if tok in ("j", "d", "ə", "ɡ", "C", "V"):
        return f"series_or_template_literal:{tok}"
    return f"received:{tok}"


def classify_runtime_other(description: str) -> str:
    if "Word Boundaries cannot be in the input or output" in description:
        return "word_boundary_in_io"
    if "incomplete matrix cannot be inserted" in description.lower():
        return "incomplete_matrix_insertion"
    if "same number of elements" in description:
        return "set_cardinality_mismatch"
    if "LonelySet" in description:
        return "lonely_set"
    return "other_runtime"


def classify_unknown_feature(error_token: str, aux: dict[str, str] | None) -> str:
    tok = error_token or (aux or {}).get("error_token", "") or "?"
    if "pitch" in tok.lower():
        return "pitch_feature_bundle"
    if tok in ("weak", "initial", "palatalized", "glide"):
        return f"bundle:{tok}"
    return f"feature:{tok}"


def classify(
    failure_class: str,
    description: str,
    *,
    error_token: str = "",
    aux: dict[str, str] | None = None,
) -> str:
    if failure_class == "syntax_other":
        return classify_syntax_other(description)
    if failure_class == "expected_underscore":
        return classify_expected_underscore(description, aux)
    if failure_class == "unknown_character":
        return classify_unknown_character(error_token, aux)
    if failure_class == "prose_or_expected_arrow":
        return classify_prose_or_expected_arrow(description)
    if failure_class == "nested_brackets":
        return classify_nested_brackets(description, aux)
    if failure_class == "expected_number":
        return classify_expected_number(description)
    if failure_class == "runtime_other":
        return classify_runtime_other(description)
    if failure_class == "unknown_feature":
        return classify_unknown_feature(error_token, aux)
    if failure_class == "diacritic_prereq":
        return "voice_prerequisite_diacritic"
    if failure_class == "unknown_grouping":
        return f"grouping:{error_token or '?'}"
    if failure_class == "stuff_after_word_bound":
        return "segments_after_word_end"
    if failure_class == "panic_other":
        return "thread_panicked"
    if failure_class == "format_error":
        return "no_compile_steps"
    if failure_class == "runtime_delete_only_segment":
        return "delete_only_segment"
    return failure_class or "other"


def main() -> int:
    rows = _load_inventory()
    blame_lookup = _load_lookup(
        "asca-field-isolation-error.csv",
        ("section_index", "rule_id", "alt_idx"),
    )
    underscore_lookup = _load_lookup(
        "underscore_errors.csv",
        ("section_index", "rule_id"),
    )
    nested_lookup = _load_lookup(
        "nested_brackets_errors.csv",
        ("section_index", "rule_id"),
    )
    character_lookup = _load_lookup(
        "character_errors.csv",
        ("section_index", "rule_id"),
    )
    feature_lookup = _load_lookup(
        "unknown_features.csv",
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
    near_miss = {sec for sec, count in section_fail_count.items() if 1 <= count <= 3}

    mono_class: set[str] = set()
    for sec in near_miss:
        classes = [
            rule["failure_class"]
            for rule in section_rules[sec]
            if rule["ok"] == "False"
        ]
        if classes and len(set(classes)) == 1:
            mono_class.add(sec)

    classified: list[Row] = []
    for sec in sorted(near_miss):
        for rule in section_rules[sec]:
            if rule["ok"] != "False":
                continue
            failure_class = rule.get("failure_class", "")
            key = (rule["section_index"], rule["rule_id"], rule.get("alt_idx", ""))
            blame_row = blame_lookup.get(key, {})
            aux = None
            if failure_class == "expected_underscore":
                aux = underscore_lookup.get((rule["section_index"], rule["rule_id"]))
            elif failure_class == "nested_brackets":
                aux = nested_lookup.get((rule["section_index"], rule["rule_id"]))
            elif failure_class == "unknown_character":
                aux = character_lookup.get((rule["section_index"], rule["rule_id"]))
            elif failure_class == "unknown_feature":
                aux = feature_lookup.get((rule["section_index"], rule["rule_id"]))
            classified.append(
                Row(
                    section_index=rule["section_index"],
                    section_name=rule["section_name"],
                    rule_id=rule["rule_id"],
                    failure_class=failure_class,
                    subcluster=classify(
                        failure_class,
                        rule.get("description", ""),
                        error_token=rule.get("error_token", ""),
                        aux=aux,
                    ),
                    blame=blame_row.get("blame", ""),
                    error_token=rule.get("error_token", ""),
                    description=rule.get("description", ""),
                    mono_class_section=sec in mono_class,
                )
            )

    def bucket_key(row: Row) -> tuple[str, str]:
        return (row.failure_class, row.subcluster)

    def sections_complete_if(target: tuple[str, str]) -> set[str]:
        completed: set[str] = set()
        for sec in near_miss:
            fails = [rule for rule in section_rules[sec] if rule["ok"] == "False"]
            if not fails:
                continue
            keys = {
                (
                    rule["failure_class"],
                    classify(
                        rule["failure_class"],
                        rule.get("description", ""),
                        error_token=rule.get("error_token", ""),
                        aux=(
                            underscore_lookup.get((rule["section_index"], rule["rule_id"]))
                            if rule["failure_class"] == "expected_underscore"
                            else nested_lookup.get((rule["section_index"], rule["rule_id"]))
                            if rule["failure_class"] == "nested_brackets"
                            else character_lookup.get((rule["section_index"], rule["rule_id"]))
                            if rule["failure_class"] == "unknown_character"
                            else feature_lookup.get((rule["section_index"], rule["rule_id"]))
                            if rule["failure_class"] == "unknown_feature"
                            else None
                        ),
                    ),
                )
                for rule in fails
            }
            if keys == {target}:
                completed.add(sec)
        return completed

    by_bucket: dict[tuple[str, str], list[Row]] = defaultdict(list)
    for row in classified:
        by_bucket[bucket_key(row)].append(row)

    bucket_stats: list[tuple[int, int, int, str, str]] = []
    for (failure_class, subcluster), items in by_bucket.items():
        complete = len(sections_complete_if((failure_class, subcluster)))
        secs = len({item.section_index for item in items})
        bucket_stats.append((complete, secs, len(items), failure_class, subcluster))
    bucket_stats.sort(reverse=True)

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
                    row.description,
                ]
            )

    print(f"wrote {OUT_CSV} ({len(classified)} rows)")
    print(f"near_miss_sections={len(near_miss)} near_miss_rules={len(classified)}")
    print("top_buckets:")
    for complete, secs, rules, failure_class, subcluster in bucket_stats[:25]:
        print(
            f"  {complete:3d} complete | {secs:3d} secs | {rules:3d} rules | "
            f"{failure_class} :: {subcluster}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
