"""Applier-neutral compile container for one sound-change section (ticket 06)."""

from __future__ import annotations

from typing import Any

from conlanger.tools.rules import SoundChangeRuleSet


class PhonologicalRuleSet:
    """One sound-change section ready for applier compilation.

    Holds corpus rules unchanged; ASCA-specific transforms (e.g. Index class
    letters from ``group_mappings.csv``) run in ``SoundChangeRuleSet`` / ``RuleChange``.
    """

    def __init__(self, section: dict[str, Any], *, format: str = "asca"):
        self._section = section
        self._format = format

    @property
    def section(self) -> dict[str, Any]:
        return self._section

    def to_sound_change_ruleset(
        self,
        *,
        group_mappings: dict[str, str] | None = None,
    ) -> SoundChangeRuleSet:
        return SoundChangeRuleSet(
            self._section,
            self._format,
            group_mappings=group_mappings,
        )
