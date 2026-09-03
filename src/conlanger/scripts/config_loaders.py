"""YAML config loaders for operator settings under ``config/`` (scripts-only I/O)."""

from __future__ import annotations

from pathlib import Path

import yaml

from conlanger.utils.mappings import (
    CompilerConfig,
    FeatureMapping,
    IpaMapping,
    ManualMapping,
    ParserConfig,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_ROOT = _REPO_ROOT / "config"

_DEFAULT_PARSER_CONFIG = _CONFIG_ROOT / "parser" / "parser_config.yml"
_DEFAULT_MANUAL_MAPPINGS = _CONFIG_ROOT / "parser" / "manual_mappings.yml"
_DEFAULT_IPA_MAPPINGS = _CONFIG_ROOT / "parser" / "ipa_mappings.yml"
_DEFAULT_FEATURE_MAPPINGS = _CONFIG_ROOT / "parser" / "feature_mappings.yml"
_DEFAULT_CORRECTIONS = _CONFIG_ROOT / "parser" / "index_diachronica_corrections.yml"
_DEFAULT_COMPILER_CONFIG = _CONFIG_ROOT / "compile" / "asca" / "compiler_config.yml"
_DEFAULT_GROUP_MAPPINGS = _CONFIG_ROOT / "compile" / "asca" / "group_mappings.yml"

_SUPPORTED_FEATURE_MAPPING_KINDS = frozenset(
    {"rename", "rename_invert", "rename_polarity", "bundle", "tone"}
)


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _parse_skip_section_ids(raw: object) -> frozenset[str]:
    if not isinstance(raw, list):
        return frozenset()
    ids: set[str] = set()
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        section_id = entry.get("id")
        if section_id:
            ids.add(str(section_id))
    return frozenset(ids)


def _parse_skip_rules(raw: object) -> tuple[frozenset[str], dict[str, str]]:
    if not isinstance(raw, list):
        return frozenset(), {}
    ids: set[str] = set()
    comments: dict[str, str] = {}
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        rule_id = entry.get("id")
        if not rule_id:
            continue
        rule_id = str(rule_id)
        ids.add(rule_id)
        reason = entry.get("reason")
        if reason:
            comments[rule_id] = str(reason)
    return frozenset(ids), comments


def _parse_series_expansions(raw: object) -> dict[str, tuple[str, ...]]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, tuple[str, ...]] = {}
    for token, members in raw.items():
        if isinstance(members, list):
            out[str(token)] = tuple(str(m) for m in members)
    return out


def _parse_section_mappings(raw: object) -> dict[str, dict[str, str]]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, dict[str, str]] = {}
    for section_key, token_map in raw.items():
        if not isinstance(token_map, dict):
            continue
        out[str(section_key)] = {
            str(token): str(target) for token, target in token_map.items()
        }
    return out


def _load_manual_mappings(path: Path) -> list[ManualMapping]:
    if not path.is_file():
        return []
    raw = _load_yaml(path)
    if not isinstance(raw, list):
        return []
    seen: set[str] = set()
    out: list[ManualMapping] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        from_text = str(entry.get("from", ""))
        if from_text in seen:
            raise ValueError(f"duplicate manual mapping from key: {from_text!r}")
        seen.add(from_text)
        out.append(
            ManualMapping(
                from_text=from_text,
                to_text=str(entry.get("to", "")),
                reason=str(entry.get("reason", "")),
                use_regex=bool(entry.get("use_regex", False)),
            )
        )
    return out


def _load_ipa_mappings(path: Path) -> tuple[IpaMapping, ...]:
    if not path.is_file():
        return ()
    raw = _load_yaml(path)
    out: list[IpaMapping] = []
    for index_feature, entry in raw.items():
        if isinstance(entry, str):
            out.append(IpaMapping(index_feature=str(index_feature), ipa_target=entry))
            continue
        if not isinstance(entry, dict):
            continue
        confidence = entry.get("confidence")
        out.append(
            IpaMapping(
                index_feature=str(index_feature),
                ipa_target=str(entry.get("ipa_target", "")),
                confidence=str(confidence) if confidence is not None else None,
                notes=str(entry.get("notes", "")),
            )
        )
    return tuple(out)


