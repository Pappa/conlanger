"""Read/write helpers for the cleaned rule index YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def yaml_string_representer(dumper: yaml.Dumper, data: str) -> yaml.nodes.ScalarNode:
    style = None
    if "\n" in data:
        style = "|"
        data = "\n".join([line.strip() for line in data.splitlines()])
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


yaml.add_representer(str, yaml_string_representer, Dumper=yaml.SafeDumper)


def write_cleaned_index(doc: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            doc,
            stream=f,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
        )


def read_cleaned_index(path: Path) -> dict[str, Any]:
    """Load a cleaned index document written by ``write_cleaned_index``."""
    with path.open("r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    if not isinstance(loaded, dict):
        msg = f"expected mapping at root of {path}"
        raise TypeError(msg)
    return loaded
