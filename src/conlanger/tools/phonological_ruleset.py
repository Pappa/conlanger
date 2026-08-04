"""Compile applier-neutral corpus rules for ASCA validation (ticket 06 follow-on)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from conlanger.tools.parsers import GroupMapping, load_group_mappings
from conlanger.tools.rules import SoundChangeRuleSet

COMPILED_RULE_FIELDS = ("input", "output", "env", "exception")

_GROUPING_PREC = r"(?:^|(?<=[\{\[\s/,>_A-Z#$%|!\(-]))"
_GROUPING_FOLLOW = r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z])"


def group_mappings_dict(
    mappings: list[GroupMapping] | None = None,
    *,
    path: Path | None = None,
) -> dict[str, str]:
    """Build a grouping→ASCA mapping dict from CSV rows."""
    rows = mappings if mappings is not None else load_group_mappings(path)
    return {row.grouping: row.mapping for row in rows}


def apply_group_mappings_to_string(text: str, mappings: dict[str, str]) -> str:
    """Expand Index class letters to ASCA tokens in one rule-string field."""
    if not text or not mappings:
        return text
    keys = sorted(mappings.keys(), key=len, reverse=True)
    alt = "|".join(re.escape(key) for key in keys)
    regex = re.compile(rf"{_GROUPING_PREC}(?:{alt}){_GROUPING_FOLLOW}")
    return regex.sub(lambda match: mappings[match.group(0)], text)


def compile_corpus_rule(
    rule: dict[str, Any],
    mappings: dict[str, str],
) -> dict[str, Any]:
    """Return a corpus rule dict with compiled input/output/env/exception fields."""
    compiled = dict(rule)
    for field in COMPILED_RULE_FIELDS:
        value = compiled.get(field)
        if value:
            compiled[field] = apply_group_mappings_to_string(str(value), mappings)
    return compiled


class PhonologicalRuleSet:
    """Runtime compile container for one sound-change section."""

    def __init__(
        self,
        section: dict[str, Any],
        *,
        group_mappings: dict[str, str] | None = None,
        mappings_path: Path | None = None,
        format: str = "asca",
    ):
        self._section = section
        self._group_mappings = (
            group_mappings
            if group_mappings is not None
            else group_mappings_dict(path=mappings_path)
        )
        self._format = format

    @property
    def group_mappings(self) -> dict[str, str]:
        return self._group_mappings

    def compile_rule(self, rule: dict[str, Any]) -> dict[str, Any]:
        return compile_corpus_rule(rule, self._group_mappings)

    def compiled_section(self) -> dict[str, Any]:
        section = dict(self._section)
        rules = section.get("rules")
        if rules:
            section["rules"] = [self.compile_rule(rule) for rule in rules]
        return section

    def to_sound_change_ruleset(self) -> SoundChangeRuleSet:
        return SoundChangeRuleSet(self.compiled_section(), self._format)
