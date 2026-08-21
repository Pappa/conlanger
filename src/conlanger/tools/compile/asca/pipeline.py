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
from conlanger.tools.compile.asca.parallel import drop_mixed_parallel_null_columns
from conlanger.tools.compile.asca.planned import (
    apply_section_local_abbreviations,
    expand_meta_notation,
)
from conlanger.tools.compile.asca.series_mappings import apply_compiler_series_mappings
from conlanger.tools.compile.asca.structures import join_asca_rule_fields
from conlanger.tools.compile.asca.subscript_references import (
    expand_subscript_references_across_fields,
)
from conlanger.tools.compile.asca.superscript_modifiers import (
    normalize_asca_superscript_modifiers,
)
from conlanger.tools.compile.asca.tone_matrices import normalize_asca_tone_matrices
from conlanger.utils.file_io import load_compiler_config
from conlanger.utils.mappings import CompilerConfig


def _compile_kwargs(
    *,
    group_mappings: dict[str, str],
    section_index: str,
    compiler_config: CompilerConfig | None,
) -> tuple[dict[str, str], str, CompilerConfig]:
    config = compiler_config if compiler_config is not None else load_compiler_config()
    return group_mappings, section_index, config


def compile_asca_field_pre_subscript(
    text: str,
    *,
    group_mappings: dict[str, str],
    section_index: str = "",
    compiler_config: CompilerConfig | None = None,
) -> str:
    """Run per-field transforms through group mappings (spike 38 orders 2–5)."""
    if not text:
        return text
    mappings, index, config = _compile_kwargs(
        group_mappings=group_mappings,
        section_index=section_index,
        compiler_config=compiler_config,
    )
    text = normalize_asca_optional_grouping_ellipsis(text)
    text = apply_compiler_series_mappings(
        text, section_index=index, compiler_config=config
    )
    text = apply_section_local_abbreviations(text)
    text = normalize_asca_superscript_modifiers(text, mappings)
    return apply_asca_group_mappings_to_string(text, mappings)


def compile_asca_field_post_subscript(text: str) -> str:
    """Run per-field transforms after cross-field subscripts (spike 38 orders 6–10)."""
    if not text:
        return text
    text = normalize_asca_length_marks(text)
    text = normalize_asca_tone_matrices(text)
    text = normalize_typographic_apostrophes(text)
    text = normalize_asca_ejective_marks(text)
    text = normalize_asca_breve_marks(text)
    return expand_meta_notation(text)


def compile_asca_field(
    text: str,
    *,
    group_mappings: dict[str, str],
    section_index: str = "",
    compiler_config: CompilerConfig | None = None,
) -> str:
    """Run the full per-field ASCA compile path when no cross-field subscripts apply."""
    text = compile_asca_field_pre_subscript(
        text,
        group_mappings=group_mappings,
        section_index=section_index,
        compiler_config=compiler_config,
    )
    return compile_asca_field_post_subscript(text)


def compile_asca_rule_fields(
    inp: str,
    output: str,
    env: str | None = None,
    exception: str | None = None,
    *,
    group_mappings: dict[str, str],
    section_index: str = "",
    compiler_config: CompilerConfig | None = None,
) -> str:
    """Compile four rule fields separately, expand cross-field subscripts, then join."""
    inp = drop_mixed_parallel_null_columns(inp)
    output = drop_mixed_parallel_null_columns(output)
    compile_kwargs = {
        "group_mappings": group_mappings,
        "section_index": section_index,
        "compiler_config": compiler_config,
    }
    compiled_input = compile_asca_field_pre_subscript(inp, **compile_kwargs)
    compiled_output = compile_asca_field_pre_subscript(output, **compile_kwargs)
    compiled_env = (
        compile_asca_field_pre_subscript(env, **compile_kwargs)
        if env is not None
        else None
    )
    compiled_exception = (
        compile_asca_field_pre_subscript(exception, **compile_kwargs)
        if exception is not None
        else None
    )
    compiled_input, compiled_output, compiled_env, compiled_exception = (
        expand_subscript_references_across_fields(
            compiled_input,
            compiled_output,
            compiled_env,
            compiled_exception,
        )
    )
    compiled_input = compile_asca_field_post_subscript(compiled_input)
    compiled_output = compile_asca_field_post_subscript(compiled_output)
    if compiled_env is not None:
        compiled_env = compile_asca_field_post_subscript(compiled_env)
    if compiled_exception is not None:
        compiled_exception = compile_asca_field_post_subscript(compiled_exception)
    return join_asca_rule_fields(
        compiled_input,
        compiled_output,
        compiled_env,
        compiled_exception,
    )
