"""CSV I/O helpers for inventory and debug outputs (no config loading)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from conlanger.utils.mappings import ManualMappingMatch

MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS = [
    "section_index",
    "section_name",
    "rule_id",
    "source",
    "from_text",
    "to_text",
]
MANUAL_MAPPINGS_MATCHED_CSV_NAME = "manual_mappings_matched_rules.csv"


def write_csv_rows(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    """Write string rows to CSV with an explicit column order."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(path, index=False)


def write_manual_mappings_matched_csv(
    matches: list[ManualMappingMatch],
    path: Path,
) -> Path:
    """Rewrite debug CSV of manual mapping hits (one row per applied pattern)."""
    rows = [match.model_dump() for match in matches]
    write_csv_rows(path, rows, MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS)
    return Path(path)
