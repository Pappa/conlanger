"""CSV/YAML I/O for mapping tables and parser config (no apply/classify logic)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from conlanger.utils.mappings import (
    FeatureMapping,
    GroupMapping,
    IpaMapping,
    ManualMapping,
    ManualMappingMatch,
    ParserConfig,
)
from conlanger.utils.series import SeriesMapping

_DATA_ROOT = Path(__file__).resolve().parents[3] / "data"

DEFAULT_GROUP_MAPPINGS_CSV = _DATA_ROOT / "asca" / "group_mappings.csv"
DEFAULT_FEATURE_MAPPINGS_CSV = _DATA_ROOT / "asca" / "feature_mappings.csv"
DEFAULT_IPA_MAPPINGS_CSV = _DATA_ROOT / "common" / "ipa_mappings.csv"
DEFAULT_MANUAL_MAPPINGS_CSV = _DATA_ROOT / "common" / "manual_mappings.csv"
DEFAULT_SERIES_MAPPINGS_CSV = _DATA_ROOT / "asca" / "series_mappings.csv"
DEFAULT_SECTION_ABBREVIATIONS_YML = (
    _DATA_ROOT / "diachronica" / "section_abbreviations.yml"
)
DEFAULT_INDEX_DIACHRONICA_CORRECTIONS = (
    _DATA_ROOT / "diachronica" / "index_diachronica_corrections.yml"
)
DEFAULT_PARSER_CONFIG_PATH = _DATA_ROOT / "parser_config.yml"
DEFAULT_IPA_MAPPING_CONFIDENCE = ["high"]

_SUPPORTED_FEATURE_MAPPING_KINDS = frozenset(
    {"rename", "rename_invert", "rename_polarity", "bundle", "tone"}
)

MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS = [
    "section_index",
    "section_name",
    "rule_id",
    "source",
    "manual_mapping",
]
MANUAL_MAPPINGS_MATCHED_CSV_NAME = "manual_mappings_matched_rules.csv"


def read_csv_rows(path: Path, *, required_columns: set[str]) -> list[dict[str, str]]:
    """Read a CSV as string rows; raise if required columns are missing."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} missing required columns: {sorted(missing)}")
    return [
        {str(k): str(v) for k, v in record.items()}
        for record in df.to_dict(orient="records")
    ]


