"""Stable inline mapping fixtures for tests (ticket 102).

Owned by tests only — not read from production ``config/`` paths.
"""

from __future__ import annotations

from conlanger.ingest.models.mappings import (
    CompilerConfig,
    FeatureMapping,
    ManualMapping,
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


def minimal_feature_mappings() -> dict[str, FeatureMapping]:
    rows = [
        ("voiced", "rename", "voice", "high"),
        ("sibilant", "rename", "strident", "high"),
        ("short", "rename_invert", "long", "high"),
        ("glottalized", "rename_polarity", "place", "high"),
        ("close-mid", "bundle", "-hi,-lo,+tense", "high"),
        ("open-mid", "bundle", "-hi,-lo,-tense", "high"),
        ("open", "rename", "lo", "high"),
        ("closed", "rename", "hi", "high"),
        ("dental", "bundle", "+cor,+anterior,+dist", "high"),
        ("alveolar", "bundle", "+cor,+anterior,-dist", "high"),
        ("palatal", "bundle", "+cor,+dist", "high"),
        ("velar", "bundle", "-fr,+bk,+hi,-lo", "high"),
        ("uvular", "bundle", "-fr,+bk,-hi,-lo", "high"),
        ("high tone", "tone", "5", "high"),
        ("low tone", "tone", "1", "high"),
        ("falling tone", "tone", "51", "high"),
        ("low falling tone", "tone", "21", "high"),
        ("high rising tone", "tone", "35", "high"),
    ]
    return {
        index_feature: FeatureMapping(
            index_feature=index_feature,
            mapping_kind=mapping_kind,
            asca_target=asca_target,
            confidence=confidence,
        )
        for index_feature, mapping_kind, asca_target, confidence in rows
    }


def minimal_manual_mappings() -> list[ManualMapping]:
    return [
        ManualMapping(from_text="ATR", to_text="atr", reason="Lowercase feature name"),
    ]


def minimal_ipa_mappings() -> dict[str, str]:
    """Resolved IPA dict for tests that still pass explicit mapping overrides."""
    return {
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
    }
