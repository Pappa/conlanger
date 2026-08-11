"""Applier-neutral compile container for one sound-change section (ticket 06)."""

from __future__ import annotations

from typing import Any

from conlanger.tools.rules import DiachronicSeries


class PhonologicalRuleSet:
    """One sound-change section ready for applier compilation.

    Holds corpus rules unchanged; ASCA-specific transforms (e.g. Index class
    letters from ``group_mappings.csv``) run in ``DiachronicSeries`` / ``RuleChange``.
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
    ) -> DiachronicSeries:
        return DiachronicSeries(
            self._section,
            self._format,
            group_mappings=group_mappings,
        )
