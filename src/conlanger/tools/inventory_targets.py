"""Compile target resolution shared by compile_rules and inventory (tickets 158/161)."""

from __future__ import annotations

import random
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from conlanger.compile.models.config import CompilerConfig
from conlanger.compile.models.rules import DiachronicSeries, RuleTitle, SoundChangeRule

# Fixed seed for inventory compile (optional-output / sporadic RNG); ticket 158.
INVENTORY_COMPILE_RNG_SEED = 0


class InventoryTarget(BaseModel):
    """One compiled ASCA validation target (optional alt/step indices)."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    alt_idx: int | None = None
    series: DiachronicSeries | None = None
    field_rule: SoundChangeRule | None = None
    step_idx: int | None = None
    format_error: str | None = None
    asca_rule: str | None = None


# Back-compat alias for internal and test imports.
_InventoryTarget = InventoryTarget


def mini_section(
    section: dict[str, Any], rule: dict[str, Any], rule_id: str
) -> dict[str, Any]:
    return {
        "index": section.get("index", ""),
        "section": f"{section.get('section', '')}#{rule_id}",
        "rules": [rule],
    }


# Back-compat alias for tests and internal callers.
_mini_section = mini_section


def series_for_sound_change_rule(
    section: dict[str, Any],
    rule_id: str,
    sound_change_rule: SoundChangeRule,
) -> DiachronicSeries:
    """Build a standalone series for one compiled inventory validation target."""
    section_index = str(section.get("index", ""))
    section_name = f"{section.get('section', '')}#{rule_id}"
    return DiachronicSeries.from_parts(
        [
            RuleTitle(section_index, section_name),
            sound_change_rule,
        ]
    )


_series_for_sound_change_rule = series_for_sound_change_rule


def series_for_alternative(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_id: str,
    alternative: SoundChangeRule,
    compiler_config: CompilerConfig | None,
) -> DiachronicSeries:
    """Build a standalone series for one already-compiled alternative."""
    del rule, compiler_config
    return series_for_sound_change_rule(section, rule_id, alternative)


_series_for_alternative = series_for_alternative


def _compiled_field_segment(
    rule: SoundChangeRule, field: Literal["input", "output"]
) -> str:
    part = rule.input if field == "input" else rule.output
    return (part.compiled or part.raw or "").strip()


def _part_choices(part: SoundChangeRule) -> list[SoundChangeRule]:
    return list(part.alternatives) if part.alternatives else [part]


def _enumerate_composed_chain_paths(
    parts: list[SoundChangeRule],
) -> list[list[SoundChangeRule]]:
    """Enumerate valid stage sequences where each step's input matches prior output."""
    if not parts:
        return []
    paths: list[list[SoundChangeRule]] = [
        [choice] for choice in _part_choices(parts[0])
    ]
    for part in parts[1:]:
        extended: list[list[SoundChangeRule]] = []
        for path in paths:
            prior_output = _compiled_field_segment(path[-1], "output")
            for choice in _part_choices(part):
                if _compiled_field_segment(choice, "input") == prior_output:
                    extended.append(path + [choice])
        paths = extended
    return paths


def resolve_inventory_targets(
    section: dict[str, Any],
    rule: dict[str, Any],
    rule_id: str,
    *,
    compiler_config: CompilerConfig | None = None,
) -> list[InventoryTarget]:
    """Compile paths shared by whole-rule inventory and field isolation."""
    mini = mini_section(section, rule, rule_id)
    try:
        scr = DiachronicSeries(
            mini,
            compiler_config=compiler_config,
            rng=random.Random(INVENTORY_COMPILE_RNG_SEED),
        )
    except (KeyError, ValueError) as exc:
        return [
            InventoryTarget(format_error=f"format_error: {exc}"),
        ]

    sound_change_parts = [
        part for part in scr._parts if isinstance(part, SoundChangeRule)
    ]
    if not sound_change_parts:
        return [
            InventoryTarget(
                format_error="format_error: no compile steps from stages",
            )
        ]

    multi_step = len(sound_change_parts) > 1
    composed_paths = _enumerate_composed_chain_paths(sound_change_parts)
    if not composed_paths:
        return [
            InventoryTarget(
                format_error="format_error: no composed chain paths from stages",
            )
        ]

    path_count = len(composed_paths)
    targets: list[InventoryTarget] = []
    step_count = len(composed_paths[0])
    for step_index in range(step_count):
        step_idx = step_index if multi_step else None
        for path_idx, path in enumerate(composed_paths):
            step_rule = path[step_index]
            alt_idx = path_idx if path_count > 1 else None
            targets.append(
                InventoryTarget(
                    alt_idx=alt_idx,
                    series=series_for_sound_change_rule(section, rule_id, step_rule),
                    field_rule=step_rule,
                    step_idx=step_idx,
                )
            )
    return targets
