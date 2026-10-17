"""Compiled rules YAML v1 (`diagnostics/compile/asca_rules.yml`, tickets 159/161)."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Protocol

import yaml

import conlanger.tools.index_io as _index_io  # noqa: F401 — registers YAML string representer
from conlanger.compile.models.rules import DiachronicSeries, SoundChangeRule
from conlanger.ingest.models.mappings import CompilerConfig
from conlanger.tools.compiled_target_serde import (
    deserialize_series,
    inventory_target_from_yaml,
    inventory_target_to_yaml,
    serialize_series,
    sound_change_rule_from_series,
)
from conlanger.tools.inventory_targets import (
    INVENTORY_COMPILE_RNG_SEED,
    InventoryTarget,
    mini_section,
)

COMPILED_RULES_YAML_NAME = "asca_rules.yml"
COMPILED_RULES_SCHEMA_VERSION = 1


class _CompileRuleBundle(Protocol):
    section: dict[str, Any]
    rule: dict[str, Any]
    rule_id: str
    targets: list[InventoryTarget]


def _skipped_rule_line(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_id: str,
    *,
    compiler_config: CompilerConfig | None,
) -> str:
    if rule.get("status") == "skipped":
        return f"#\t{rule.get('raw', '')}"

    mini = mini_section(section, rule, rule_id)
    series = DiachronicSeries(
        mini,
        compiler_config=compiler_config,
        rng=random.Random(INVENTORY_COMPILE_RNG_SEED),
    )
    for part in series.parts:
        if isinstance(part, SoundChangeRule):
            return str(part).strip()
    return f"#\t{rule.get('raw', '')}"


def compiled_rule_entry(
    rule: dict[str, Any],
    *,
    rule_id: str,
    source: str,
    targets: list[InventoryTarget],
    section: dict[str, Any],
    compiler_config: CompilerConfig | None = None,
) -> dict[str, Any]:
    """Build one ``rules`` entry for ``asca_rules.yml`` v1."""
    entry: dict[str, Any] = {"rule_id": rule_id, "source": source}

    if rule.get("status") == "skipped":
        entry["status"] = "skipped"
        entry["rule"] = _skipped_rule_line(
            section, rule, rule_id, compiler_config=compiler_config
        )
        return entry

    if not targets:
        entry["compile_error"] = "no compile targets"
        return entry

    target = targets[0]
    if target.format_error is not None:
        text = target.format_error
        prefix = "format_error: "
        entry["compile_error"] = text.removeprefix(prefix)
        return entry

    if target.field_rule is not None and target.field_rule.sporadic_skipped:
        entry["status"] = "compile_skipped"
        entry["rule"] = str(target.field_rule).strip()
        return entry

    compiled_targets: list[dict[str, Any]] = []
    for compile_target in targets:
        if compile_target.format_error is not None:
            continue
        if compile_target.series is None or compile_target.field_rule is None:
            continue
        compiled_targets.append(inventory_target_to_yaml(compile_target))

    if not compiled_targets:
        entry["compile_error"] = "no compiled targets"
        return entry

    entry["targets"] = compiled_targets
    return entry


def build_asca_rules_document(
    bundles: list[_CompileRuleBundle],
    *,
    compiler_config: CompilerConfig | None = None,
) -> dict[str, Any]:
    """Assemble v1 ``asca_rules.yml`` from compile targets (not validation rows)."""
    sections_out: list[dict[str, Any]] = []
    current_key: tuple[str, str] | None = None
    current_section: dict[str, Any] | None = None
    rules_out: list[dict[str, Any]] = []

    for bundle in bundles:
        section = bundle.section
        if section.get("status") == "skipped":
            continue

        section_key = (
            str(section.get("index", "")),
            str(section.get("section", "")),
        )
        if section_key != current_key:
            if current_section is not None:
                sections_out.append({**current_section, "rules": rules_out})
            current_key = section_key
            current_section = {
                "section": section.get("section"),
                "index": str(section.get("index", "")),
            }
            rules_out = []

        source = str(bundle.rule.get("source", ""))
        rules_out.append(
            compiled_rule_entry(
                bundle.rule,
                rule_id=bundle.rule_id,
                source=source,
                targets=bundle.targets,
                section=section,
                compiler_config=compiler_config,
            )
        )

    if current_section is not None:
        sections_out.append({**current_section, "rules": rules_out})

    return {"schema_version": COMPILED_RULES_SCHEMA_VERSION, "sections": sections_out}


def read_compiled_rules_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        msg = f"compiled rules YAML must be a mapping: {path}"
        raise TypeError(msg)
    version = document.get("schema_version")
    if version != COMPILED_RULES_SCHEMA_VERSION:
        msg = (
            f"unsupported compiled rules schema_version {version!r} "
            f"(expected {COMPILED_RULES_SCHEMA_VERSION})"
        )
        raise ValueError(msg)
    return document


def write_compiled_rules_yaml(document: dict[str, Any], path: Path) -> None:
    """Write ``asca_rules.yml`` using the same string representer as the index."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            document,
            stream=handle,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
        )


__all__ = [
    "COMPILED_RULES_SCHEMA_VERSION",
    "COMPILED_RULES_YAML_NAME",
    "build_asca_rules_document",
    "compiled_rule_entry",
    "deserialize_series",
    "inventory_target_from_yaml",
    "inventory_target_to_yaml",
    "read_compiled_rules_yaml",
    "serialize_series",
    "sound_change_rule_from_series",
    "write_compiled_rules_yaml",
]
