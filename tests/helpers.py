"""Importable test helpers (also re-exported from ``conftest``)."""

from __future__ import annotations

from conlanger.tools.ingest import IndexDiachronicaParser
from tests.fixtures.minimal_mappings import minimal_parser_config


def default_index_parser(**overrides) -> IndexDiachronicaParser:
    """Build an ``IndexDiachronicaParser`` with minimal inline mapping fixtures.

    Pass keyword overrides to replace the ``ParserConfig`` (e.g. ``parser_config=...``).
    """
    config = overrides.pop("parser_config", minimal_parser_config())
    if overrides:
        config = config.model_copy(update=overrides)
    return IndexDiachronicaParser(config)
