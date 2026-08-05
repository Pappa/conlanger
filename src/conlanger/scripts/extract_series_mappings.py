"""Extract correspondence-series mappings from Index Diachronica HTML.

Writes ``data/asca/series_mappings.csv`` and a coverage report under
``.scratch/cleaned-rule-corpus/``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from conlanger.tools.series_mappings import (
    DEFAULT_SERIES_MAPPINGS_CSV,
    extract_series_mappings_from_html,
    write_coverage_report,
    write_series_mappings_csv,
)

DEFAULT_HTML = ROOT / "data" / "diachronica" / "index_diachronica_original.html"
DEFAULT_REPORT = (
    ROOT / ".scratch" / "cleaned-rule-corpus" / "series-mappings-coverage.md"
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", type=Path, default=DEFAULT_HTML)
    ap.add_argument("--csv-out", type=Path, default=DEFAULT_SERIES_MAPPINGS_CSV)
    ap.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    args = ap.parse_args()

    if not args.html.is_file():
        print(f"ERROR: HTML not found at {args.html}", file=sys.stderr)
        return 1

    rows = extract_series_mappings_from_html(args.html)
    write_series_mappings_csv(rows, args.csv_out)
    write_coverage_report(args.html, args.csv_out, args.report_out)
    print(f"wrote {args.csv_out} rows={len(rows)}")
    print(f"wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
