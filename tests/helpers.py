"""Importable test helpers (also re-exported from ``conftest``)."""

from __future__ import annotations

from pathlib import Path

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


_INDEX_DIACHRONICA_HTML = """\
<!doctype html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
<section id="{section_id}">
{section_body}
</section>
</body></html>
"""


def write_tmp_index_html(
    path: Path,
    *,
    section_id: str,
    section_body: str,
) -> None:
    path.write_text(
        _INDEX_DIACHRONICA_HTML.format(
            section_id=section_id,
            section_body=section_body,
        ),
        encoding="utf-8",
    )
