"""Compile target resolution shared by compile_rules and inventory (tickets 158/161)."""

from __future__ import annotations

import random
from typing import Any

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
    targets: list[InventoryTarget] = []
    for step_index, part in enumerate(sound_change_parts):
        step_idx = step_index if multi_step else None
        if part.alternatives:
            for alt_idx, alternative in enumerate(part.alternatives):
                targets.append(
                    InventoryTarget(
                        alt_idx=alt_idx,
                        series=series_for_sound_change_rule(
                            section, rule_id, alternative
                        ),
                        field_rule=alternative,
                        step_idx=step_idx,
                    )
                )
            continue
        targets.append(
            InventoryTarget(
                series=series_for_sound_change_rule(section, rule_id, part),
                field_rule=part,
                step_idx=step_idx,
            )
        )
    return targets
