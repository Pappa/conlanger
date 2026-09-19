"""Spike 85: in-memory nested-set flatten → compile validation metrics.

Throwaway. Does not write ``data/diachronica/index_diachronica_parsed.yml``.
Does not append the committed changelog.

    uv run python .scratch/rule-index/research/nested_set_flatten_prototype.py

Phase A validates every rule whose working fields change (plus every current
``nested_brackets`` inventory source) via ``validate_index_rule``, then merges
unchanged rows from the committed inventory. That is a full inventory
comparison: unflattened rules cannot flip ``ok``.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from flatten_nested_sets import (
    MODE_UNION,
    MODE_UNION_PAREN,
    apply_flatten_to_parts,
    apply_flatten_to_rule,
    flatten_nested_sets,
)
from scan_nested_sets import (
    assign_bucket,
    classify_rule,
    count_working_depth_ge2,
)

from conlanger.tools.compile.asca.group_mappings import asca_group_mappings_dict
from conlanger.tools.index_inventory import (
    validate_index_rule,
)
from conlanger.tools.ingest.section_policy import resolve_catch_all_else_rules

YAML_PATH = ROOT / "data/diachronica/index_diachronica_parsed.yml"
INVENTORY_PATH = ROOT / ".scratch/rule-index/inventory/rule-inventory.csv"
PROBE_WORDS = ROOT / "tests/fixtures/asca_probe_words.wsca"
OUT_CSV = Path(__file__).with_name("nested-set-flatten-prototype.csv")
OUT_JSON = Path(__file__).with_name("nested-set-flatten-prototype-metrics.json")

# #67 inventory buckets (nested-sets-inventory.md §4). A source may appear in
# more than one prose table; first match in this ordered map wins for CSV.
_BUCKET_SOURCES: list[tuple[str, tuple[str, ...]]] = [
    (
        "A",
        (
            "index_diachronica_original.html:998",
            "index_diachronica_original.html:1149",
            "index_diachronica_original.html:1398",
            "index_diachronica_original.html:2173",
            "index_diachronica_original.html:4654",
            "index_diachronica_original.html:5048",
            "index_diachronica_original.html:3124",
            "index_diachronica_original.html:3737",
            "index_diachronica_original.html:8439",
            "index_diachronica_original.html:12290",
        ),
    ),
    (
        "B",
        (
            "index_diachronica_original.html:1903",
            "index_diachronica_original.html:5509",
            "index_diachronica_original.html:5510",
            "index_diachronica_original.html:11518",
            "index_diachronica_original.html:11552",
            "index_diachronica_original.html:11579",
            "index_diachronica_original.html:11601",
            "index_diachronica_original.html:11624",
            "index_diachronica_original.html:1954",
            "index_diachronica_original.html:1762",
            "index_diachronica_original.html:6192",
            "index_diachronica_original.html:6225",
            "index_diachronica_original.html:6226",
            "index_diachronica_original.html:6194",
        ),
    ),
    (
        "C",
        (
            "index_diachronica_original.html:1903",
            "index_diachronica_original.html:5509",
            "index_diachronica_original.html:5510",
            "index_diachronica_original.html:6193",
        ),
    ),
    (
        "D",
        (
            "index_diachronica_original.html:2398",
            "index_diachronica_original.html:2409",
            "index_diachronica_original.html:5454",
            "index_diachronica_original.html:6165",
            "index_diachronica_original.html:3124",
            "index_diachronica_original.html:3737",
            "index_diachronica_original.html:5900",
            "index_diachronica_original.html:14327",
            "index_diachronica_original.html:2415",
        ),
    ),
    (
        "E",
        (
            "index_diachronica_original.html:2173",
            "index_diachronica_original.html:4265",
            "index_diachronica_original.html:4654",
            "index_diachronica_original.html:5839",
            "index_diachronica_original.html:6380",
            "index_diachronica_original.html:5803",
            "index_diachronica_original.html:5570",
            "index_diachronica_original.html:2415",
            "index_diachronica_original.html:9306",
            "index_diachronica_original.html:11857",
            "index_diachronica_original.html:7926",
            "index_diachronica_original.html:10824",
            "index_diachronica_original.html:14482",
            "index_diachronica_original.html:9842",
            "index_diachronica_original.html:10564",
            "index_diachronica_original.html:12394",
            "index_diachronica_original.html:12512",
            "index_diachronica_original.html:14142",
            "index_diachronica_original.html:11722",
        ),
    ),
]


def _bucket_for(source: str) -> str:
    for bucket, sources in _BUCKET_SOURCES:
        if source in sources:
            return bucket
    return "?"


def _ok_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_index() -> dict[str, Any]:
    return yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))


def flatten_index(
    doc: dict[str, Any], *, mode: str
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Deep-copy ``doc`` and flatten working fields. Returns changed ``source`` map."""
    out = deepcopy(doc)
    changed: dict[str, list[str]] = {}
    for section in out.get("sections") or []:
        new_rules = []
        for rule in section.get("rules") or []:
            flattened, fields = apply_flatten_to_rule(rule, mode=mode)
            new_rules.append(flattened)
            if fields:
                changed[str(rule.get("source", ""))] = fields
        section["rules"] = new_rules
    return out, changed