def _load_feature_mappings(path: Path) -> dict[str, FeatureMapping]:
    if not path.is_file():
        return {}
    raw = _load_yaml(path)
    if not isinstance(raw, dict):
        return {}
    out: dict[str, FeatureMapping] = {}
    for index_feature, entry in raw.items():
        if not isinstance(entry, dict):
            continue
        kind = str(entry.get("mapping_kind", "")).strip()
        if kind not in _SUPPORTED_FEATURE_MAPPING_KINDS:
            raise ValueError(
                f"unsupported feature mapping_kind {kind!r} for "
                f"{index_feature!r} (supported: rename, rename_invert, "
                f"rename_polarity, bundle, tone)"
            )
        out[str(index_feature)] = FeatureMapping(
            index_feature=str(index_feature),
            mapping_kind=kind,
            asca_target=str(entry.get("asca_target", "")),
            host=str(entry.get("host", "")),
            confidence=str(entry.get("confidence", "")),
            notes=str(entry.get("notes", "")),
        )
    return out


def _load_corrections(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    raw = _load_yaml(path)
    if not isinstance(raw, dict):
        return {}
    rules_list = raw.get("rules")
    if not isinstance(rules_list, list):
        return {}
    out: dict[str, str] = {}
    for entry in rules_list:
        if not isinstance(entry, dict):
            continue
        rule = entry.get("rule")
        if not isinstance(rule, dict):
            continue
        rule_id = rule.get("id")
        content = rule.get("content")
        if rule_id is None or content is None:
            continue
        content_str = str(content).strip()
        if not content_str:
            continue
        out[str(rule_id)] = content_str
    return out


def _load_group_mappings(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    raw = _load_yaml(path)
    if not isinstance(raw, dict):
        return {}
    out: dict[str, str] = {}
    for grouping, entry in raw.items():
        if isinstance(entry, str):
            out[str(grouping)] = entry
        elif isinstance(entry, dict):
            out[str(grouping)] = str(entry.get("mapping", ""))
    return out


def _load_compiler_series(
    raw: object,
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    if not isinstance(raw, dict):
        return {}, {}
    series = raw.get("series_mappings") or {}
    if not isinstance(series, dict):
        return {}, {}
    raw_global = series.get("global") or {}
    global_map = (
        {str(token): str(target) for token, target in raw_global.items()}
        if isinstance(raw_global, dict)
        else {}
    )
    sections: dict[str, dict[str, str]] = {}
    for entry in series.get("sections") or []:
        if not isinstance(entry, dict) or entry.get("section") is None:
            continue
        section_key = str(entry["section"])
        token_map = {
            str(token): str(target)
            for token, target in entry.items()
            if token != "section"
        }
        sections[section_key] = token_map
    return global_map, sections


def load_parser_config(path: Path | None = None) -> ParserConfig:
    """Load a fat ``ParserConfig`` from ``config/parser/`` YAML fragments."""
    config_root = _CONFIG_ROOT / "parser" if path is None else Path(path).parent
    parser_yaml = _DEFAULT_PARSER_CONFIG if path is None else Path(path)

    raw = _load_yaml(parser_yaml)
    confidence_raw = raw.get("ipa_mappings", {})
    if isinstance(confidence_raw, dict) and "confidence" in confidence_raw:
        confidence_list = confidence_raw["confidence"]
        ipa_confidence = (
            frozenset(str(c) for c in confidence_list)
            if isinstance(confidence_list, list)
            else None
        )
    else:
        ipa_confidence = None

    skip_rule_ids, skip_rule_comments = _parse_skip_rules(raw.get("skip_rules"))

    manual_path = config_root / "manual_mappings.yml"
    ipa_path = config_root / "ipa_mappings.yml"
    feature_path = config_root / "feature_mappings.yml"
    corrections_path = config_root / "index_diachronica_corrections.yml"

    return ParserConfig(
        manual_mappings=_load_manual_mappings(manual_path),
        ipa_mappings=_load_ipa_mappings(ipa_path),
        ipa_mappings_confidence=ipa_confidence,
        feature_mappings=_load_feature_mappings(feature_path),
        corrections=_load_corrections(corrections_path),
        series_expansions=_parse_series_expansions(raw.get("series_expansions")),
        section_mappings_sections=_parse_section_mappings(raw.get("section_mappings")),
        skip_section_ids=_parse_skip_section_ids(raw.get("skip_sections")),
        skip_rule_ids=skip_rule_ids,
        skip_rule_comments=skip_rule_comments,
    )


def load_compiler_config(path: Path | None = None) -> CompilerConfig:
    """Load a fat ``CompilerConfig`` from ``config/compile/asca/`` YAML fragments."""
    config_root = (
        _CONFIG_ROOT / "compile" / "asca" if path is None else Path(path).parent
    )
    compiler_yaml = _DEFAULT_COMPILER_CONFIG if path is None else Path(path)

    raw = _load_yaml(compiler_yaml)
    global_map, sections = _load_compiler_series(raw)
    group_path = config_root / "group_mappings.yml"

    return CompilerConfig(
        group_mappings=_load_group_mappings(group_path),
        series_mappings_global=global_map,
        series_mappings_sections=sections,
    )
