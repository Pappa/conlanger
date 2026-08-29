"""Checks unit test coverage per file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

COVERAGE_JSON = ROOT / ".coverage.json"
DEFAULT_MIN_COVERAGE = 85


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-coverage", type=float, default=DEFAULT_MIN_COVERAGE)
    parser.add_argument("--coverage-json", type=Path, default=COVERAGE_JSON)
    args = parser.parse_args()

    with open(args.coverage_json, "r") as f:
        coverage_data = json.load(f).get("files", {})

    coverage_status = 0

    for file, data in coverage_data.items():
        coverage = data.get("summary", {}).get("percent_covered", 0)
        if coverage < args.min_coverage:
            print(f"{file} coverage is {coverage:.2f}%")
            coverage_status = 1

    if coverage_status == 1:
        print(f"Coverage is below the minimum threshold: {args.min_coverage:.2f}%")

    return coverage_status


if __name__ == "__main__":
    raise SystemExit(main())
