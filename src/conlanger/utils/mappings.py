"""CSV-backed Index→ASCA mapping tables shared across parse and compile."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

_DATA_ROOT = Path(__file__).resolve().parents[3] / "data"

DEFAULT_GROUP_MAPPINGS_CSV = _DATA_ROOT / "asca" / "group_mappings.csv"
DEFAULT_FEATURE_MAPPINGS_CSV = _DATA_ROOT / "asca" / "feature_mappings.csv"
DEFAULT_IPA_MAPPINGS_CSV = _DATA_ROOT / "common" / "ipa_mapping.csv"
DEFAULT_MANUAL_MAPPINGS_CSV = _DATA_ROOT / "common" / "manual_mappings.csv"
DEFAULT_PARSER_CONFIG_PATH = _DATA_ROOT / "parser_config.yml"
DEFAULT_IPA_MAPPING_CONFIDENCE = ["high"]
_SUPPORTED_FEATURE_MAPPING_KINDS = frozenset(
    {"rename", "rename_invert", "rename_polarity", "bundle"}
)

_CORPUS_CONTEXT_FIELD_KEYS = ("env", "exception")


@dataclass(frozen=True)
class GroupMapping:
    grouping: str
    mapping: str
    comment: str = ""


@dataclass(frozen=True)
class IpaMapping:
    index_feature: str
    ipa_target: str
    confidence: str = ""
    notes: str = ""


@dataclass(frozen=True)
class ManualMapping:
    """One owner-authored substring rewrite from ``manual_mappings.csv``."""

    from_text: str
    to_text: str
    reason: str = ""


@dataclass(frozen=True)
class ManualMappingHit:
    """A single substring replace performed by ``apply_manual_mappings``."""

    from_text: str
    to_text: str


@dataclass(frozen=True)
class ManualMappingMatch:
    """Debug row for a manual mapping applied during ingest."""

    section_index: str
    section_name: str
    rule_idx: int
    source: str
    manual_mapping: str


@dataclass(frozen=True)
class FeatureMapping:
    index_feature: str
    mapping_kind: str
    asca_target: str
    host: str = ""
    confidence: str = ""
    notes: str = ""


@dataclass(frozen=True)
class ParserConfig:
    ipa_mapping_confidence: frozenset[str]


def load_group_mappings(path: Path | None = None) -> list[GroupMapping]:
    """Load Index→ASCA group letter mappings from CSV."""
    csv_path = DEFAULT_GROUP_MAPPINGS_CSV if path is None else Path(path)
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    missing = {"grouping", "mapping"} - set(df.columns)
    if missing:
        raise ValueError(
            f"group mappings CSV missing required columns: {sorted(missing)}"
        )
    has_comment = "comment" in df.columns
    out: list[GroupMapping] = []
    for row in df.itertuples(index=False):
        out.append(
            GroupMapping(
                grouping=row.grouping,
                mapping=row.mapping,
                comment=row.comment if has_comment else "",
            )
        )
    return out


def load_feature_mappings(path: Path | None = None) -> list[FeatureMapping]:
    """Load Index→ASCA feature-matrix synonym mappings from CSV."""
    csv_path = DEFAULT_FEATURE_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    required = {"index_feature", "mapping_kind", "asca_target", "confidence"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"feature mappings CSV missing required columns: {sorted(missing)}"
        )
    out: list[FeatureMapping] = []
    for row in df.itertuples(index=False):
        kind = row.mapping_kind.strip()
        if kind not in _SUPPORTED_FEATURE_MAPPING_KINDS:
            raise ValueError(
                f"unsupported feature mapping_kind {kind!r} for "
                f"{row.index_feature!r} (supported: rename, rename_invert, rename_polarity, bundle)"
            )
        out.append(
            FeatureMapping(
                index_feature=row.index_feature,
                mapping_kind=kind,
                asca_target=row.asca_target,
                host=getattr(row, "host", "") if "host" in df.columns else "",
                confidence=row.confidence,
                notes=getattr(row, "notes", "") if "notes" in df.columns else "",
            )
        )
    return out


def feature_mappings_dict(
    path: Path | None = None,
) -> dict[str, FeatureMapping]:
    """Return feature mappings keyed by ``index_feature``."""
    return {row.index_feature: row for row in load_feature_mappings(path)}


def normalize_feature_matrices_in_field(
    text: str,
    mappings: dict[str, FeatureMapping],
) -> str:
    """Replace Index matrix feature names inside ``[...]`` with ASCA targets."""
    if not text or not mappings:
        return text
    names = sorted(mappings.keys(), key=len, reverse=True)
    feature_re = re.compile(
        r"([+-])\s*(" + "|".join(re.escape(name) for name in names) + r")(?![a-zA-Z])"
    )

    def replace_polarity_and_name(match: re.Match[str]) -> str:
        polarity, index_name = match.group(1), match.group(2)
        mapping = mappings[index_name]
        if mapping.mapping_kind == "bundle":
            return mapping.asca_target
        if mapping.mapping_kind == "rename":
            return f"{polarity}{mapping.asca_target}"
        if mapping.mapping_kind in ("rename_invert", "rename_polarity"):
            flipped = "-" if polarity == "+" else "+"
            return f"{flipped}{mapping.asca_target}"
        return match.group(0)

    def replace_bracket_inner(match: re.Match[str]) -> str:
        inner = feature_re.sub(replace_polarity_and_name, match.group(1))
        return f"[{inner}]"

    return re.sub(r"\[([^\]]*)\]", replace_bracket_inner, text)


def apply_feature_mappings(
    parts: dict[str, str],
    mappings: dict[str, FeatureMapping] | None = None,
) -> dict[str, str]:
    """Normalize Index feature matrix names in rule fields; ``raw`` unchanged upstream."""
    table = mappings if mappings is not None else feature_mappings_dict()
    if not table:
        return parts
    result = dict(parts)
    stages = result.get("stages")
    if stages is not None:
        result["stages"] = [
            normalize_feature_matrices_in_field(stage, table) for stage in stages
        ]
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key in result:
            result[key] = normalize_feature_matrices_in_field(result[key], table)
    return result


def load_parser_config(path: Path | None = None) -> ParserConfig:
    """Load parser runtime settings from YAML."""
    config_path = DEFAULT_PARSER_CONFIG_PATH if path is None else Path(path)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    confidence = raw.get("ipa_mapping", {}).get(
        "confidence", DEFAULT_IPA_MAPPING_CONFIDENCE
    )
    return ParserConfig(ipa_mapping_confidence=frozenset(confidence))


def load_ipa_mappings(path: Path | None = None) -> list[IpaMapping]:
    """Load Index→ASCA IPA character mappings from CSV."""
    csv_path = DEFAULT_IPA_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    required = {"index_feature", "ipa_target", "confidence"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"IPA mappings CSV missing required columns: {sorted(missing)}"
        )
    has_notes = "notes" in df.columns
    out: list[IpaMapping] = []
    for row in df.itertuples(index=False):
        out.append(
            IpaMapping(
                index_feature=row.index_feature,
                ipa_target=row.ipa_target,
                confidence=row.confidence,
                notes=row.notes if has_notes else "",
            )
        )
    return out


def ipa_mappings_dict(
    path: Path | None = None,
    *,
    config: ParserConfig | None = None,
) -> dict[str, str]:
    """Return IPA mappings keyed by Index character for configured confidence levels."""
    confidences = (
        config.ipa_mapping_confidence
        if config is not None
        else load_parser_config().ipa_mapping_confidence
    )
    return {
        row.index_feature: row.ipa_target
        for row in load_ipa_mappings(path)
        if row.confidence in confidences and row.ipa_target
    }


def normalize_ipa_in_field(text: str, mappings: dict[str, str]) -> str:
    """Replace Index IPA characters in one rule field with ASCA targets."""
    if not text or not mappings:
        return text
    for source in sorted(mappings.keys(), key=len, reverse=True):
        text = text.replace(source, mappings[source])
    return text


def apply_ipa_mappings(
    parts: dict[str, str],
    mappings: dict[str, str] | None = None,
    *,
    config: ParserConfig | None = None,
) -> dict[str, str]:
    """Normalize Index IPA characters in rule fields; ``raw`` unchanged upstream."""
    table = mappings if mappings is not None else ipa_mappings_dict(config=config)
    if not table:
        return parts
    result = dict(parts)
    stages = result.get("stages")
    if stages is not None:
        result["stages"] = [normalize_ipa_in_field(stage, table) for stage in stages]
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key in result:
            result[key] = normalize_ipa_in_field(result[key], table)
    return result


def load_manual_mappings(path: Path | None = None) -> list[ManualMapping]:
    """Load owner-authored rule rewrites from CSV (``from``, ``to``; optional ``reason``)."""
    csv_path = DEFAULT_MANUAL_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    required = {"from", "to"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"manual mappings CSV missing required columns: {sorted(missing)}"
        )
    has_reason = "reason" in df.columns
    seen: set[str] = set()
    out: list[ManualMapping] = []
    for record in df.to_dict(orient="records"):
        from_text = record["from"]
        if from_text in seen:
            raise ValueError(f"duplicate manual mapping from key: {from_text!r}")
        seen.add(from_text)
        out.append(
            ManualMapping(
                from_text=from_text,
                to_text=record["to"],
                reason=record["reason"] if has_reason else "",
            )
        )
    return out


def apply_manual_mappings(
    text: str,
    mappings: list[ManualMapping] | None = None,
) -> tuple[str, list[ManualMappingHit]]:
    """Replace ``from`` substrings with ``to`` (first occurrence each).

    Mappings are applied longest-``from`` first so a shorter pattern cannot steal
    a longer match when both would apply. Relative order among equal-length
    ``from`` keys follows CSV order (stable sort).
    """
    rows = mappings if mappings is not None else load_manual_mappings()
    if not text or not rows:
        return text, []
    ordered = sorted(rows, key=lambda row: len(row.from_text), reverse=True)
    working = text
    hits: list[ManualMappingHit] = []
    for row in ordered:
        if row.from_text and row.from_text in working:
            working = working.replace(row.from_text, row.to_text, 1)
            hits.append(ManualMappingHit(from_text=row.from_text, to_text=row.to_text))
    return working, hits


MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS = [
    "section_index",
    "section_name",
    "rule_idx",
    "source",
    "manual_mapping",
]
MANUAL_MAPPINGS_MATCHED_CSV_NAME = "manual_mappings_matched_rules.csv"


def write_manual_mappings_matched_csv(
    matches: list[ManualMappingMatch],
    path: Path,
) -> Path:
    """Rewrite debug CSV of manual mapping hits (one row per applied pattern)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "section_index": match.section_index,
            "section_name": match.section_name,
            "rule_idx": match.rule_idx,
            "source": match.source,
            "manual_mapping": match.manual_mapping,
        }
        for match in matches
    ]
    df = pd.DataFrame(rows, columns=MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS)
    df.to_csv(path, index=False)
    return path
