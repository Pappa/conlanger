"""Index syllable position ``#U`` / ``U#`` → ASCA underline structures (ticket 98)."""

from __future__ import annotations

import re

from conlanger.compile.position_in_projection import (
    env_is_projected_position_in_compile_string,
)
from conlanger.ingest.utils.syllable_position import (
    strip_editorial_in_before_syllable_position,
)
from conlanger.utils.symbols import project_index_syllable_stem_symbols

_MECHANICAL_EXCEPTION_ASCA = {
    "#U": ":{#_#, #<.._>}:",
    "U#": ":{#_#, <.._>#}:",
    "#U, U#": ":{#_#, #<.._>, <.._>#}:",
}

_MECHANICAL_ENV_ASCA = {
    "#U": "#<.._>",
    "U#": "<.._>#",
}

_COMMA_U_HASH_RE = re.compile(r"^#U\s*,\s*U#$")

_SYLLABLE_STRESS_ENV_RAW = {
    "U[-stress]": "_ %[-stress]",
    "U[+stress]": "_ %[+stress]",
    "in U[-stress]": "_ %[-stress]",
    "in U[+stress]": "_ %[+stress]",
}
_STRESSED_MONOSYLLABLE_ENV_RAW = "#U[+stress]#"
_STRESSED_MONOSYLLABLE_ENV_COMPILED = "#_[+stress]"

_IN_STRESS_COMMA_RE = re.compile(
    r",\s+in\s+(?:%\[(\+stress|-stress)\]|\$\[(\+stress|-stress)\])",
)

_PROSE_AFTER_HASH_U_RE = re.compile(r"\bin\s+#U\s+(?:before|with)\b", re.IGNORECASE)

_SYLLABLE_HOST_IN_STRESS_RE = re.compile(
    r"(?P<sep>,\s+in\s+|\s+in\s+)(?:U:|%)(?P<feat>\[(?:\+stress|-stress)\])(?=$|\s*!)",
)
_WHOLE_IN_U_COLON_STRESS_RE = re.compile(r"^in\s+(?:U:|%:)(?P<feat>\[-stress\])$")
_WHOLE_IN_SYLLABLE_HOST_MATRIX_RE = re.compile(
    r"^in\s+(?:U:|%:)(?P<tail>(?:\[[^\]]+\])+)$",
)

_IN_MECHANICAL_HASH_U_TAIL_RE = re.compile(r"\bin\s+#U(?=\s*$|\s*!)")
_IN_MECHANICAL_U_HASH_TAIL_RE = re.compile(r"\bin\s+U#(?=\s*$|\s*!)")


def normalize_syllable_position_marker(text: str) -> str | None:
    """Return a mechanical ``#U`` / ``U#`` key when ``text`` matches exactly."""
    normalized = strip_editorial_in_before_syllable_position(text.strip())
    if _COMMA_U_HASH_RE.fullmatch(normalized):
        return "#U, U#"
    if normalized in _MECHANICAL_EXCEPTION_ASCA:
        return normalized
    return None


def compile_syllable_position_exception(raw: str | None) -> str | None:
    if raw is None:
        return None
    key = normalize_syllable_position_marker(raw)
    if key is None:
        return None
    return _MECHANICAL_EXCEPTION_ASCA[key]


def compile_syllable_position_env(raw: str | None) -> str | None:
    if raw is None:
        return None
    key = normalize_syllable_position_marker(raw)
    if key is None:
        return None
    return _MECHANICAL_ENV_ASCA.get(key)


def _compile_syllable_stress_env_from_raw(raw: str | None) -> str | None:
    if raw is None:
        return None
    stripped = raw.strip()
    if stripped in _SYLLABLE_STRESS_ENV_RAW:
        return _SYLLABLE_STRESS_ENV_RAW[stripped]
    if stripped == _STRESSED_MONOSYLLABLE_ENV_RAW:
        return _STRESSED_MONOSYLLABLE_ENV_COMPILED
    return None