def write_csv_rows(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    """Write string rows to CSV with an explicit column order."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(path, index=False)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_group_mappings(path: Path | None = None) -> list[GroupMapping]:
    """Load Index→ASCA group letter mappings from CSV."""
    csv_path = DEFAULT_GROUP_MAPPINGS_CSV if path is None else Path(path)
    records = read_csv_rows(csv_path, required_columns={"grouping", "mapping"})
    return [
        GroupMapping(
            grouping=row["grouping"],
            mapping=row["mapping"],
            comment=row.get("comment", ""),
        )
        for row in records
    ]


def load_feature_mappings(path: Path | None = None) -> list[FeatureMapping]:
    """Load Index→ASCA feature-matrix synonym mappings from CSV."""
    csv_path = DEFAULT_FEATURE_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    records = read_csv_rows(
        csv_path,
        required_columns={"index_feature", "mapping_kind", "asca_target", "confidence"},
    )
    out: list[FeatureMapping] = []
    for row in records:
        kind = row["mapping_kind"].strip()
        if kind not in _SUPPORTED_FEATURE_MAPPING_KINDS:
            raise ValueError(
                f"unsupported feature mapping_kind {kind!r} for "
                f"{row['index_feature']!r} (supported: rename, rename_invert, "
                f"rename_polarity, bundle, tone)"
            )
        out.append(
            FeatureMapping(
                index_feature=row["index_feature"],
                mapping_kind=kind,
                asca_target=row["asca_target"],
                host=row.get("host", ""),
                confidence=row["confidence"],
                notes=row.get("notes", ""),
            )
        )
    return out


def feature_mappings_dict(
    path: Path | None = None,
) -> dict[str, FeatureMapping]:
    """Return feature mappings keyed by ``index_feature``."""
    return {row.index_feature: row for row in load_feature_mappings(path)}


def load_parser_config(path: Path | None = None) -> ParserConfig:
    """Load parser runtime settings from YAML."""
    config_path = DEFAULT_PARSER_CONFIG_PATH if path is None else Path(path)
    raw = _load_yaml(config_path)
    confidence = raw.get("ipa_mappings", {}).get(
        "confidence", DEFAULT_IPA_MAPPING_CONFIDENCE
    )
    raw_expansions = raw.get("series_expansions") or {}
    series_expansions: dict[str, tuple[str, ...]] = {}
    for token, members in raw_expansions.items():
        if isinstance(members, list):
            series_expansions[str(token)] = tuple(str(m) for m in members)
    return ParserConfig(
        ipa_mappings_confidence=frozenset(confidence),
        series_expansions=series_expansions,
    )


def load_index_diachronica_corrections(
    path: Path | None = None,
) -> dict[str, str]:
    """Load flat rule-id → Unicode line corrections overlay."""
    yml_path = DEFAULT_INDEX_DIACHRONICA_CORRECTIONS if path is None else Path(path)
    if not yml_path.is_file():
        return {}
    raw = _load_yaml(yml_path)
    if not isinstance(raw, dict):
        return {}
    return {
        str(key): str(value)
        for key, value in raw.items()
        if value is not None and str(value).strip()
    }


def load_ipa_mappings(path: Path | None = None) -> list[IpaMapping]:
    """Load Index→ASCA IPA character mappings from CSV."""
    csv_path = DEFAULT_IPA_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    records = read_csv_rows(
        csv_path, required_columns={"index_feature", "ipa_target", "confidence"}
    )
    return [
        IpaMapping(
            index_feature=row["index_feature"],
            ipa_target=row["ipa_target"],
            confidence=row["confidence"],
            notes=row.get("notes", ""),
        )
        for row in records
    ]


def ipa_mappings_dict(
    path: Path | None = None,
    *,
    config: ParserConfig | None = None,
) -> dict[str, str]:
    """Return IPA mappings keyed by Index character for configured confidence levels."""
    confidences = (
        config.ipa_mappings_confidence
        if config is not None
        else load_parser_config().ipa_mappings_confidence
    )
    return {
        row.index_feature: row.ipa_target
        for row in load_ipa_mappings(path)
        if row.confidence in confidences and row.ipa_target
    }


def load_manual_mappings(path: Path | None = None) -> list[ManualMapping]:
    """Load owner-authored rule rewrites from CSV (``from``, ``to``; optional ``reason``)."""
    csv_path = DEFAULT_MANUAL_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    records = read_csv_rows(csv_path, required_columns={"from", "to"})
    seen: set[str] = set()
    out: list[ManualMapping] = []
    for row in records:
        from_text = row["from"]
        if from_text in seen:
            raise ValueError(f"duplicate manual mapping from key: {from_text!r}")
        seen.add(from_text)
        out.append(
            ManualMapping(
                from_text=from_text,
                to_text=row["to"],
                reason=row.get("reason", ""),
            )
        )
    return out


def write_manual_mappings_matched_csv(
    matches: list[ManualMappingMatch],
    path: Path,
) -> Path:
    """Rewrite debug CSV of manual mapping hits (one row per applied pattern)."""
    rows = [
        {
            "section_index": match.section_index,
            "section_name": match.section_name,
            "rule_id": match.rule_id,
            "source": match.source,
            "manual_mapping": match.manual_mapping,
        }
        for match in matches
    ]
    write_csv_rows(path, rows, MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS)
    return Path(path)


def load_series_mappings(path: Path | None = None) -> list[SeriesMapping]:
    """Load correspondence-series mappings from CSV."""
    csv_path = DEFAULT_SERIES_MAPPINGS_CSV if path is None else Path(path)
    records = read_csv_rows(
        csv_path, required_columns={"section_index", "token", "asca_target"}
    )
    return [
        SeriesMapping(
            section_index=row["section_index"],
            token=row["token"],
            asca_target=row["asca_target"],
            source=row.get("source", ""),
            notes=row.get("notes", ""),
        )
        for row in records
    ]


def _dedupe_series_rows(rows: list[SeriesMapping]) -> list[SeriesMapping]:
    """Keep the first row per (section_index, token); extraction order = priority."""
    seen: set[tuple[str, str]] = set()
    out: list[SeriesMapping] = []
    for row in rows:
        key = (row.section_index, row.token)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def write_series_mappings_csv(rows: list[SeriesMapping], path: Path) -> None:
    """Dedupe, sort, and write series mappings CSV."""
    deduped = _dedupe_series_rows(rows)
    deduped.sort(key=lambda row: (row.section_index, row.token))
    write_csv_rows(
        path,
        [
            {
                "section_index": row.section_index,
                "token": row.token,
                "asca_target": row.asca_target,
                "source": row.source,
                "notes": row.notes,
            }
            for row in deduped
        ],
        ["section_index", "token", "asca_target", "source", "notes"],
    )


@dataclass(frozen=True)
class DefaultIngestTables:
    """Package-default tables for Index Diachronica ingest."""

    manual_mappings: list[ManualMapping]
    parser_config: ParserConfig
    feature_mappings: dict[str, FeatureMapping]
    ipa_mappings: dict[str, str]
    corrections: dict[str, str]


def load_default_ingest_tables(
    *,
    manual_mappings_path: Path | None = None,
    parser_config_path: Path | None = None,
    feature_mappings_path: Path | None = None,
    ipa_mappings_path: Path | None = None,
    corrections_path: Path | None = None,
) -> DefaultIngestTables:
    """Load all parse-time mapping tables from package defaults (or overrides)."""
    parser_config = load_parser_config(parser_config_path)
    return DefaultIngestTables(
        manual_mappings=load_manual_mappings(manual_mappings_path),
        parser_config=parser_config,
        feature_mappings=feature_mappings_dict(feature_mappings_path),
        ipa_mappings=ipa_mappings_dict(ipa_mappings_path, config=parser_config),
        corrections=load_index_diachronica_corrections(corrections_path),
    )
