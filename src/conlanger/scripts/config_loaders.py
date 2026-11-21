"""YAML config loaders for operator settings under ``config/`` (scripts-only I/O)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from conlanger.compile.models.config import CompilerConfig
from conlanger.ingest.models.mappings import (
    FeatureMapping,
    IpaMapping,
    ManualMapping,
    ParserConfig,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_ROOT = _REPO_ROOT / "config"

_DEFAULT_PARSER_CONFIG = _CONFIG_ROOT / "parser" / "parser_config.yml"
_DEFAULT_COMPILER_CONFIG = _CONFIG_ROOT / "compile" / "asca" / "compiler_config.yml"

_SUPPORTED_FEATURE_MAPPING_KINDS = frozenset(
    {"rename", "rename_invert", "rename_polarity", "bundle", "tone"}
)


def _load_yaml_list(path: Path) -> list[dict[str, Any]]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(loaded, list):
        raise TypeError("Data is not the expected type: list")
    return loaded


def _load_yaml_dict(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise TypeError("Data is not the expected type: dict")
    return loaded


def _load_manual_mappings(path: Path) -> list[ManualMapping]:
    if not path.is_file():
        return []
    raw = _load_yaml_list(path)
    seen: set[str] = set()
    out: list[ManualMapping] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        targets: list[str] = [str(target) for target in entry.get("targets", [])] or [
            str(entry.get("from", ""))
        ]
        for target in targets:
            if target in seen:
                raise ValueError(f"duplicate manual mapping target: {target!r}")
            seen.add(target)

            count = entry.get("count", None)
            comment = entry.get("comment", False)
            reason = str(entry.get("reason", "comment" if comment else ""))
            to_text = str(entry.get("to", ""))

            if not to_text and comment:
                to_text = f" ; {target.lstrip()}"

            out.append(
                ManualMapping(
                    from_text=target,
                    to_text=to_text,
                    reason=reason,
                    use_regex=bool(entry.get("use_regex", False)),
                    count=int(count) if count is not None else None,
                )
            )
    return out


def _load_ipa_mappings(path: Path) -> tuple[IpaMapping, ...]:
    if not path.is_file():
        return ()
    raw = _load_yaml_dict(path)
    out: list[IpaMapping] = []
    for index_feature, entry in raw.items():
        if isinstance(entry, str):
            out.append(IpaMapping(index_feature=str(index_feature), ipa_target=entry))
        elif isinstance(entry, dict):
            out.append(
                IpaMapping(
                    index_feature=str(index_feature),
                    ipa_target=str(entry.get("ipa_target", "")),
                    confidence=entry.get("confidence", None),
                    notes=str(entry.get("notes", "")),
                )
            )
    return tuple(out)


def _load_feature_mappings(path: Path) -> dict[str, FeatureMapping]:
    if not path.is_file():
        return {}
    raw = _load_yaml_dict(path)
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
    raw = _load_yaml_dict(path)
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
    raw = _load_yaml_dict(path)
    out: dict[str, str] = {}
    for grouping, entry in raw.items():
        if isinstance(entry, str):
            out[str(grouping)] = entry
        elif isinstance(entry, dict):
            out[str(grouping)] = str(entry.get("mapping", ""))
    return out


def _load_compiler_series(
    raw: dict[str, Any],
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    if not isinstance(raw, dict):
        return {}, {}
    series = raw.get("series_mappings", {})
    if not isinstance(series, dict):
        return {}, {}
    raw_global = series.get("global", {})
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

    raw = _load_yaml_dict(parser_yaml)

    manual_path = config_root / "manual_mappings.yml"
    ipa_path = config_root / "ipa_mappings.yml"
    feature_path = config_root / "feature_mappings.yml"
    corrections_path = config_root / "index_corrections.yml"

    return ParserConfig(
        manual_mappings=_load_manual_mappings(manual_path),
        ipa_mappings=_load_ipa_mappings(ipa_path),
        ipa_mappings_confidence=frozenset(raw.get("ipa_mappings_confidence", [])),
        feature_mappings=_load_feature_mappings(feature_path),
        corrections=_load_corrections(corrections_path),
        series_expansions=raw.get("series_expansions", {}),
        section_mappings_sections=raw.get("section_mappings", {}),
        skip_sections=raw.get("skip_sections", []),
        skip_rules=raw.get("skip_rules", []),
    )


def apply_compiler_config_cli_overrides(
    config: CompilerConfig,
    *,
    sample_sporadic: bool | None = None,
    sample_dialect: bool | None = None,
    sample_alternatives: bool | None = None,
    seed: int | None = None,
) -> CompilerConfig:
    """Apply CLI scalar overrides on top of a loaded ``CompilerConfig``."""
    updates: dict[str, Any] = {}
    if sample_sporadic is not None:
        updates["sample_sporadic"] = sample_sporadic
    if sample_dialect is not None:
        updates["sample_dialect"] = sample_dialect
    if sample_alternatives is not None:
        updates["sample_alternatives"] = sample_alternatives
    if seed is not None:
        updates["seed"] = seed
    if not updates:
        return config
    return config.model_copy(update=updates)


def compiler_config_for_compile(
    path: Path | None = None,
    *,
    sample_sporadic: bool | None = None,
    sample_dialect: bool | None = None,
    sample_alternatives: bool | None = None,
    seed: int | None = None,
) -> CompilerConfig:
    """Build ``CompilerConfig`` for ``compile_rules`` with optional CLI scalar overrides.

    When ``path`` is omitted, uses Pydantic class defaults only (no YAML load).
    """
    config = CompilerConfig() if path is None else load_compiler_config(path)
    return apply_compiler_config_cli_overrides(
        config,
        sample_sporadic=sample_sporadic,
        sample_dialect=sample_dialect,
        sample_alternatives=sample_alternatives,
        seed=seed,
    )


def load_compiler_config(path: Path | None = None) -> CompilerConfig:
    """Load ``CompilerConfig`` from ``config/compile/asca/`` YAML fragments.

    Scalar keys present in the compiler YAML override ``CompilerConfig`` class
    defaults; absent keys keep those defaults (not implicit ``false``).
    """
    config_root = (
        _CONFIG_ROOT / "compile" / "asca" if path is None else Path(path).parent
    )
    compiler_yaml = _DEFAULT_COMPILER_CONFIG if path is None else Path(path)

    raw = _load_yaml_dict(compiler_yaml)
    global_map, sections = _load_compiler_series(raw)
    group_path = config_root / "group_mappings.yml"

    payload: dict[str, Any] = {
        "group_mappings": _load_group_mappings(group_path),
        "series_mappings_global": global_map,
        "series_mappings_sections": sections,
    }
    for key in (
        "sample_sporadic",
        "sample_dialect",
        "sample_alternatives",
        "seed",
        "position_templates",
    ):
        if key in raw:
            payload[key] = raw[key]

    return CompilerConfig.model_validate(payload)
