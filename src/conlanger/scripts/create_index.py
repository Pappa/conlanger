"""Create cleaned index YAML and ASCA validation inventory from Index HTML.

Ticket 12: one invocation emits cleaned YAML, validation CSV, and summary markdown.
Uses ticket-11 extract-only ingest (``IndexDiachronicaParser``) and ``validate_asca``.
Series mappings are no longer refreshed at regen (retired parse-time CSV; see ticket 74).
"""

import argparse
import logging
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from conlanger.appliers.asca import asca_supports_validate, resolve_asca_bin
from conlanger.scripts.config_loaders import load_compiler_config, load_parser_config
from conlanger.tools.index_inventory import (
    FIELD_ISOLATION_ERROR_CSV_NAME,
    FIELD_ISOLATION_SUCCESS_CSV_NAME,
    INVENTORY_CHANGELOG_CSV_NAME,
    INVENTORY_ERROR_CSV_NAME,
    INVENTORY_SUCCESS_CSV_NAME,
    append_ok_flip_changelog,
    iter_inventory_with_field_isolation,
    load_inventory_csv,
    ok_flip_changelog_rows,
    summarize_inventory,
    validation_rows_to_dataframe,
    write_field_isolation_csvs,
    write_filtered_inventory_csvs,
)
from conlanger.tools.index_io import write_cleaned_index
from conlanger.tools.ingest import (
    IndexDiachronicaParser,
    write_rule_comment_phrase_summary,
)
from conlanger.utils.file_io import (
    MANUAL_MAPPINGS_MATCHED_CSV_NAME,
    write_manual_mappings_matched_csv,
)

DEFAULT_HTML = ROOT / "data" / "diachronica" / "index_diachronica_original.html"
DEFAULT_YAML = ROOT / "data" / "diachronica" / "index_diachronica_parsed.yml"
DEFAULT_INVENTORY_DIR = ROOT / ".scratch" / "cleaned-rule-index" / "inventory"
DEFAULT_COMMENT_SUMMARY = (
    ROOT / ".scratch" / "cleaned-rule-index" / "rule-comment-phrases.md"
)
DEFAULT_PROBE = ROOT / "tests" / "fixtures" / "asca_probe_words.wsca"


def _fork_asca_command(*, repo_root: Path = ROOT) -> Path:
    return repo_root / "bin" / "bin" / "asca"


def _validation_asca_command(*, use_fork: bool, repo_root: Path = ROOT) -> str | None:
    """Return the asca executable path for inventory validation."""
    if use_fork:
        fork = _fork_asca_command(repo_root=repo_root)
        return str(fork) if fork.is_file() else None
    return resolve_asca_bin()


