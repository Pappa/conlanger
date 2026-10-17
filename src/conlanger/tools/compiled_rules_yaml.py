"""Compile diagnostic YAML (`diagnostics/compile/asca_rules.yml`, ticket 159)."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import yaml

import conlanger.tools.index_io as _index_io  # noqa: F401 — registers YAML string representer
from conlanger.compile.models.rules import DiachronicSeries, SoundChangeRule
from conlanger.ingest.models.mappings import CompilerConfig
from conlanger.tools.index_inventory import (
    INVENTORY_COMPILE_RNG_SEED,
    OK_SKIPPED,
    OK_TRUE,
    RULE_SKIPPED_FAILURE_CLASS,
    IndexRuleInventoryBundle,
    ValidationRow,
    _mini_section,
)

COMPILED_RULES_YAML_NAME = "asca_rules.yml"


def _row_valid(row: ValidationRow) -> bool:
    return row.ok == OK_TRUE


def _compile_error_message(rows: list[ValidationRow]) -> str:
    if rows and rows[0].description:
        text = rows[0].description
        prefix = "format_error: "
        if text.startswith(prefix):
            return text[len(prefix) :]
        return text
    return "compile failed"


def _skipped_rule_line(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_id: str,
    *,
    compiler_config: CompilerConfig | None,
) -> str:
    if rule.get("status") == "skipped":
        return f"#\t{rule.get('raw', '')}"

    mini = _mini_section(section, rule, rule_id)
    series = DiachronicSeries(
        mini,
        compiler_config=compiler_config,
        rng=random.Random(INVENTORY_COMPILE_RNG_SEED),
    )
    for part in series.parts:
        if isinstance(part, SoundChangeRule):
            return str(part).strip()
    return f"#\t{rule.get('raw', '')}"


def _payload_from_validation_rows(rows: list[ValidationRow]) -> dict[str, Any]:
    if not rows:
        return {"valid": False, "compile_error": "no validation rows"}

    if len(rows) == 1 and rows[0].alt_idx is None and rows[0].step_idx is None:
        return {"valid": _row_valid(rows[0]), "rule": rows[0].rule}

    has_steps = any(row.step_idx is not None for row in rows)
    has_alts = any(row.alt_idx is not None for row in rows)

    if has_steps and not has_alts:
        ordered = sorted(rows, key=lambda row: row.step_idx or 0)
        steps = [{"rule": row.rule, "valid": _row_valid(row)} for row in ordered]
        return {"valid": all(step["valid"] for step in steps), "steps": steps}

    if has_alts:
        ordered = sorted(
            rows,
            key=lambda row: (row.step_idx or 0, row.alt_idx or 0),
        )
        alternatives = [{"rule": row.rule, "valid": _row_valid(row)} for row in ordered]
        return {
            "valid": all(alt["valid"] for alt in alternatives),
            "alternatives": alternatives,
        }

    branches = [{"rule": row.rule, "valid": _row_valid(row)} for row in rows]
    return {
        "valid": all(branch["valid"] for branch in branches),
        "steps": branches,
    }


def compiled_rule_entry_from_rows(
    rule: dict[str, Any],
    rows: list[ValidationRow],
    *,
    section: dict[str, Any],
    rule_id: str,
    compiler_config: CompilerConfig | None = None,
    sporadic_skipped_line: str | None = None,
    compile_error: str | None = None,
) -> dict[str, Any]:
    """Build one ``rules`` entry for ``asca_rules.yml``."""
    entry: dict[str, Any] = {"rule_id": rule_id}

    if rule.get("status") == "skipped":
        entry["status"] = "skipped"
        entry["rule"] = _skipped_rule_line(
            section, rule, rule_id, compiler_config=compiler_config
        )
        return entry

    if sporadic_skipped_line is not None:
        entry["status"] = "compile_skipped"
        entry["rule"] = sporadic_skipped_line
        return entry

    if compile_error is not None:
        entry["valid"] = False
        text = compile_error
        prefix = "format_error: "
        entry["compile_error"] = text.removeprefix(prefix)
        return entry

    if (
        len(rows) == 1
        and rows[0].ok == OK_SKIPPED
        and rows[0].failure_class == RULE_SKIPPED_FAILURE_CLASS
    ):
        entry["status"] = "skipped"
        entry["rule"] = _skipped_rule_line(
            section, rule, rule_id, compiler_config=compiler_config
        )
        return entry

    if rows and rows[0].failure_class == "format_error":
        entry["valid"] = False
        entry["compile_error"] = _compile_error_message(rows)
        return entry

    entry.update(_payload_from_validation_rows(rows))
    return entry


def build_asca_rules_document(
    bundles: list[IndexRuleInventoryBundle],
    *,
    compiler_config: CompilerConfig | None = None,
) -> dict[str, Any]:
    """Assemble the top-level ``sections`` document for ``asca_rules.yml``."""
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

        sporadic_line: str | None = None
        target_error: str | None = None
        if bundle.targets:
            target = bundle.targets[0]
            if target.format_error is not None:
                target_error = target.format_error
            elif target.field_rule is not None and target.field_rule.sporadic_skipped:
                sporadic_line = str(target.field_rule).strip()

        rules_out.append(
            compiled_rule_entry_from_rows(
                bundle.rule,
                bundle.rows,
                section=section,
                rule_id=bundle.rule_id,
                compiler_config=compiler_config,
                sporadic_skipped_line=sporadic_line,
                compile_error=target_error,
            )
        )

    if current_section is not None:
        sections_out.append({**current_section, "rules": rules_out})

    return {"sections": sections_out}


def bundles_for_row_prefix(
    bundles: list[IndexRuleInventoryBundle],
    rows: list[ValidationRow],
) -> list[IndexRuleInventoryBundle]:
    """Return bundles whose rows are a prefix of ``rows`` (for ``--limit``)."""
    if not rows:
        return []
    remaining = list(rows)
    trimmed: list[IndexRuleInventoryBundle] = []
    for bundle in bundles:
        bundle_rows = bundle.rows
        if len(bundle_rows) > len(remaining):
            trimmed.append(
                IndexRuleInventoryBundle(
                    section=bundle.section,
                    rule=bundle.rule,
                    rule_id=bundle.rule_id,
                    rows=remaining,
                    targets=bundle.targets[: len(remaining)],
                )
            )
            break
        trimmed.append(bundle)
        remaining = remaining[len(bundle_rows) :]
        if not remaining:
            break
    return trimmed


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
