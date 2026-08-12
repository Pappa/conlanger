"""Regenerate cleaned corpus YAML and ASCA validation inventory from Index HTML.

Ticket 12: one invocation emits cleaned YAML, validation CSV, and summary markdown.
Uses ticket-11 extract-only ingest (``IndexDiachronicaParser``) and ``validate_asca``.
Optional ``--update-series-mappings`` refreshes ``data/asca/series_mappings.csv`` before parse.
"""

import argparse
import logging
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from conlanger.tools.compile.asca.group_mappings import asca_group_mappings_dict
from conlanger.tools.corpus_inventory import (
    INVENTORY_CHANGELOG_CSV_NAME,
    INVENTORY_CSV_NAME,
    INVENTORY_ERROR_CSV_NAME,
    INVENTORY_SUCCESS_CSV_NAME,
    append_ok_flip_changelog,
    iter_validation_rows,
    load_inventory_csv,
    ok_flip_changelog_rows,
    summarize_inventory,
    validation_rows_to_dataframe,
    write_filtered_inventory_csvs,
    write_validation_csv,
)
from conlanger.tools.corpus_io import write_cleaned_corpus
from conlanger.tools.ingest import (
    IndexDiachronicaParser,
    write_rule_comment_phrase_summary,
)
from conlanger.tools.series_extract import (
    DEFAULT_SERIES_MAPPINGS_REPORT,
    update_series_mappings_from_html,
)
from conlanger.utils.file_io import (
    DEFAULT_SERIES_MAPPINGS_CSV,
    MANUAL_MAPPINGS_MATCHED_CSV_NAME,
    load_default_ingest_tables,
    write_manual_mappings_matched_csv,
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
        help=(
            "writes asca-rule-inventory.csv (+ success/error splits), "
            "asca-rule-inventory-changelog.csv, "
            "manual_mappings_matched_rules.csv, and asca-rule-inventory-summary.md"
        ),
    )
    ap.add_argument("--probe-words", type=Path, default=DEFAULT_PROBE)
    ap.add_argument(
        "--skip-validation",
        action="store_true",
        help="ingest only; skip validate_asca inventory (when asca binary absent)",
    )
    ap.add_argument("--limit", type=int, default=0, help="optional cap for smoke tests")
    ap.add_argument(
        "--update-series-mappings",
        action="store_true",
        help=(
            "refresh data/asca/series_mappings.csv and series-mappings-coverage.md "
            "from HTML before parse"
        ),
    )
    ap.add_argument(
        "--reset-changelog",
        action="store_true",
        help=(
            "overwrite asca-rule-inventory-changelog.csv instead of appending "
            "(use after a column-schema change)"
        ),
    )
    args = ap.parse_args()

    if not args.html.is_file():
        print(f"ERROR: HTML not found at {args.html}", file=sys.stderr)
        return 1

    if args.update_series_mappings:
        row_count = update_series_mappings_from_html(
            args.html,
            csv_path=DEFAULT_SERIES_MAPPINGS_CSV,
            report_path=DEFAULT_SERIES_MAPPINGS_REPORT,
        )
        print(
            f"wrote {DEFAULT_SERIES_MAPPINGS_CSV} rows={row_count}\n"
            f"wrote {DEFAULT_SERIES_MAPPINGS_REPORT}"
        )

    tables = load_default_ingest_tables()
    parser = IndexDiachronicaParser(
        series_mappings=tables.series_mappings,
        manual_mappings=tables.manual_mappings,
        parser_config=tables.parser_config,
        feature_mappings=tables.feature_mappings,
        ipa_mappings=tables.ipa_mappings,
    )
    doc = parser.parse(args.html)
    write_cleaned_corpus(doc, args.yaml_out)
    n_with_comment = write_rule_comment_phrase_summary(doc, DEFAULT_COMMENT_SUMMARY)

    matched_path = args.inventory_dir / MANUAL_MAPPINGS_MATCHED_CSV_NAME
    write_manual_mappings_matched_csv(parser.manual_mapping_matches, matched_path)
    for unused in parser.unmatched_manual_mappings():
        print(
            f"WARNING: unmatched manual mapping from={unused.from_text!r}",
            file=sys.stderr,
        )

    n_sections = len(doc["sections"])
    n_rules = sum(len(s.get("rules") or []) for s in doc["sections"])
    n_skipped = sum(
        1
        for section in doc["sections"]
        for rule in section.get("rules") or []
        if rule.get("status") == "skipped"
    )
    print(
        f"wrote {args.yaml_out} sections={n_sections} rules={n_rules} "
        f"parse_skipped={n_skipped} rules_with_comment={n_with_comment}"
    )
    print(f"wrote {DEFAULT_COMMENT_SUMMARY}")
    print(f"wrote {matched_path} matches={len(parser.manual_mapping_matches)}")

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

    group_mappings = asca_group_mappings_dict()
    rows = list(
        iter_validation_rows(
            doc,
            probe_words=args.probe_words,
            group_mappings=group_mappings,
        )
    )
    if args.limit:
        rows = rows[: args.limit]

    csv_path = args.inventory_dir / INVENTORY_CSV_NAME
    success_path = args.inventory_dir / INVENTORY_SUCCESS_CSV_NAME
    error_path = args.inventory_dir / INVENTORY_ERROR_CSV_NAME
    changelog_path = args.inventory_dir / INVENTORY_CHANGELOG_CSV_NAME
    summary_path = args.inventory_dir / "asca-rule-inventory-summary.md"

    previous = load_inventory_csv(csv_path)
    current_df = validation_rows_to_dataframe(rows)
    run_timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    flips = ok_flip_changelog_rows(previous, current_df, timestamp=run_timestamp)

    write_validation_csv(rows, csv_path)
    write_filtered_inventory_csvs(current_df, args.inventory_dir)
    if args.reset_changelog and changelog_path.is_file():
        changelog_path.unlink()
    flip_n = append_ok_flip_changelog(flips, changelog_path)
    changelog_action = "reset" if args.reset_changelog else "appended"

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
        f"wrote {success_path} rows={ok_n}\n"
        f"wrote {error_path} rows={fail_n}\n"
        f"{changelog_action} {changelog_path} flips={flip_n} "
        f"timestamp={run_timestamp}\n"
        f"wrote {summary_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
