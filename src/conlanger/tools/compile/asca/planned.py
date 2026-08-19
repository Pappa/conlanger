"""Planned ASCA compile transforms (spike 38 orders 4, 10)."""

from conlanger.tools.compile.asca.input_optionals import (
    expand_input_optionals_to_structures,
)
from conlanger.tools.compile.asca.parenthetical import (
    expand_index_parenthetical_notation,
)
from conlanger.tools.compile.asca.slash_boundary import (
    drop_concatenated_deletion_column,
)
from conlanger.tools.compile.asca.subscript_references import (
    expand_index_subscript_references,
)
from conlanger.tools.compile.asca.tilde import expand_index_tilde_notation

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
    text = expand_index_parenthetical_notation(text)
    text = expand_input_optionals_to_structures(text)
    return drop_concatenated_deletion_column(text)
