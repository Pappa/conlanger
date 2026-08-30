"""Index→ASCA mapping dataclasses and in-memory apply/normalize helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from conlanger.utils.series import section_index_prefixes

_CORPUS_CONTEXT_FIELD_KEYS = ("env", "exception")


@dataclass(frozen=True)
class GroupMapping:
    grouping: str
    mapping: str
    comment: str = ""


@dataclass(frozen=True)
class IpaMapping:
    index_feature: str
    ipa_target: str
    confidence: str | None = None
    notes: str = ""


@dataclass(frozen=True)
class ManualMapping:
    """One owner-authored substring rewrite from ``manual_mappings``."""

    from_text: str
    to_text: str
    reason: str = ""
    use_regex: bool = False


@dataclass(frozen=True)
class ManualMappingHit:
    """A single substring replace performed by ``apply_manual_mappings``."""

    from_text: str
    to_text: str


@dataclass(frozen=True)
class ManualMappingMatch:
    """Debug row for a manual mapping applied during ingest."""

    section_index: str
    section_name: str
    rule_id: str
    source: str
    manual_mapping: str


@dataclass(frozen=True)
class FeatureMapping:
    index_feature: str
    mapping_kind: str
    asca_target: str
    host: str = ""
    confidence: str = ""
    notes: str = ""


class ParserConfig(BaseModel):
    """Fat parse-time config: mapping tables plus runtime parser settings."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    manual_mappings: list[ManualMapping] = Field(default_factory=list)
    ipa_mappings: tuple[IpaMapping, ...] = Field(default_factory=tuple)
    ipa_mappings_confidence: frozenset[str] | None = None
    feature_mappings: dict[str, FeatureMapping] = Field(default_factory=dict)
    corrections: dict[str, str] = Field(default_factory=dict)
    series_expansions: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    section_mappings_sections: dict[str, dict[str, str]] = Field(default_factory=dict)
    skip_section_ids: frozenset[str] = Field(default_factory=frozenset)
    skip_rule_ids: frozenset[str] = Field(default_factory=frozenset)
    skip_rule_comments: dict[str, str] = Field(default_factory=dict)

    def resolved_ipa_mappings(self) -> dict[str, str]:
        """Return IPA char → target map, optionally filtered by confidence."""
        if self.ipa_mappings_confidence is None:
            return {
                row.index_feature: row.ipa_target
                for row in self.ipa_mappings
                if row.ipa_target
            }
        return {
            row.index_feature: row.ipa_target
            for row in self.ipa_mappings
            if row.confidence in self.ipa_mappings_confidence and row.ipa_target
        }

    def resolved_section_mappings(self, section_index: str) -> dict[str, str]:
        """Merge section rows via longest-prefix ancestry; child overrides parent."""
        result: dict[str, str] = {}
        if not section_index:
            return result
        for prefix in section_index_prefixes(section_index):
            section_map = self.section_mappings_sections.get(prefix)
            if section_map:
                result.update(section_map)
        return result


class CompilerConfig(BaseModel):
    """Fat compile-time config: group mappings plus series token maps."""

    model_config = ConfigDict(frozen=True)

    group_mappings: dict[str, str] = Field(default_factory=dict)
    series_mappings_global: dict[str, str] = Field(default_factory=dict)
    series_mappings_sections: dict[str, dict[str, str]] = Field(default_factory=dict)

    def resolved_series_mappings(self, section_index: str) -> dict[str, str]:
        """Global token map with longest-prefix section rows overlaid."""
        result = dict(self.series_mappings_global)
        if not section_index:
            return result
        for prefix in section_index_prefixes(section_index):
            section_map = self.series_mappings_sections.get(prefix)
            if section_map:
                result.update(section_map)
        return result

    def lookup_series_mapping(self, section_index: str, token: str) -> str | None:
        """Return the target for ``token`` via section longest-prefix, else ``global``."""
        return self.resolved_series_mappings(section_index).get(token)


