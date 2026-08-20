"""Documented ASCA per-rule compile pipeline (``docs/sound-change-applier.md``)."""

from __future__ import annotations

from conlanger.tools.compile.asca.apostrophes import normalize_typographic_apostrophes
from conlanger.tools.compile.asca.breve_marks import normalize_asca_breve_marks
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
from conlanger.tools.compile.asca.series_mappings import apply_compiler_series_mappings
from conlanger.tools.compile.asca.superscript_modifiers import (
    normalize_asca_superscript_modifiers,
)
from conlanger.tools.compile.asca.tone_matrices import normalize_asca_tone_matrices
from conlanger.utils.file_io import load_compiler_config
from conlanger.utils.mappings import CompilerConfig


def compile_asca_rule_string(
    text: str,
    *,
    group_mappings: dict[str, str],
    section_index: str = "",
    compiler_config: CompilerConfig | None = None,
) -> str:
    """Run the documented ASCA compile transforms on a joined rule string."""
    config = compiler_config if compiler_config is not None else load_compiler_config()
    text = normalize_asca_optional_grouping_ellipsis(text)
    text = apply_compiler_series_mappings(
        text, section_index=section_index, compiler_config=config
    )
    text = expand_index_subscript_references(text)
    text = apply_section_local_abbreviations(text)
    text = normalize_asca_superscript_modifiers(text, group_mappings)
    text = apply_asca_group_mappings_to_string(text, group_mappings)
    text = normalize_asca_length_marks(text)
    text = normalize_asca_tone_matrices(text)
    text = normalize_typographic_apostrophes(text)
    text = normalize_asca_ejective_marks(text)
    text = normalize_asca_breve_marks(text)
    return expand_meta_notation(text)