def _rewrite_in_u_stress_tail(feat: str) -> str:
    return f" in ${feat}"


def _matrix_brackets_from_tail(tail: str) -> str | None:
    if re.fullmatch(r"\[\+stress\](?:\[[^\]]+\])*", tail):
        return tail
    if re.fullmatch(r"\[\+stress,\s*.+\]", tail) is None:
        return None
    features = re.findall(r"\+[^\s,\]]+", tail)
    if not features or features[0] != "+stress":
        return None
    return "".join(f"[{feature}]" for feature in features)


def _rewrite_legacy_whole_in_syllable_host_matrix(text: str) -> str:
    match = _WHOLE_IN_SYLLABLE_HOST_MATRIX_RE.fullmatch(text.strip())
    if match is None:
        return text
    tail = match.group("tail")
    if re.fullmatch(r"\[-stress\]", tail):
        return "_ $[-stress]"
    matrix_tail = _matrix_brackets_from_tail(tail)
    if matrix_tail is None:
        return text
    return f"_ %{matrix_tail}"


def project_position_in_compiled_field(text: str | None) -> str | None:
    """Rewrite legacy string env tails with embedded ``in U…`` / ``in #U`` (ticket 174)."""
    if text is None:
        return None
    projected = text
    if not _PROSE_AFTER_HASH_U_RE.search(projected):
        projected = _IN_MECHANICAL_HASH_U_TAIL_RE.sub(" #<.._>", projected)
        projected = _IN_MECHANICAL_U_HASH_TAIL_RE.sub(" <.._>#", projected)

    projected = _rewrite_legacy_whole_in_syllable_host_matrix(projected)
    projected = _SYLLABLE_HOST_IN_STRESS_RE.sub(
        lambda match: _rewrite_in_u_stress_tail(match.group("feat")),
        projected,
    )
    return _WHOLE_IN_U_COLON_STRESS_RE.sub(
        lambda match: f"_ ${match.group('feat')}",
        projected,
    )


def project_syllable_stress_compiled_env(
    env_raw: str | None,
    compiled_env: str | None,
) -> str | None:
    """Project Index syllable-stress env strings to ASCA with segment focus ``_``."""
    from_raw = _compile_syllable_stress_env_from_raw(env_raw)
    if from_raw is not None:
        return project_index_syllable_stem_symbols(from_raw)

    if compiled_env is None:
        return None

    projected = compiled_env
    if projected in ("%[-stress]", "in %[-stress]"):
        return "_ $[-stress]"
    if projected in ("%[+stress]", "in %[+stress]"):
        return "_ $[+stress]"
    if projected == "#%[+stress]#":
        return _STRESSED_MONOSYLLABLE_ENV_COMPILED

    def _comma_in_stress_repl(match: re.Match[str]) -> str:
        feature = match.group(1) or match.group(2)
        return f" in $[{feature}]"

    projected = _IN_STRESS_COMMA_RE.sub(_comma_in_stress_repl, projected)
    return project_position_in_compiled_field(projected)


def apply_syllable_position_compiled_overrides(
    env_raw: str | None,
    exception_raw: str | None,
    compiled_env: str | None,
    compiled_exception: str | None,
) -> tuple[str | None, str | None]:
    """Override compiled env/exception when raw fields are mechanical syllable markers."""
    if env_is_projected_position_in_compile_string(env_raw):
        compiled_env = env_raw
        compiled_exception = project_position_in_compiled_field(compiled_exception)
        return compiled_env, compiled_exception

    override_env = compile_syllable_position_env(env_raw)
    override_exception = compile_syllable_position_exception(exception_raw)
    if override_env is not None:
        compiled_env = override_env
    compiled_env = project_syllable_stress_compiled_env(env_raw, compiled_env)
    if override_exception is not None:
        compiled_exception = override_exception
    compiled_exception = project_position_in_compiled_field(compiled_exception)
    return compiled_env, compiled_exception
