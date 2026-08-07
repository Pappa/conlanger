"""Documented ASCA per-rule compile pipeline (``docs/sound-change-applier.md``)."""

from __future__ import annotations

from conlanger.tools.asca_compile.aliases import apply_asca_aliases
from conlanger.tools.asca_compile.apostrophes import normalize_typographic_apostrophes
from conlanger.tools.asca_compile.ejectives import normalize_asca_ejective_marks
from conlanger.tools.asca_compile.ellipsis import (
    normalize_asca_optional_grouping_ellipsis,
)
from conlanger.tools.asca_compile.group_mappings import (
    apply_asca_group_mappings_to_string,
    asca_group_mappings_dict,
)
from conlanger.tools.asca_compile.length_marks import normalize_asca_length_marks
from conlanger.tools.asca_compile.planned import (
    apply_section_local_abbreviations,
    expand_index_subscript_references,
    expand_meta_notation,
)

# Steps 2–10 after field join (step 1) in RuleChange._compile_rule_text.
ASCA_COMPILE_STEP_NAMES: tuple[str, ...] = (
    "normalize_asca_optional_grouping_ellipsis",
    "expand_index_subscript_references",
    "apply_section_local_abbreviations",
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
    group_mappings: dict[str, str] | None = None,
) -> str:
    """Run the documented ASCA compile transforms on a joined rule string."""
    mappings = (
        group_mappings if group_mappings is not None else asca_group_mappings_dict()
    )
    text = normalize_asca_optional_grouping_ellipsis(text)
    text = expand_index_subscript_references(text)
    text = apply_section_local_abbreviations(text)
    text = apply_asca_group_mappings_to_string(text, mappings)
    text = normalize_asca_length_marks(text)
    text = normalize_typographic_apostrophes(text)
    text = normalize_asca_ejective_marks(text)
    text = apply_asca_aliases(text)
    return expand_meta_notation(text)
