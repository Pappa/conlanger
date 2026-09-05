"""Scan syntax_other failures in ≤3-fail sections (spike 64).

Run: uv run python .scratch/cleaned-rule-index/research/scan_syntax_other_near_miss.py
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INVENTORY_PATH = ROOT / ".scratch/cleaned-rule-index/inventory/asca-rule-inventory.csv"
OUT_CSV = Path(__file__).with_name("syntax-other-near-miss-sections.csv")
OUT_MD = Path(__file__).with_name("syntax-other-near-miss-sections.md")


@dataclass
class Row:
    section_index: str
    section_name: str
    rule_id: str
    subcluster: str
    description: str
    mono_class_section: bool


def _syntax_from_description(description: str) -> str:
    parts = description.split("|")
    return parts[1].strip() if len(parts) > 1 else ""


def classify(description: str) -> str:
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


def main() -> int:
    rows = list(csv.DictReader(INVENTORY_PATH.open(encoding="utf-8")))
    section_rules: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("failure_class") == "section_skipped":
            continue
        section_rules[row["section_index"]].append(row)

    section_fail_count = {
        sec: sum(1 for r in rs if r["ok"] == "False")
        for sec, rs in section_rules.items()
    }
    near_miss = {s for s, c in section_fail_count.items() if 1 <= c <= 3}

    mono_class: set[str] = set()
    for sec in near_miss:
        classes = [r["failure_class"] for r in section_rules[sec] if r["ok"] == "False"]
        if classes and all(c == "syntax_other" for c in classes):
            mono_class.add(sec)

    classified: list[Row] = []
    for sec in sorted(near_miss):
        for r in section_rules[sec]:
            if r["ok"] == "False" and r["failure_class"] == "syntax_other":
                classified.append(
                    Row(
                        section_index=r["section_index"],
                        section_name=r["section_name"],
                        rule_id=r["rule_id"],
                        subcluster=classify(r.get("description", "")),
                        description=r.get("description", ""),
                        mono_class_section=sec in mono_class,
                    )
                )

    def sections_complete_if(subcluster: str) -> set[str]:
        completed: set[str] = set()
        for sec in near_miss:
            fails = [r for r in section_rules[sec] if r["ok"] == "False"]
            sub = [
                r
                for r in fails
                if r["failure_class"] == "syntax_other"
                and classify(r.get("description", "")) == subcluster
            ]
            if sub and len(sub) == len(fails):
                completed.add(sec)
        return completed

    subcluster_stats: list[tuple[int, int, int, str]] = []
    by_sub: dict[str, list[Row]] = defaultdict(list)
    for row in classified:
        by_sub[row.subcluster].append(row)
    for sub, items in by_sub.items():
        secs = {r.section_index for r in items}
        subcluster_stats.append(
            (len(sections_complete_if(sub)), len(secs), len(items), sub)
        )
    subcluster_stats.sort(reverse=True)

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "section_index",
                "section_name",
                "rule_id",
                "subcluster",
                "mono_class_section",
                "description",
            ]
        )
        for row in classified:
            w.writerow(
                [
                    row.section_index,
                    row.section_name,
                    row.rule_id,
                    row.subcluster,
                    row.mono_class_section,
                    row.description,
                ]
            )

    lines = [
        "# syntax_other in ≤3-fail sections (spike 64)",
        "",
        "Research for spike [64](../issues/64-spike-syntax-other-near-miss-sections.md).",
        "",
        "Primary sources:",
        "",
        (
            "- Inventory: [`asca-rule-inventory.csv`](../inventory/asca-rule-inventory.csv) "
            "(post-ticket-63 baseline: **8094 / 9639** ok, **299 / 713** sections all-OK)"
        ),
        (
            "- Scan script: [`scan_syntax_other_near_miss.py`](./scan_syntax_other_near_miss.py) "
            "→ [`syntax-other-near-miss-sections.csv`](./syntax-other-near-miss-sections.csv)"
        ),
        "",
        "---",
        "",
        "## 1. Executive summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| Near-miss sections (1–3 fails) | {len(near_miss)} |",
        f"| `syntax_other` rules in near-miss band | {len(classified)} |",
        f"| Sections with ≥1 such rule | {len({r.section_index for r in classified})} |",
        f"| Mono-class near-miss (all fails = `syntax_other`) | {len(mono_class)} |",
        "",
        (
            "Pre-pass sizing (2026-08-12) cited **179** rules / **137** sections / **71** mono-class; "
            "post-62/63 inventory drift is expected."
        ),
        "",
        "## 2. Ranked subclusters (sections-completed if cleared)",
        "",
        "| sections complete | sections | rules | subcluster | recommendation |",
        "|------------------:|---------:|------:|------------|----------------|",
    ]
    recs = {
        "null_in_parallel_output_set": "correction-pass → [81](../issues/81-correction-pass-parallel-output-null.md)",
        "missing_slash_output_env": "correction-pass → [82](../issues/82-correction-pass-output-env-slash-boundary.md)",
        "insertion_wildcard_input": "correction-pass → [83](../issues/83-correction-pass-australasian-wildcard-insertion.md)",
        "wildcard_in_correspondence_set": "correction-pass → [83](../issues/83-correction-pass-australasian-wildcard-insertion.md)",
        "underscore_env_shorthand": "defer — correction-pass batched with env notation",
        "expected_range_dots": "correction-pass (Yup'ik `V(..)V` range)",
        "word_edge_percent_hash": "correction-pass (compile `%#` / `#%`)",
        "paren_in_segment_residual": "correction-pass (ticket 48 follow-on)",
        "superscript_segment_modifier": "correction-pass (ticket 50 follow-on)",
        "floating_glottal_diacritic": "manual_mappings / skip (Chumash)",
        "click_or_exotic_ipa:ǃ": "defer — manual_mappings batch or skip",
        "click_or_exotic_ipa:ǀ": "defer — manual_mappings batch or skip",
        "click_or_exotic_ipa:ⁿ": "defer — manual_mappings batch or skip",
        "click_or_exotic_ipa:ǂ": "defer — manual_mappings batch or skip",
        "ejective_modifier_residual": "defer — overlaps [20](../issues/20-correction-pass-ejective-marks.md) residuals",
        "segments_before_word_beg_other": "defer — mixed shapes, low leverage",
        "negation_in_output": "manual_mappings",
        "tone_negation": "manual_mappings (ticket 62 residual)",
    }
    for complete, secs, rules, sub in subcluster_stats:
        rec = recs.get(sub, "triage / low leverage")
        lines.append(f"| {complete} | {secs} | {rules} | `{sub}` | {rec} |")

    lines.extend(
        [
            "",
            "## 3. Top-three correction-pass tickets (filed)",
            "",
            (
                "1. **[81 — parallel output ∅ sets](../issues/81-correction-pass-parallel-output-null.md)** "
                f"— **{subcluster_stats[0][2] if subcluster_stats else 0}** rules, "
                f"**{subcluster_stats[0][0] if subcluster_stats else 0}** mono-class sections complete if cleared. "
                "Index writes `{m,∅}` / `{r,∅}` parallel outputs; ASCA wants deletion via `∅` segment or split rules."
            ),
            "",
            (
                "2. **[82 — output/env slash boundary](../issues/82-correction-pass-output-env-slash-boundary.md)** "
                "— residual `Expected end of line… forget a '/'` after tickets 48/51; mostly `(` concat and env glue."
            ),
            "",
            (
                "3. **[83 — Australasian `*X` wildcards](../issues/83-correction-pass-australasian-wildcard-insertion.md)** "
                "— `*R`/`*L`/`*j` insertion inputs and `{z,*Z,*D}` correspondence sets; overlaps series expansion policy."
            ),
            "",
            "## 4. Defer / skip",
            "",
            (
                "- **Khoisan clicks** (`ǃ`, `ǀ`, `ǂ`, `ⁿ` prefix): **16** near-miss rules across **~10** sections — "
                "no class-first compile path; batch `manual_mappings` or `status: skipped`."
            ),
            "- **Chumash floating glottal** (`ˀj`, `ˀN`, …): **5** rules, **3** sections — section-local rewrites only.",
            (
                "- **Iroquoian / Yup'ik `%#` env** and **range `..`**: medium leverage (**9+9** rules) but mixed with "
                "other failure classes in most sections — file after passes 81–83 land."
            ),
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_CSV} ({len(classified)} rows)")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