def normalize_feature_matrices_in_field(
    text: str,
    mappings: dict[str, FeatureMapping],
) -> str:
    """Replace Index matrix feature names inside ``[...]`` with ASCA targets."""
    if not text or not mappings:
        return text
    names = sorted(mappings.keys(), key=len, reverse=True)
    feature_re = re.compile(
        r"([+-])\s*(" + "|".join(re.escape(name) for name in names) + r")(?![a-zA-Z])"
    )

    def replace_polarity_and_name(match: re.Match[str]) -> str:
        polarity, index_name = match.group(1), match.group(2)
        mapping = mappings[index_name]
        if mapping.mapping_kind == "bundle":
            return mapping.asca_target
        if mapping.mapping_kind == "tone":
            # ASCA tone is `[tone: N]` only — never ± (ticket 62).
            if polarity != "+":
                return match.group(0)
            return f"tone: {mapping.asca_target}"
        if mapping.mapping_kind == "rename":
            return f"{polarity}{mapping.asca_target}"
        if mapping.mapping_kind in ("rename_invert", "rename_polarity"):
            flipped = "-" if polarity == "+" else "+"
            return f"{flipped}{mapping.asca_target}"
        return match.group(0)

    def replace_bracket_inner(match: re.Match[str]) -> str:
        inner = feature_re.sub(replace_polarity_and_name, match.group(1))
        return f"[{inner}]"

    return re.sub(r"\[([^\]]*)\]", replace_bracket_inner, text)


def apply_feature_mappings(
    parts: dict[str, str],
    mappings: dict[str, FeatureMapping],
) -> dict[str, str]:
    """Normalize Index feature matrix names in rule fields; ``raw`` unchanged upstream."""
    if not mappings:
        return parts
    result = dict(parts)
    stages = result.get("stages")
    if stages is not None:
        result["stages"] = [
            normalize_feature_matrices_in_field(stage, mappings) for stage in stages
        ]
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key in result:
            result[key] = normalize_feature_matrices_in_field(result[key], mappings)
    return result


def normalize_ipa_in_field(text: str, mappings: dict[str, str]) -> str:
    """Replace Index IPA characters in one rule field with ASCA targets."""
    if not text or not mappings:
        return text
    for source in sorted(mappings.keys(), key=len, reverse=True):
        text = text.replace(source, mappings[source])
    return text


def apply_ipa_mappings(
    parts: dict[str, str],
    mappings: dict[str, str],
) -> dict[str, str]:
    """Normalize Index IPA characters in rule fields; ``raw`` unchanged upstream."""
    if not mappings:
        return parts
    result = dict(parts)
    stages = result.get("stages")
    if stages is not None:
        result["stages"] = [normalize_ipa_in_field(stage, mappings) for stage in stages]
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key in result:
            result[key] = normalize_ipa_in_field(result[key], mappings)
    return result


def apply_section_mappings(
    text: str,
    section_index: str,
    config: ParserConfig,
) -> str:
    """Replace section-scoped tokens on the working line (``raw`` unchanged upstream)."""
    if not text or not section_index:
        return text
    mapping = config.resolved_section_mappings(section_index)
    if not mapping:
        return text
    ordered = sorted(mapping.items(), key=lambda pair: len(pair[0]), reverse=True)
    working = text
    for from_text, to_text in ordered:
        if from_text and from_text in working:
            working = working.replace(from_text, to_text)
    return working


def apply_manual_mappings(
    text: str,
    mappings: list[ManualMapping],
) -> tuple[str, list[ManualMappingHit]]:
    """Replace ``from`` substrings with ``to`` (all occurrences).

    Mappings are applied longest-``from`` first so a shorter pattern cannot steal
    a longer match when both would apply. Relative order among equal-length
    ``from`` keys follows list order (stable sort).
    """
    if not text or not mappings:
        return text, []
    ordered = sorted(mappings, key=lambda row: len(row.from_text), reverse=True)
    working = text
    hits: list[ManualMappingHit] = []
    for row in ordered:
        if row.from_text and row.from_text in working:
            working = working.replace(row.from_text, row.to_text)
            hits.append(ManualMappingHit(from_text=row.from_text, to_text=row.to_text))
    return working, hits
