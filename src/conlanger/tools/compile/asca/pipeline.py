"""Documented ASCA per-rule compile pipeline (``docs/system/sound-change-applier.md``)."""

from __future__ import annotations

from conlanger.tools.compile.asca.apostrophes import normalize_typographic_apostrophes
from conlanger.tools.compile.asca.breve_marks import normalize_asca_breve_marks
from conlanger.tools.compile.asca.dot_affricate import normalize_dot_affricate_notation
from conlanger.tools.compile.asca.editorial_slash_gloss import (
    normalize_editorial_slash_gloss_residue,
)
from conlanger.tools.compile.asca.ejectives import normalize_asca_ejective_marks
from conlanger.tools.compile.asca.ellipsis import (
    normalize_asca_optional_grouping_ellipsis,
)
from conlanger.tools.compile.asca.group_mappings import (
    apply_asca_group_mappings_to_string,
)
from conlanger.tools.compile.asca.host_bracket_matrices import (
    normalize_asca_host_bracket_matrices,
)
from conlanger.tools.compile.asca.identity_exceptions import (
    apply_identity_exception_input_narrowing,
    resolve_index_identity_exceptions,
)
from conlanger.tools.compile.asca.length_marks import normalize_asca_length_marks
from conlanger.tools.compile.asca.optional_length import (
    expand_optional_length_in_text,
    expand_optional_length_tokens,
)
from conlanger.tools.compile.asca.parallel import (
    drop_mixed_parallel_null_columns,
    drop_mixed_parallel_null_columns_tokens,
)
from conlanger.tools.compile.asca.pharyngealized_marks import (
    normalize_asca_pharyngealized_marks,
)
from conlanger.tools.compile.asca.planned import (
    apply_section_local_abbreviations,
    expand_meta_notation,
)
from conlanger.tools.compile.asca.prenasal_prefix import normalize_prenasal_prefix
from conlanger.tools.compile.asca.series_mappings import apply_compiler_series_mappings
from conlanger.tools.compile.asca.sets import (
    convert_set_to_environment_set,
    is_whole_field_set,
)
from conlanger.tools.compile.asca.structures import join_asca_rule_fields
from conlanger.tools.compile.asca.subscript_references import (
    expand_subscript_references_across_fields,
)
from conlanger.tools.compile.asca.superscript_modifiers import (
    normalize_asca_superscript_modifiers,
)
from conlanger.tools.compile.asca.syllable_position import (
    apply_syllable_position_compiled_overrides,
)
from conlanger.tools.compile.asca.tone_matrices import (
    normalize_asca_adjacent_feature_matrices,
    normalize_asca_tone_matrices,
)
from conlanger.tools.compile.asca.voice_prerequisite_diacritics import (
    normalize_asca_voice_prerequisite_diacritics,
)
from conlanger.tools.compile.compile_fields import RuleEnv, RuleInput, RuleOutput
from conlanger.utils.mappings import CompilerConfig


def _resolve_compiler_config(
    compiler_config: CompilerConfig | None,
) -> CompilerConfig:
    return compiler_config or CompilerConfig()


def compile_asca_field_pre_subscript(
    text: str,
    *,
    section_index: str = "",
    compiler_config: CompilerConfig | None = None,
) -> str:
    """Run per-field transforms through group mappings (spike 38 orders 2–5)."""
    if not text:
        return text
    config = _resolve_compiler_config(compiler_config)
    mappings = config.group_mappings
    text = normalize_editorial_slash_gloss_residue(text)
    text = normalize_asca_optional_grouping_ellipsis(text)
    text = apply_compiler_series_mappings(
        text, section_index=section_index, compiler_config=config
    )
    text = apply_section_local_abbreviations(text)
    text = normalize_asca_superscript_modifiers(text, mappings)
    return apply_asca_group_mappings_to_string(text, mappings)


def compile_asca_field_post_subscript(text: str) -> str:
    """Run per-field transforms after cross-field subscripts (spike 38 orders 6–10)."""
    if not text:
        return text
    text = expand_optional_length_in_text(text)
    text = normalize_asca_length_marks(text)
    text = normalize_asca_tone_matrices(text)
    text = normalize_typographic_apostrophes(text)
    text = normalize_asca_pharyngealized_marks(text)
    text = normalize_asca_ejective_marks(text)
    text = normalize_asca_breve_marks(text)
    text = normalize_asca_voice_prerequisite_diacritics(text)
    text = normalize_prenasal_prefix(text)
    text = normalize_dot_affricate_notation(text)
    return expand_meta_notation(text)