def _asca_version(asca_bin: str) -> str:
    try:
        proc = subprocess.run(  # noqa: PLW1510
            [asca_bin, "--version"],
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
            "writes asca-rule-inventory-success.csv / -error.csv, "
            "asca-field-isolation-success.csv / -error.csv (when --field-isolation), "
            "asca-rule-inventory-changelog.csv, "
            "manual_mappings_matched_rules.csv, and asca-rule-inventory-summary.md"
        ),
    )
    ap.add_argument(
        "--field-isolation",
        type=bool,
        default=False,
        help=("run asca-field-isolation (default: False)"),
    )
    ap.add_argument("--probe-words", type=Path, default=DEFAULT_PROBE)
    ap.add_argument(
        "--use-asca-fork",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "use the repo-local asca fork at bin/bin/asca for validation "
            "(default: on; off uses ASCA_BIN or PATH)"
        ),
    )
    ap.add_argument(
        "--skip-validation",
        action="store_true",
        help="ingest only; skip validate_asca inventory (when asca binary absent)",
    )
    ap.add_argument("--limit", type=int, default=0, help="optional cap for smoke tests")
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

    parser_config = load_parser_config()
    compiler_config = load_compiler_config()
    parser = IndexDiachronicaParser(parser_config)
    doc = parser.parse(args.html)
    write_cleaned_index(doc, args.yaml_out)
    n_with_comment = write_rule_comment_phrase_summary(doc, DEFAULT_COMMENT_SUMMARY)

    matched_path = args.inventory_dir / MANUAL_MAPPINGS_MATCHED_CSV_NAME
    write_manual_mappings_matched_csv(parser.manual_mapping_matches, matched_path)
    for unused in parser.unmatched_manual_mappings():
        print(
            f"WARNING: unmatched manual mapping from={unused.from_text!r}",
            file=sys.stderr,
        )
    for unused_id in parser.unmatched_corrections():
        print(
            f"WARNING: unmatched correction rule_id={unused_id!r}",
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

    asca_command = _validation_asca_command(
        use_fork=args.use_asca_fork,
        repo_root=ROOT,
    )
    if args.use_asca_fork and asca_command is None:
        fork = _fork_asca_command(repo_root=ROOT)
        print(
            f"ERROR: asca fork not found at {fork} "
            "(install with cargo per docs/DEV.md, or pass --no-use-asca-fork)",
            file=sys.stderr,
        )
        return 1

    if asca_command is None:
        print(
            "ERROR: asca binary not found "
            "(install the fork per docs/DEV.md or use --use-asca-fork, "
            "or use --skip-validation)",
            file=sys.stderr,
        )
        return 1

    if not asca_supports_validate(asca_bin=asca_command):
        print(
            "ERROR: asca binary lacks the validate subcommand "
            "(install the fork from docs/DEV.md, or use --no-use-asca-fork, "
            "or use --skip-validation)",
            file=sys.stderr,
        )
        return 1

    rows, field_rows = iter_inventory_with_field_isolation(
        doc,
        field_isolation=args.field_isolation,
        probe_words=args.probe_words,
        compiler_config=compiler_config,
        asca_bin=asca_command,
    )
    if args.limit:
        rows = rows[: args.limit]
        field_rows = field_rows[: args.limit]

    success_path = args.inventory_dir / INVENTORY_SUCCESS_CSV_NAME
    error_path = args.inventory_dir / INVENTORY_ERROR_CSV_NAME
    field_success_path = args.inventory_dir / FIELD_ISOLATION_SUCCESS_CSV_NAME
    field_error_path = args.inventory_dir / FIELD_ISOLATION_ERROR_CSV_NAME
    changelog_path = args.inventory_dir / INVENTORY_CHANGELOG_CSV_NAME
    summary_path = args.inventory_dir / "asca-rule-inventory-summary.md"

    previous = load_inventory_csv(args.inventory_dir)
    current_df = validation_rows_to_dataframe(rows)
    run_timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    flips = ok_flip_changelog_rows(previous, current_df, timestamp=run_timestamp)

    write_filtered_inventory_csvs(current_df, args.inventory_dir)
    if args.field_isolation:
        write_field_isolation_csvs(field_rows, args.inventory_dir)
    if args.reset_changelog and changelog_path.is_file():
        changelog_path.unlink()
    flip_n = append_ok_flip_changelog(flips, changelog_path)
    changelog_action = "reset" if args.reset_changelog else "appended"

    summary = summarize_inventory(
        rows,
        source_yaml=str(args.yaml_out.relative_to(ROOT)),
        probe_words=str(args.probe_words.relative_to(ROOT)),
        asca_version=_asca_version(asca_command),
        field_isolation_rows=field_rows,
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary, encoding="utf-8")

    ok_n = sum(1 for row in rows if row.ok)
    fail_n = len(rows) - ok_n
    field_ok_n = sum(1 for row in field_rows if row.whole_ok)
    field_fail_n = len(field_rows) - field_ok_n
    lines = [
        f"wrote {success_path} rows={ok_n}",
        f"wrote {error_path} rows={fail_n}",
    ]
    if args.field_isolation:
        lines.extend(
            [
                f"wrote {field_success_path} rows={field_ok_n}",
                f"wrote {field_error_path} rows={field_fail_n}",
            ]
        )
    lines.extend(
        [
            (
                f"{changelog_action} {changelog_path} flips={flip_n} "
                f"timestamp={run_timestamp}"
            ),
            f"wrote {summary_path}",
        ]
    )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
