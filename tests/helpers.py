"""Importable test helpers (also re-exported from ``conftest``)."""

from __future__ import annotations

from conlanger.tools.ingest import IndexDiachronicaParser
from tests.fixtures.minimal_mappings import (
    minimal_feature_mappings,
    minimal_ipa_mappings,
    minimal_manual_mappings,
    minimal_parser_config,
)


def default_index_parser(**overrides) -> IndexDiachronicaParser:
    """Build an ``IndexDiachronicaParser`` with minimal inline mapping fixtures.

    Pass keyword overrides to replace individual constructor arguments
    (e.g. ``parser_config=...``, ``ipa_mappings=...``).
    """
    kwargs = {
        "manual_mappings": minimal_manual_mappings(),
        "parser_config": minimal_parser_config(),
        "feature_mappings": minimal_feature_mappings(),
        "ipa_mappings": minimal_ipa_mappings(),
        "corrections": {},
    }
    kwargs.update(overrides)
    return IndexDiachronicaParser(**kwargs)
