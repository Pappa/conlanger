"""Stable inline mapping fixtures for tests (ticket 102).

Owned by tests only — not read from production ``config/`` paths.
"""

from __future__ import annotations

from conlanger.utils.mappings import (
    CompilerConfig,
    FeatureMapping,
    IpaMapping,
    ManualMapping,
    ParserConfig,
)

MINIMAL_GROUP_MAPPINGS: dict[str, str] = {
    "A": "O:[+delrel]",
    "B": "V:[+back]",
    "D": "P:[+voice]",
    "E": "V:[+front]",
    "H": "[-place]",
    "J": "{L,G}",
    "K": "C:[-front,+back,+hi,-lo]",
    "Ḱ": "C:[+front,+hi,-lo]",
    "P": "C:[+labial]",
    "Q": "{C:[-front,+back,-hi,-lo],[+click]}",
    "R": "[+son,-syll]",
    "S": "P",
    "T": "P:[-voice]",
    "U": "%",
    "W": "G",
    "Z": "[+cont]",
}


def minimal_compiler_config() -> CompilerConfig:
    return CompilerConfig(
        group_mappings=MINIMAL_GROUP_MAPPINGS,
        series_mappings_sections={
            "6": {"s₁": "F", "s₂": "F", "s₃": "F"},
        },
    )


def minimal_parser_config() -> ParserConfig:
    ipa_rows = tuple(
        IpaMapping(index_feature=char, ipa_target=target, confidence="high")
        for char, target in {
            "Š": "ʃ",
            "ḱ": "kʲ",
            "è": "ɛ",
            "é": "e",
            "ı": "j",
            "ṽ": "v\u0303",
            "Ṽ": "v\u0303",
            "û": "u",
            "î": "i",
            "oı̃": "oj\u0303",
            "iı̃": "ij\u0303",
            "eı̃": "ej\u0303",
            "ɛ̃": "ɛ\u0303",
            "wɛ̃": "wɛ\u0303",
        }.items()
    )
    return ParserConfig(
        manual_mappings=minimal_manual_mappings(),
        ipa_mappings=ipa_rows,
        ipa_mappings_confidence=frozenset({"high", "medium"}),
        feature_mappings=minimal_feature_mappings(),
        corrections={},
        series_expansions={
            "sₓ": ("s₁", "s₂", "s₃"),
            "Hₓ": ("h₁", "h₂", "h₃"),
        },
        section_mappings_sections={
            "10.1": {"*D": "D", "*R": "R", "*T": "T"},
        },
    )


def minimal_feature_mappings() -> dict[str, FeatureMapping]:
    rows = [
        FeatureMapping("voiced", "rename", "voice", confidence="high"),
        FeatureMapping("sibilant", "rename", "strident", confidence="high"),
        FeatureMapping("short", "rename_invert", "long", confidence="high"),
        FeatureMapping("glottalized", "rename_polarity", "place", confidence="high"),
        FeatureMapping("close-mid", "bundle", "-hi,-lo,+tense", confidence="high"),
        FeatureMapping("open-mid", "bundle", "-hi,-lo,-tense", confidence="high"),
        FeatureMapping("open", "rename", "lo", confidence="high"),
        FeatureMapping("closed", "rename", "hi", confidence="high"),
        FeatureMapping("dental", "bundle", "+cor,+anterior,+dist", confidence="high"),
        FeatureMapping("alveolar", "bundle", "+cor,+anterior,-dist", confidence="high"),
        FeatureMapping("palatal", "bundle", "+cor,+dist", confidence="high"),
        FeatureMapping("velar", "bundle", "-fr,+bk,+hi,-lo", confidence="high"),
        FeatureMapping("uvular", "bundle", "-fr,+bk,-hi,-lo", confidence="high"),
        FeatureMapping("high tone", "tone", "5", confidence="high"),
        FeatureMapping("low tone", "tone", "1", confidence="high"),
        FeatureMapping("falling tone", "tone", "51", confidence="high"),
        FeatureMapping("low falling tone", "tone", "21", confidence="high"),
        FeatureMapping("high rising tone", "tone", "35", confidence="high"),
    ]
    return {row.index_feature: row for row in rows}


def minimal_manual_mappings() -> list[ManualMapping]:
    return [
        ManualMapping(from_text="ATR", to_text="atr", reason="Lowercase feature name"),
    ]


def minimal_ipa_mappings() -> dict[str, str]:
    """Resolved IPA dict for tests that still pass explicit mapping overrides."""
    return minimal_parser_config().resolved_ipa_mappings()
