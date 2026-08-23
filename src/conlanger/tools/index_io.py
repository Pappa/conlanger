"""Read/write helpers for the cleaned rule index YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class _LiteralStr(str):
    """Marker type for YAML literal-block emission."""


def _literal_str_representer(
    dumper: yaml.Dumper, data: _LiteralStr
) -> yaml.nodes.ScalarNode:
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


yaml.add_representer(_LiteralStr, _literal_str_representer)
yaml.add_representer(_LiteralStr, _literal_str_representer, Dumper=yaml.SafeDumper)


def _mark_raw_literal(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if key == "raw" and isinstance(value, str):
                out[key] = _LiteralStr(value)
            else:
                out[key] = _mark_raw_literal(value)
        return out
    if isinstance(obj, list):
        return [_mark_raw_literal(item) for item in obj]
    return obj


def dump_cleaned_index(doc: dict[str, Any]) -> str:
    """Serialize a cleaned index document; multi-line ``raw`` uses YAML ``|`` blocks."""
    return yaml.safe_dump(
        _mark_raw_literal(doc),
        allow_unicode=True,
        sort_keys=False,
    )


def write_cleaned_index(doc: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_cleaned_index(doc), encoding="utf-8")
