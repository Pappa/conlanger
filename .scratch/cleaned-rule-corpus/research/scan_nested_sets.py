"""Scan Index Diachronica parsed YAML for nested-set shapes (spike 67).

Run: uv run python .scratch/cleaned-rule-corpus/research/scan_nested_sets.py
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
YAML_PATH = ROOT / "data/diachronica/index_diachronica_parsed.yml"
INVENTORY_PATH = (
    ROOT / ".scratch/cleaned-rule-corpus/inventory/asca-rule-inventory.csv"
)

# Index parenthetical segment notation (ticket 48): segment + {variants}
_PAREN_SEG_RE = __import__("re").compile(
    r"[A-Za-zÀ-ÿ0-9ːˤʷʼ₃₁₂₃₄₅₆₇₈₉₀]+(?:\[[^\]]+\])?\{[^}]+\}"
)


def max_brace_depth(text: str) -> int:
    depth = max_depth = 0
    for ch in text:
        if ch == "{":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == "}":
            depth -= 1
    return max_depth


def brace_balance(text: str) -> int:
    depth = 0
    for ch in text:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
    return depth


def _is_whole_field_set(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 2 or not stripped.startswith("{") or not stripped.endswith("}"):
        return False
    depth = 0
    for position, char in enumerate(stripped):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
            if depth == 0 and position != len(stripped) - 1:
                return False
    return depth == 0


def _split_top_level_sets(text: str) -> list[str]:
    """Split a field into top-level ``{…}`` chunks (condensed parallel columns)."""
    chunks: list[str] = []
    depth = 0
    start: int | None = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                chunks.append(text[start : i + 1])
                start = None
    return chunks


def _split_set_members(set_text: str) -> list[str]:
    inner = set_text.strip()[1:-1]
    members: list[str] = []
    current: list[str] = []
    depth = 0
    for char in inner:
        if char == "{":
            depth += 1
            current.append(char)
        elif char == "}":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            members.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    members.append("".join(current).strip())
    return members


def analyze_braces(text: str) -> dict[str, bool]:
    """Classify brace usage in one field value."""
    result = {
        "has_brace": "{" in text,
        "max_depth": max_brace_depth(text),
        "unbalanced": brace_balance(text) != 0,
        "true_nested_set": False,
        "parenthetical_in_set": False,
        "adjacent_parallel_sets_only": False,
        "mixed_nested_and_paren": False,
    }
    if not result["has_brace"]:
        return result

    sets = _split_top_level_sets(text)
    nested_members = 0
    paren_in_set = 0
    for set_chunk in sets:
        for member in _split_set_members(set_chunk):
            if "{" in member:
                if _PAREN_SEG_RE.search(member) and not member.strip().startswith("{"):
                    paren_in_set += 1
                elif member.strip().startswith("{"):
                    nested_members += 1
                elif "{" in member:
                    paren_in_set += 1

    if nested_members:
        result["true_nested_set"] = True
    if paren_in_set:
        result["parenthetical_in_set"] = True
    if nested_members and paren_in_set:
        result["mixed_nested_and_paren"] = True

  # Adjacent parallel sets without true nesting: multiple top-level sets, depth 1 each
    if (
        len(sets) > 1
        and not result["true_nested_set"]
        and all(max_brace_depth(s) == 1 for s in sets)
    ):
        result["adjacent_parallel_sets_only"] = True

    # Whole-field single set with nested member
    if _is_whole_field_set(text) and nested_members:
        result["true_nested_set"] = True

    return result


def is_optional_output_skipped(input_text: str, output_text: str) -> bool:
    if not (
        _is_whole_field_set(output_text) and not _is_whole_field_set(input_text)
    ):
        return False
    members = _split_set_members(output_text)
    return bool(members) and any("{" in m for m in members)


@dataclass
class RuleHit:
    source: str
    section: str
    rule_idx: int
    fields: dict[str, str] = field(default_factory=dict)
    field_analysis: dict[str, dict] = field(default_factory=dict)
    max_depth: int = 0
    tags: set[str] = field(default_factory=set)


def _field_kind(name: str) -> str:
    if name.startswith("stage["):
        return "io"
    if name in ("env", "exception"):
        return "env"
    return "other"


def classify_rule(rule: dict, section_name: str, rule_idx: int) -> RuleHit | None:
    source = rule.get("source", "")
    hit = RuleHit(source=source, section=section_name, rule_idx=rule_idx)

    stages = [s for s in rule.get("stages", []) if s and str(s).strip()]
    for i, stage in enumerate(stages):
        val = str(stage)
        if "{" not in val:
            continue
        hit.fields[f"stage[{i}]"] = val
        fa = analyze_braces(val)
        hit.field_analysis[f"stage[{i}]"] = fa
        hit.max_depth = max(hit.max_depth, fa["max_depth"])

    for key in ("env", "exception", "raw"):
        if key in rule and rule[key]:
            val = str(rule[key])
            if "{" not in val:
                continue
            hit.fields[key] = val
            fa = analyze_braces(val)
            hit.field_analysis[key] = fa
            hit.max_depth = max(hit.max_depth, fa["max_depth"])

    if len(stages) >= 2:
        non_empty = [s.strip() for s in stages if s and s.strip()]
        for idx in range(len(non_empty) - 1):
            if is_optional_output_skipped(non_empty[idx], non_empty[idx + 1]):
                hit.tags.add("optional_output_skipped")

    if hit.max_depth < 2 and "optional_output_skipped" not in hit.tags:
        if not any(fa.get("unbalanced") for fa in hit.field_analysis.values()):
            return None

    # Aggregate tags
    io_fa = [fa for n, fa in hit.field_analysis.items() if _field_kind(n) == "io"]
    env_fa = [fa for n, fa in hit.field_analysis.items() if _field_kind(n) == "env"]

    if any(fa.get("unbalanced") for fa in hit.field_analysis.values()):
        hit.tags.add("unbalanced")
    if any(fa.get("true_nested_set") for fa in io_fa):
        hit.tags.add("io_true_nested")
    if any(fa.get("true_nested_set") for fa in env_fa):
        hit.tags.add("env_true_nested")
    if any(fa.get("parenthetical_in_set") for fa in io_fa):
        hit.tags.add("io_parenthetical")
    if any(fa.get("parenthetical_in_set") for fa in env_fa):
        hit.tags.add("env_parenthetical")
    if any(fa.get("adjacent_parallel_sets_only") for fa in io_fa):
        hit.tags.add("io_adjacent_parallel_only")
    if any(fa.get("max_depth", 0) >= 2 for fa in hit.field_analysis.values()):
        hit.tags.add("depth_ge_2")

    return hit


def assign_bucket(hit: RuleHit) -> str:
    if "unbalanced" in hit.tags:
        return "E_unbalanced_malformed"
    if "io_true_nested" in hit.tags and "env_true_nested" in hit.tags:
        return "A_true_nested_io_and_env"
    if "io_true_nested" in hit.tags:
        return "A_true_nested_io"
    if "env_true_nested" in hit.tags:
        return "B_true_nested_env_exception"
    if "io_parenthetical" in hit.tags and not hit.tags & {
        "io_true_nested",
        "env_true_nested",
    }:
        return "C_parenthetical_in_io_set"
    if "env_parenthetical" in hit.tags and not hit.tags & {
        "io_true_nested",
        "env_true_nested",
    }:
        return "C_parenthetical_in_env_set"
    if "optional_output_skipped" in hit.tags:
        return "D_optional_output_overlap"
    if "depth_ge_2" in hit.tags:
        return "F_depth_ge2_unclassified"
    if "io_adjacent_parallel_only" in hit.tags:
        return "G_adjacent_parallel_sets_ok"
    return "Z_other"


def main() -> None:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    hits: list[RuleHit] = []
    total_rules = 0
    for section in data.get("sections", []):
        for ri, rule in enumerate(section.get("rules", []) or []):
            total_rules += 1
            h = classify_rule(rule, section.get("section", ""), ri)
            if h:
                hits.append(h)

    inv_nested_sources: set[str] = set()
    with INVENTORY_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("failure_class") == "nested_brackets":
                inv_nested_sources.add(row["source"])

    buckets: dict[str, list[RuleHit]] = defaultdict(list)
    for h in hits:
        buckets[assign_bucket(h)].append(h)

    summary = {
        "total_rules_scanned": total_rules,
        "rules_with_nested_signal": len(hits),
        "inventory_nested_brackets_unique_sources": len(inv_nested_sources),
        "bucket_counts": {k: len(v) for k, v in sorted(buckets.items())},
        "bucket_inventory_overlap": {},
        "bucket_examples": {},
    }

    for bucket, items in sorted(buckets.items()):
        overlap = sum(1 for h in items if h.source in inv_nested_sources)
        summary["bucket_inventory_overlap"][bucket] = overlap
        examples = []
        for h in items[:5]:
            examples.append(
                {
                    "source": h.source,
                    "section": h.section,
                    "rule_idx": h.rule_idx,
                    "tags": sorted(h.tags),
                    "fields": h.fields,
                    "in_inventory_nested_brackets": h.source in inv_nested_sources,
                }
            )
        summary["bucket_examples"][bucket] = examples

    out_path = Path(__file__).with_name("nested-sets-scan.json")
    out_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary["bucket_counts"], indent=2))
    print("inventory overlap per bucket:", summary["bucket_inventory_overlap"])
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
