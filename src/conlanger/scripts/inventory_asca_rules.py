"""Inventory ASCA compile/validate outcomes for provisional Index Diachronica YAML rules.

Evidence ticket: .scratch/cleaned-rule-corpus/issues/02-inventory-valid-vs-invalid-rules.md
Criteria: .scratch/cleaned-rule-corpus/research/asca-rule-validity.md
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from conlanger.tools.corpus_inventory import parse_unknown_token_error
from conlanger.tools.rules import SoundChangeRule

DEFAULT_YAML = ROOT / "legacy/data/index_diachronica_ai.yml"
DEFAULT_WORDS = ROOT / "data/generated/lexicon/asca/weirdness0.5.wsca"
DEFAULT_OUT = ROOT / ".scratch/cleaned-rule-corpus/inventory/asca-rule-inventory.csv"

ERROR_CLASS_PATTERNS = [
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
]


def classify_error(error: str) -> str:
    if not error:
        return ""
    for name, pat in ERROR_CLASS_PATTERNS:
        if pat.search(error):
            return name
    if error.lower().startswith("syntax error"):
        return "syntax_other"
    if error.lower().startswith("runtime error"):
        return "runtime_other"
    if "panicked" in error.lower():
        return "panic_other"
    return "other"


def format_syntax(rule: dict) -> str:
    return SoundChangeRule(rule, format="asca").value


def check_one(args: tuple) -> dict:
    section_index, section_name, rule_idx, syntax, words, asca_bin = args
    title = f"{section_index}_{rule_idx}"
    body = f"@ {title}\n\t{syntax}\n"
    with tempfile.TemporaryDirectory() as tmp:
        rsca = Path(tmp) / f"{title}.rsca"
        rsca.write_text(body, encoding="utf-8")
        cmd = [asca_bin, "run", words, "-r", str(rsca)]
        try:
            proc = subprocess.run(  # noqa: PLW1510
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
            )
            err = (proc.stderr or "").strip().replace("\n", " ")
            # strip ANSI
            err = re.sub(r"\x1b\[[0-9;]*m", "", err)
            error_token, suggested = parse_unknown_token_error(err)
            return {
                "section_index": section_index,
                "section_name": section_name,
                "rule_idx": rule_idx,
                "syntax": syntax,
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "error": err,
                "error_class": classify_error(err),
                "error_token": error_token,
                "suggested": suggested,
            }
        except subprocess.TimeoutExpired:
            return {
                "section_index": section_index,
                "section_name": section_name,
                "rule_idx": rule_idx,
                "syntax": syntax,
                "ok": False,
                "returncode": 124,
                "error": "timeout",
                "error_class": "timeout",
                "error_token": "",
                "suggested": "",
            }


def iter_jobs(doc: dict, words: str, asca_bin: str):
    for section in doc.get("sections") or []:
        rules = section.get("rules") or []
        if not rules:
            continue
        section_index = str(section.get("index", ""))
        section_name = str(section.get("section", ""))
        for rule_idx, rule in enumerate(rules):
            try:
                syntax = format_syntax(rule)
            except Exception as exc:  # noqa: BLE001 — record format failures
                err = f"format_error: {exc}"
                error_token, suggested = parse_unknown_token_error(err)
                yield {
                    "section_index": section_index,
                    "section_name": section_name,
                    "rule_idx": rule_idx,
                    "syntax": "",
                    "ok": False,
                    "returncode": -1,
                    "error": err,
                    "error_class": "format_error",
                    "error_token": error_token,
                    "suggested": suggested,
                    "_precomputed": True,
                }
                continue
            yield (
                section_index,
                section_name,
                rule_idx,
                syntax,
                words,
                asca_bin,
            )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaml", type=Path, default=DEFAULT_YAML)
    ap.add_argument("--words", type=Path, default=DEFAULT_WORDS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="optional cap for smoke tests")
    args = ap.parse_args()

    if shutil.which("asca") is None:
        print("ERROR: asca not found on PATH", file=sys.stderr)
        return 1
    asca_bin = shutil.which("asca")
    if not args.yaml.exists():
        print(f"ERROR: yaml not found at {args.yaml}", file=sys.stderr)
        return 1
    if not args.words.exists():
        print(f"ERROR: words not found at {args.words}", file=sys.stderr)
        return 1

    doc = yaml.safe_load(args.yaml.read_text(encoding="utf-8"))
    jobs = []
    precomputed = []
    for item in iter_jobs(doc, str(args.words), asca_bin):
        if isinstance(item, dict) and item.get("_precomputed"):
            item.pop("_precomputed")
            precomputed.append(item)
        else:
            jobs.append(item)
        if args.limit and len(jobs) + len(precomputed) >= args.limit:
            jobs = jobs[: max(0, args.limit - len(precomputed))]
            break

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "section_index",
        "section_name",
        "rule_idx",
        "syntax",
        "ok",
        "returncode",
        "error",
        "error_class",
        "error_token",
        "suggested",
    ]

    rows = list(precomputed)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check_one, job) for job in jobs]
        total = len(futures)
        for idx, fut in enumerate(as_completed(futures)):
            rows.append(fut.result())
            if idx % 500 == 0 or idx == total:
                print(f"progress {idx}/{total}", flush=True)

    rows.sort(key=lambda r: (r["section_index"], int(r["rule_idx"])))
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    ok_n = sum(1 for r in rows if r["ok"] in (True, "True", "true"))
    # after csv round-trip bools are bool here
    ok_n = sum(1 for r in rows if r["ok"] is True)
    fail_n = len(rows) - ok_n
    print(f"wrote {args.out} rows={len(rows)} ok={ok_n} fail={fail_n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
