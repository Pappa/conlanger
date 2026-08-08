"""Planned ASCA compile transforms (spike 38 orders 4, 10)."""

from conlanger.tools.asca_compile.subscript_references import (
    expand_index_subscript_references,
)
from conlanger.tools.asca_compile.parenthetical import (
    expand_index_parenthetical_notation,
)
from conlanger.tools.asca_compile.tilde import expand_index_tilde_notation

__all__ = [
    "apply_section_local_abbreviations",
    "expand_index_subscript_references",
    "expand_meta_notation",
]


def apply_section_local_abbreviations(text: str) -> str:
    """Section-local abbreviation table expansion (planned)."""
    return text


def expand_meta_notation(text: str) -> str:
    """Cluster-driven meta-notation handlers."""
    text = expand_index_tilde_notation(text)
    return expand_index_parenthetical_notation(text)