def compile_asca_rule_field_strings(
    inp: str,
    output: str,
    env: str | None = None,
    exception: str | None = None,
    *,
    section_index: str = "",
    compiler_config: CompilerConfig | None = None,
) -> tuple[str, str, str | None, str | None]:
    """Compile four rule fields separately and expand cross-field subscripts."""
    inp = drop_mixed_parallel_null_columns(inp)
    output = drop_mixed_parallel_null_columns(output)
    compile_kwargs = {
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
    config = _resolve_compiler_config(compiler_config)
    (
        compiled_input,
        compiled_output,
        compiled_env,
        compiled_exception,
        pending_identity,
    ) = resolve_index_identity_exceptions(
        compiled_input,
        compiled_output,
        compiled_env,
        compiled_exception,
        exception_raw=exception,
        group_mappings=config.group_mappings,
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
    compiled_input = normalize_asca_host_bracket_matrices(compiled_input)
    compiled_output = normalize_asca_host_bracket_matrices(compiled_output)
    if pending_identity is not None:
        compiled_input = apply_identity_exception_input_narrowing(
            compiled_input,
            pending_identity,
        )
    compiled_input = normalize_asca_adjacent_feature_matrices(compiled_input)
    compiled_output = normalize_asca_adjacent_feature_matrices(compiled_output)
    if compiled_env is not None:
        compiled_env = compile_asca_field_post_subscript(compiled_env)
        if is_whole_field_set(compiled_env):
            compiled_env = convert_set_to_environment_set(compiled_env)
    if compiled_exception is not None:
        compiled_exception = compile_asca_field_post_subscript(compiled_exception)
        if is_whole_field_set(compiled_exception):
            compiled_exception = convert_set_to_environment_set(compiled_exception)
    compiled_env, compiled_exception = apply_syllable_position_compiled_overrides(
        env,
        exception,
        compiled_env,
        compiled_exception,
    )
    return compiled_input, compiled_output, compiled_env, compiled_exception


def compile_asca_rule_compile_fields(
    inp: RuleInput,
    output: RuleOutput,
    env: RuleEnv | None = None,
    exception: RuleEnv | None = None,
    *,
    section_index: str = "",
    compiler_config: CompilerConfig | None = None,
) -> tuple[RuleInput, RuleOutput, RuleEnv | None, RuleEnv | None]:
    """Compile four pydantic compile-field objects; write compiled ASCA on each."""
    inp = inp.with_tokens(drop_mixed_parallel_null_columns_tokens(inp.tokens))
    output = output.with_tokens(drop_mixed_parallel_null_columns_tokens(output.tokens))
    inp = inp.with_tokens(expand_optional_length_tokens(inp.tokens))
    output = output.with_tokens(expand_optional_length_tokens(output.tokens))
    if env is not None:
        env = env.with_tokens(expand_optional_length_tokens(env.tokens))
    if exception is not None:
        exception = exception.with_tokens(
            expand_optional_length_tokens(exception.tokens)
        )
    compiled_input, compiled_output, compiled_env, compiled_exception = (
        compile_asca_rule_field_strings(
            inp.raw,
            output.raw,
            env.raw if env is not None else None,
            exception.raw if exception is not None else None,
            section_index=section_index,
            compiler_config=compiler_config,
        )
    )
    return (
        inp.with_compiled(compiled_input),
        output.with_compiled(compiled_output),
        env.with_compiled(compiled_env) if env is not None else None,
        exception.with_compiled(compiled_exception) if exception is not None else None,
    )


def compile_asca_rule_fields(
    inp: str,
    output: str,
    env: str | None = None,
    exception: str | None = None,
    *,
    section_index: str = "",
    compiler_config: CompilerConfig | None = None,
) -> str:
    """Compile four rule fields separately, expand cross-field subscripts, then join."""
    return join_asca_rule_fields(
        *compile_asca_rule_field_strings(
            inp,
            output,
            env,
            exception,
            section_index=section_index,
            compiler_config=compiler_config,
        )
    )
