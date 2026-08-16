"""
Refreshes ``data/asca/series_mappings.csv`` and ``data/diachronica/section_abbreviations.yml``.
"""

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from conlanger.tools.series_extract import (
    DEFAULT_SERIES_MAPPINGS_REPORT,
    update_series_mappings_from_html,
)
from conlanger.utils.file_io import (
    DEFAULT_SECTION_ABBREVIATIONS_YML,
    DEFAULT_SERIES_MAPPINGS_CSV,
)

DEFAULT_HTML = ROOT / "data" / "diachronica" / "index_diachronica_original.html"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", type=Path, default=DEFAULT_HTML)
    args = ap.parse_args()

    if not args.html.is_file():
        print(f"ERROR: HTML not found at {args.html}", file=sys.stderr)
        return 1

    row_count = update_series_mappings_from_html(
        args.html,
        csv_path=DEFAULT_SERIES_MAPPINGS_CSV,
        report_path=DEFAULT_SERIES_MAPPINGS_REPORT,
        abbreviations_path=DEFAULT_SECTION_ABBREVIATIONS_YML,
    )
    print(
        f"wrote {DEFAULT_SERIES_MAPPINGS_CSV} rows={row_count}\n"
        f"wrote {DEFAULT_SECTION_ABBREVIATIONS_YML}\n"
        f"wrote {DEFAULT_SERIES_MAPPINGS_REPORT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
