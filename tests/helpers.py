"""Importable test helpers (also re-exported from ``conftest``)."""

from __future__ import annotations

from conlanger.tools.parsers import IndexDiachronicaParser
from conlanger.utils.file_io import load_default_ingest_tables

_CACHED_INGEST_TABLES = None


def default_index_parser(**overrides) -> IndexDiachronicaParser:
    """Build an ``IndexDiachronicaParser`` with package-default mapping tables.

    Tables are loaded once per process; pass keyword overrides to replace
    individual constructor arguments (e.g. ``parser_config=...``).
    """
    global _CACHED_INGEST_TABLES
    if _CACHED_INGEST_TABLES is None:
        _CACHED_INGEST_TABLES = load_default_ingest_tables()
    tables = _CACHED_INGEST_TABLES
    kwargs = {
        "series_mappings": tables.series_mappings,
        "manual_mappings": tables.manual_mappings,
        "parser_config": tables.parser_config,
        "feature_mappings": tables.feature_mappings,
        "ipa_mappings": tables.ipa_mappings,
    }
    kwargs.update(overrides)
    return IndexDiachronicaParser(**kwargs)
