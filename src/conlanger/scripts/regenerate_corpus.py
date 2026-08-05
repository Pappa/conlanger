"""Regenerate cleaned corpus YAML and ASCA validation inventory from Index HTML.

Ticket 12: one invocation emits cleaned YAML, validation CSV, and summary markdown.
Uses ticket-11 extract-only ingest (``IndexDiachronicaParser``) and ``validate_asca``.
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from conlanger.tools.corpus_inventory import (
    iter_validation_rows,
    summarize_inventory,
    write_validation_csv,
)
from conlanger.tools.corpus_io import write_cleaned_corpus
from conlanger.tools.parsers import (
    IndexDiachronicaParser,
    write_rule_comment_phrase_summary,
)

DEFAULT_HTML = ROOT / "data" / "diachronica" / "index_diachronica_original.html"
DEFAULT_YAML = ROOT / "data" / "diachronica" / "index_diachronica_parsed.yml"
DEFAULT_INVENTORY_DIR = ROOT / ".scratch" / "cleaned-rule-corpus" / "inventory"
DEFAULT_COMMENT_SUMMARY = (
    ROOT / ".scratch" / "cleaned-rule-corpus" / "rule-comment-phrases.md"
)
DEFAULT_PROBE = ROOT / "tests" / "fixtures" / "asca_probe_words.wsca"


def _asca_version() -> str:
    asca = shutil.which("asca")
    if asca is None:
        return "not found on PATH"
    try:
        proc = subprocess.run(  # noqa: PLW1510
            [asca, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.stdout.strip():
            return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "0.10.x"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", type=Path, default=DEFAULT_HTML)
    ap.add_argument("--yaml-out", type=Path, default=DEFAULT_YAML)
    ap.add_argument(
        "--inventory-dir",
        type=Path,
        default=DEFAULT_INVENTORY_DIR,
        help="writes asca-rule-inventory.csv and asca-rule-inventory-summary.md",
    )
    ap.add_argument("--probe-words", type=Path, default=DEFAULT_PROBE)
    ap.add_argument(
        "--skip-validation",
        action="store_true",
        help="ingest only; skip validate_asca inventory (when asca binary absent)",
    )
    ap.add_argument("--limit", type=int, default=0, help="optional cap for smoke tests")
    args = ap.parse_args()

    if not args.html.is_file():
        print(f"ERROR: HTML not found at {args.html}", file=sys.stderr)
        return 1

    parser = IndexDiachronicaParser()
    doc = parser.parse(args.html)
    write_cleaned_corpus(doc, args.yaml_out)
    n_with_comment = write_rule_comment_phrase_summary(doc, DEFAULT_COMMENT_SUMMARY)

    n_sections = len(doc["sections"])
    n_rules = sum(len(s.get("rules") or []) for s in doc["sections"])
    n_skipped = sum(
        1
        for section in doc["sections"]
        for rule in section.get("rules") or []
        if rule.get("skipped")
    )
    print(
        f"wrote {args.yaml_out} sections={n_sections} rules={n_rules} "
        f"parse_skipped={n_skipped} rules_with_comment={n_with_comment}"
    )
    print(f"wrote {DEFAULT_COMMENT_SUMMARY}")

    if args.skip_validation:
        print("skipped validation inventory (--skip-validation)")
        return 0

    if not args.probe_words.is_file():
        print(f"ERROR: probe wordlist not found at {args.probe_words}", file=sys.stderr)
        return 1

    if shutil.which("asca") is None:
        print(
            "ERROR: asca binary not found on PATH "
            "(install asca 0.10.x and ensure it is on PATH, or use --skip-validation)",
            file=sys.stderr,
        )
        return 1

    rows = list(iter_validation_rows(doc, probe_words=args.probe_words))
    if args.limit:
        rows = rows[: args.limit]

    csv_path = args.inventory_dir / "asca-rule-inventory.csv"
    summary_path = args.inventory_dir / "asca-rule-inventory-summary.md"
    write_validation_csv(rows, csv_path)

    summary = summarize_inventory(
        rows,
        source_yaml=str(args.yaml_out.relative_to(ROOT)),
        probe_words=str(args.probe_words.relative_to(ROOT)),
        asca_version=_asca_version(),
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary, encoding="utf-8")

    ok_n = sum(1 for row in rows if row.ok)
    fail_n = len(rows) - ok_n
    print(
        f"wrote {csv_path} rows={len(rows)} ok={ok_n} fail={fail_n}\n"
        f"wrote {summary_path}"
    )
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unexpected error")
