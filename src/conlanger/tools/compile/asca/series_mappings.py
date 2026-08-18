"""Compile-time correspondence-series index → segment expansion."""

from __future__ import annotations

from conlanger.utils.mappings import CompilerConfig


def apply_compiler_series_mappings(
    text: str,
    *,
    section_index: str,
    compiler_config: CompilerConfig,
) -> str:
    """Replace mapped correspondence-series indices in a joined rule string."""
    mapping = compiler_config.resolved_series_mappings(section_index)
    if not text or not mapping:
        return text
    result = text
    for token in sorted(mapping, key=len, reverse=True):
        if token:
            result = result.replace(token, mapping[token])
    return result
