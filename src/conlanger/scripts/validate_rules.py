"""Compile and validate parsed index YAML; write ASCA validation inventory.

Loads applier-neutral index from disk, compiles each rule to ASCA in memory for
compile validation only, and writes inventory CSVs and summary markdown.
"""

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from conlanger.appliers.asca import asca_supports_validate
from conlanger.scripts.config_loaders import load_compiler_config
from conlanger.scripts.pipeline_defaults import (
    DEFAULT_INVENTORY_DIR,
    DEFAULT_PROBE,
    DEFAULT_YAML,
    ROOT,
)
from conlanger.scripts.validation_cli import (
    asca_version,
    fork_asca_command,
    validation_asca_command,
)
from conlanger.tools.index_inventory import (
    FIELD_ISOLATION_ERROR_CSV_NAME,
    FIELD_ISOLATION_SUCCESS_CSV_NAME,
    INVENTORY_CHANGELOG_CSV_NAME,
    INVENTORY_ERROR_CSV_NAME,
    INVENTORY_SUCCESS_CSV_NAME,
    append_ok_flip_changelog,
    filter_inventory_by_ok,
    iter_inventory_with_field_isolation,
    load_inventory_csv,
    ok_flip_changelog_rows,
    summarize_inventory,
    validation_rows_to_dataframe,
    write_field_isolation_csvs,
    write_filtered_inventory_csvs,
)
from conlanger.tools.index_io import read_cleaned_index
from conlanger.tools.inventory_error_clusters import write_error_cluster_csvs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--yaml-in", type=Path, default=DEFAULT_YAML)
    ap.add_argument(
        "--inventory-dir",
        type=Path,
        default=DEFAULT_INVENTORY_DIR,
        help=(
            "writes asca-rule-inventory-success.csv / -error.csv, "
            "asca-field-isolation-success.csv / -error.csv (when --field-isolation), "
            "asca-rule-inventory-changelog.csv, "
            "error cluster CSVs, "
            "and asca-rule-inventory-summary.md"
        ),
    )
    ap.add_argument(
        "--field-isolation",
        action=argparse.BooleanOptionalAction,
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

    if not args.yaml_in.is_file():
        print(f"ERROR: parsed YAML not found at {args.yaml_in}", file=sys.stderr)
        return 1

    if not args.probe_words.is_file():
        print(f"ERROR: probe wordlist not found at {args.probe_words}", file=sys.stderr)
        return 1

    asca_command = validation_asca_command(
        use_fork=args.use_asca_fork,
        repo_root=ROOT,
    )
    if args.use_asca_fork and asca_command is None:
        fork = fork_asca_command(repo_root=ROOT)
        print(
            f"ERROR: asca fork not found at {fork} "
            "(install with cargo per docs/DEV.md, or pass --no-use-asca-fork)",
            file=sys.stderr,
        )
        return 1

    if asca_command is None:
        print(
            "ERROR: asca binary not found "
            "(install the fork per docs/DEV.md or use --use-asca-fork)",
            file=sys.stderr,
        )
        return 1

    if not asca_supports_validate(asca_bin=asca_command):
        print(
            "ERROR: asca binary lacks the validate subcommand "
            "(install the fork from docs/DEV.md, or use --no-use-asca-fork)",
            file=sys.stderr,
        )
        return 1

    doc = read_cleaned_index(args.yaml_in)
    compiler_config = load_compiler_config()
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
    error_df = filter_inventory_by_ok(current_df, ok=False)
    write_error_cluster_csvs(error_df, args.inventory_dir)
    if args.field_isolation:
        write_field_isolation_csvs(field_rows, args.inventory_dir)
    if args.reset_changelog and changelog_path.is_file():
        changelog_path.unlink()
    flip_n = append_ok_flip_changelog(flips, changelog_path)
    changelog_action = "reset" if args.reset_changelog else "appended"

    summary = summarize_inventory(
        rows,
        source_yaml=str(args.yaml_in.relative_to(ROOT)),
        probe_words=str(args.probe_words.relative_to(ROOT)),
        asca_version=asca_version(asca_command),
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