def _inventory_index(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            alt = row.get("alt_idx") or ""
            rows[(row["source"], alt)] = row
    return rows


def _validate_job(
    payload: tuple[dict[str, Any], dict[str, Any], Path, dict[str, str]],
) -> list[dict[str, Any]]:
    section, rule, probe, group_mappings = payload
    rows = validate_index_rule(
        section,
        rule,
        str(rule.get("rule_id", "")),
        probe_words=probe,
        group_mappings=group_mappings,
    )
    return [row.__dict__ if hasattr(row, "__dict__") else dict(row) for row in rows]


def _row_to_dict(row: Any) -> dict[str, Any]:
    data = dict(row.as_csv_dict())
    data["ok"] = _ok_bool(data.get("ok"))
    data["alt_idx"] = (
        "" if data.get("alt_idx") in (None, "None") else str(data.get("alt_idx") or "")
    )
    return data


def validate_changed_rules(
    doc: dict[str, Any],
    *,
    sources: set[str],
    workers: int,
) -> dict[tuple[str, str], dict[str, Any]]:
    probe = PROBE_WORDS
    group_mappings = asca_group_mappings_dict()
    jobs: list[tuple[dict[str, Any], dict[str, Any], Path, dict[str, str]]] = []
    for section in doc.get("sections") or []:
        for rule in section.get("rules") or []:
            if str(rule.get("source", "")) in sources:
                jobs.append((section, rule, probe, group_mappings))
    results: dict[tuple[str, str], dict[str, Any]] = {}
    if not jobs:
        return results
    print(f"validating {len(jobs)} rules ({workers} threads)…", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(
                validate_index_rule,
                section,
                rule,
                str(rule.get("rule_id", "")),
                probe_words=probe,
                group_mappings=group_mappings,
            )
            for section, rule, probe, group_mappings in jobs
        ]
        done = 0
        for future in as_completed(futures):
            rows = future.result()
            for row in rows:
                data = _row_to_dict(row)
                alt = (
                    ""
                    if data.get("alt_idx") in (None, "None")
                    else str(data["alt_idx"])
                )
                results[(data["source"], alt)] = data
            done += 1
            if done % 25 == 0 or done == len(futures):
                print(f"  {done}/{len(futures)}", flush=True)
    return results


def merge_inventory(
    baseline: dict[tuple[str, str], dict[str, str]],
    validated: dict[tuple[str, str], dict[str, Any]],
    *,
    replaced_sources: set[str],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for key, row in baseline.items():
        source, alt = key
        if source in replaced_sources and key in validated:
            merged.append(validated[key])
            seen.add(key)
        elif source in replaced_sources:
            # Source was revalidated but this alt_idx vanished — drop it.
            continue
        else:
            merged.append(
                {
                    "source": source,
                    "alt_idx": alt,
                    "ok": _ok_bool(row.get("ok")),
                    "failure_class": row.get("failure_class") or "",
                    "rule_id": row.get("rule_id", ""),
                    "section_index": row.get("section_index", ""),
                    "description": row.get("description", ""),
                }
            )
            seen.add(key)
    for key, data in validated.items():
        if key not in seen:
            merged.append(data)
    return merged


def summarize(
    merged: list[dict[str, Any]],
    baseline: dict[tuple[str, str], dict[str, str]],
) -> dict[str, Any]:
    ok_true = sum(1 for row in merged if _ok_bool(row.get("ok")))
    nested = sum(1 for row in merged if row.get("failure_class") == "nested_brackets")
    flips = 0
    regressions = 0
    transitions: Counter[str] = Counter()
    for row in merged:
        key = (row["source"], str(row.get("alt_idx") or ""))
        prev = baseline.get(key)
        if prev is None:
            continue
        prev_ok = _ok_bool(prev.get("ok"))
        cur_ok = _ok_bool(row.get("ok"))
        prev_fc = prev.get("failure_class") or ""
        cur_fc = row.get("failure_class") or ("ok" if cur_ok else "")
        if prev_ok != cur_ok:
            flips += 1
            if prev_ok and not cur_ok:
                regressions += 1
        if prev_fc != cur_fc and (
            prev_fc == "nested_brackets"
            or cur_fc == "nested_brackets"
            or prev_ok != cur_ok
        ):
            label_prev = "ok" if prev_ok and not prev_fc else (prev_fc or "ok")
            label_cur = "ok" if cur_ok else (cur_fc or "fail")
            transitions[f"{label_prev}→{label_cur}"] += 1
    return {
        "ok_true": ok_true,
        "nested_brackets": nested,
        "ok_flips": flips,
        "regressions": regressions,
        "transitions": dict(transitions),
        "inventory_rows": len(merged),
    }


def write_per_rule_csv(
    path: Path,
    *,
    baseline: dict[tuple[str, str], dict[str, str]],
    merged_by_mode: dict[str, list[dict[str, Any]]],
    changed_by_mode: dict[str, dict[str, list[str]]],
) -> None:
    sources: set[str] = set()
    for changed in changed_by_mode.values():
        sources.update(changed)
    for source, _alt in baseline:
        if baseline[(source, _alt)].get("failure_class") == "nested_brackets":
            sources.add(source)
    fieldnames = [
        "source",
        "alt_idx",
        "bucket",
        "fields_changed_union",
        "fields_changed_union_paren",
        "ok_before",
        "ok_union",
        "ok_union_paren",
        "failure_class_before",
        "failure_class_union",
        "failure_class_union_paren",
    ]
    index_union = {
        (r["source"], str(r.get("alt_idx") or "")): r
        for r in merged_by_mode[MODE_UNION]
    }
    index_paren = {
        (r["source"], str(r.get("alt_idx") or "")): r
        for r in merged_by_mode[MODE_UNION_PAREN]
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for (source, alt), prev in sorted(baseline.items()):
            if source not in sources:
                continue
            u = index_union.get((source, alt), {})
            p = index_paren.get((source, alt), {})
            writer.writerow(
                {
                    "source": source,
                    "alt_idx": alt,
                    "bucket": _bucket_for(source),
                    "fields_changed_union": "|".join(
                        changed_by_mode[MODE_UNION].get(source, [])
                    ),
                    "fields_changed_union_paren": "|".join(
                        changed_by_mode[MODE_UNION_PAREN].get(source, [])
                    ),
                    "ok_before": _ok_bool(prev.get("ok")),
                    "ok_union": _ok_bool(u.get("ok", prev.get("ok"))),
                    "ok_union_paren": _ok_bool(p.get("ok", prev.get("ok"))),
                    "failure_class_before": prev.get("failure_class") or "",
                    "failure_class_union": u.get(
                        "failure_class", prev.get("failure_class") or ""
                    ),
                    "failure_class_union_paren": p.get(
                        "failure_class", prev.get("failure_class") or ""
                    ),
                }
            )


def run_else_fixtures() -> dict[str, Any]:
    """P3 vs P4 commutativity on the Old Irish :5509/:5510 pair."""
    nested_env = "_{s,({m,j,w})V}"
    results: dict[str, Any] = {}
    for mode in (MODE_UNION, MODE_UNION_PAREN):
        env_p3 = flatten_nested_sets(nested_env, mode=mode)
        pair_p3 = [
            {
                "stages": ["m̩ n̩", "am an"],
                "env": env_p3,
                "raw": "m̩ n̩ → am an / _{s,({m,j,w})V}",
            },
            {"stages": ["m̩ n̩", "em en"], "env": "else", "raw": "m̩ n̩ → em en / else"},
        ]
        resolved_p3 = resolve_catch_all_else_rules(pair_p3)

        pair_p4 = [
            {
                "stages": ["m̩ n̩", "am an"],
                "env": nested_env,
                "raw": "m̩ n̩ → am an / _{s,({m,j,w})V}",
            },
            {"stages": ["m̩ n̩", "em en"], "env": "else", "raw": "m̩ n̩ → em en / else"},
        ]
        resolved_p4 = resolve_catch_all_else_rules(pair_p4)
        resolved_p4[0], _ = apply_flatten_to_rule(resolved_p4[0], mode=mode)
        resolved_p4[1], _ = apply_flatten_to_rule(resolved_p4[1], mode=mode)

        results[mode] = {
            "p3_prev_env": resolved_p3[0].get("env"),
            "p3_else_exception": resolved_p3[1].get("exception"),
            "p4_prev_env": resolved_p4[0].get("env"),
            "p4_else_exception": resolved_p4[1].get("exception"),
            "exception_equal": resolved_p3[1].get("exception")
            == resolved_p4[1].get("exception"),
        }

    # Deferred else: :1762 has env AND nested exception, so :1763 stays env: else.
    deferred = resolve_catch_all_else_rules(
        [
            {
                "stages": ["aː", "aa"],
                "env": "W_",
                "exception": "when _{C{C,ː},#}",
                "raw": "aː → aa / W_ ! when _{C{C,ː},#}",
            },
            {"stages": ["aː", "a"], "env": "else", "raw": "aː → a / else"},
        ]
    )
    results["deferred_1762_1763"] = {
        "else_keeps_env": deferred[1].get("env"),
        "else_has_exception": "exception" in deferred[1],
        "prev_exception_still_nested": deferred[0].get("exception"),
    }
    return results


def run_series_slot_probe() -> dict[str, Any]:
    """P1 vs P2: series_expansions can splice collectives inside braces."""
    from conlanger.utils.series import apply_series_expansions

    expansions = {"hₓ": ("h₁", "h₂", "h₃")}
    before_series = {"stages": ["{ʔ,hₓ}"], "raw": "{ʔ,hₓ} → ∅"}
    after_series = apply_series_expansions(dict(before_series), expansions)
    p1 = apply_flatten_to_parts(dict(before_series), mode=MODE_UNION) or {}
    p1_then_series = apply_series_expansions(p1, expansions)
    p2 = apply_flatten_to_parts(dict(after_series), mode=MODE_UNION) or {}
    nested_after_series = {"stages": ["{ʔ,{h₁,h₂,h₃}}"]}
    p2_nested = apply_flatten_to_parts(dict(nested_after_series), mode=MODE_UNION) or {}
    return {
        "html_shape": "{ʔ,hₓ}",
        "after_series_expansions": after_series.get("stages"),
        "p1_flatten_then_series": p1_then_series.get("stages"),
        "p2_series_then_flatten": p2.get("stages"),
        "hypothetical_nested_after_series": p2_nested.get("stages"),
        "p1_equals_p2_on_current_998_shape": p1_then_series.get("stages")
        == p2.get("stages"),
    }


def run_phase_a(workers: int) -> dict[str, Any]:
    print("loading YAML…", flush=True)
    doc = load_index()
    baseline = _inventory_index(INVENTORY_PATH)
    nested_sources = {
        source
        for (source, _alt), row in baseline.items()
        if row.get("failure_class") == "nested_brackets"
    }
    before_ok = sum(1 for row in baseline.values() if _ok_bool(row.get("ok")))
    before_nested = sum(
        1 for row in baseline.values() if row.get("failure_class") == "nested_brackets"
    )
    before_depth = count_working_depth_ge2(doc)

    metrics: dict[str, Any] = {
        "before": {
            "ok_true": before_ok,
            "nested_brackets": before_nested,
            "working_depth_ge2": before_depth,
            "inventory_rows": len(baseline),
        }
    }
    merged_by_mode: dict[str, list[dict[str, Any]]] = {}
    changed_by_mode: dict[str, dict[str, list[str]]] = {}
    depth_by_mode: dict[str, int] = {}

    for mode in (MODE_UNION, MODE_UNION_PAREN):
        print(f"\n=== Phase A mode={mode} ===", flush=True)
        flattened, changed = flatten_index(doc, mode=mode)
        changed_by_mode[mode] = changed
        depth_by_mode[mode] = count_working_depth_ge2(flattened)
        sources = set(changed) | nested_sources
        print(
            f"rules with ≥1 field flattened: {len(changed)}; "
            f"validate sources: {len(sources)}",
            flush=True,
        )
        validated = validate_changed_rules(flattened, sources=sources, workers=workers)
        merged = merge_inventory(baseline, validated, replaced_sources=sources)
        merged_by_mode[mode] = merged
        stats = summarize(merged, baseline)
        stats["rules_flattened"] = len(changed)
        stats["working_depth_ge2"] = depth_by_mode[mode]
        metrics[mode] = stats
        print(json.dumps(stats, indent=2, ensure_ascii=False), flush=True)

    write_per_rule_csv(
        OUT_CSV,
        baseline=baseline,
        merged_by_mode=merged_by_mode,
        changed_by_mode=changed_by_mode,
    )
    print(f"wrote {OUT_CSV}", flush=True)

    # Scan-style bucket counts after union flatten (working fields via classify).
    after_hits = []
    flattened_union, _ = flatten_index(doc, mode=MODE_UNION)
    for section in flattened_union.get("sections") or []:
        for idx, rule in enumerate(section.get("rules") or []):
            hit = classify_rule(rule, section.get("section", ""), idx)
            if hit:
                after_hits.append(hit)
    bucket_counts = Counter(assign_bucket(h) for h in after_hits)
    metrics["scan_buckets_after_union"] = dict(bucket_counts)
    metrics["else_fixtures"] = run_else_fixtures()
    metrics["series_slot_probe"] = run_series_slot_probe()
    OUT_JSON.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"wrote {OUT_JSON}", flush=True)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument(
        "--self-check-only",
        action="store_true",
        help="run flatten self-check + else/series fixtures; skip asca inventory",
    )
    args = parser.parse_args()
    if args.self_check_only:
        print(json.dumps(run_else_fixtures(), indent=2, ensure_ascii=False))
        print(json.dumps(run_series_slot_probe(), indent=2, ensure_ascii=False))
        return
    run_phase_a(workers=args.workers)


if __name__ == "__main__":
    main()
