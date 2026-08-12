"""Documented ASCA per-rule compile pipeline (``docs/sound-change-applier.md``)."""

from __future__ import annotations

from conlanger.tools.compile.asca.aliases import apply_asca_aliases
from conlanger.tools.compile.asca.apostrophes import normalize_typographic_apostrophes
from conlanger.tools.compile.asca.ejectives import normalize_asca_ejective_marks
from conlanger.tools.compile.asca.ellipsis import (
    normalize_asca_optional_grouping_ellipsis,
)
from conlanger.tools.compile.asca.group_mappings import (
    apply_asca_group_mappings_to_string,
)
from conlanger.tools.compile.asca.length_marks import normalize_asca_length_marks
from conlanger.tools.compile.asca.planned import (
    apply_section_local_abbreviations,
    expand_index_subscript_references,
    expand_meta_notation,
)
from conlanger.tools.compile.asca.superscript_modifiers import (
    normalize_asca_superscript_modifiers,
)

ASCA_COMPILE_STEP_NAMES: tuple[str, ...] = (
    "normalize_asca_optional_grouping_ellipsis",
    "expand_index_subscript_references",
    "apply_section_local_abbreviations",
    "normalize_asca_superscript_modifiers",
    "apply_asca_group_mappings",
    "normalize_asca_length_marks",
    "normalize_typographic_apostrophes",
    "normalize_asca_ejective_marks",
    "apply_asca_aliases",
    "expand_meta_notation",
)


def compile_asca_rule_string(
    text: str,
    *,
    group_mappings: dict[str, str],
) -> str:
    """Run the documented ASCA compile transforms on a joined rule string."""
    text = normalize_asca_optional_grouping_ellipsis(text)
    text = expand_index_subscript_references(text)
    text = apply_section_local_abbreviations(text)
    text = normalize_asca_superscript_modifiers(text, group_mappings)
    text = apply_asca_group_mappings_to_string(text, group_mappings)
    text = normalize_asca_length_marks(text)
    text = normalize_typographic_apostrophes(text)
    text = normalize_asca_ejective_marks(text)
    text = apply_asca_aliases(text)
    return expand_meta_notation(text)
