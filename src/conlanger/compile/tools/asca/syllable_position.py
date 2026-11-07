"""Index syllable position ``#U`` / ``U#`` → ASCA underline structures (ticket 98)."""

from __future__ import annotations

import re

from conlanger.compile.position_in_projection import (
    env_is_projected_position_in_compile_string,
    materialize_position_in_asca,
    project_position_in_target,
)
from conlanger.compile.utils.symbols import normalize_symbols_for_asca
from conlanger.utils.syllable_position import (
    strip_editorial_in_before_syllable_position,
)

SYLLABLE_AT_WORD_BOUNDARY = {
    "#U": "#<(..)_(..)>",
    "U#": "<(..)_(..)>#",
    "#U, U#": ":{#<(..)_(..)>, <(..)_(..)>#}:",
    "#%": "#<(..)_(..)>",
    "%#": "<(..)_(..)>#",
    "#%, %#": ":{#<(..)_(..)>, <(..)_(..)>#}:",
}

_COMMA_U_HASH_RE = re.compile(r"^#(U|%)\s*,\s*(U|%)#$")

_SYLLABLE_STRESS_ENV_RAW = {
    "U[-stress]": "<(..)_(..)>:[-stress]",
    "U[+stress]": "<(..)_(..)>:[+stress]",
    "in U[-stress]": "<(..)_(..)>:[-stress]",
    "in U[+stress]": "<(..)_(..)>:[+stress]",
    "%[-stress]": "<(..)_(..)>:[-stress]",
    "%[+stress]": "<(..)_(..)>:[+stress]",
    "in %[-stress]": "<(..)_(..)>:[-stress]",
    "in %[+stress]": "<(..)_(..)>:[+stress]",
}
_STRESSED_MONOSYLLABLE_ENVS_RAW = ("#U[+stress]#", "#%[+stress]#")
_STRESSED_MONOSYLLABLE_ENV_COMPILED = "#<(..)_(..)>:[+stress]#"

_IN_STRESS_COMMA_RE = re.compile(
    r",\s+in\s+(?:U|%\[(\+stress|-stress)\]|\$\[(\+stress|-stress)\])",
)

_PROSE_AFTER_HASH_U_RE = re.compile(r"\bin\s+#U\s+(?:before|with)\b", re.IGNORECASE)

_SYLLABLE_HOST_IN_MATRIX_RE = re.compile(
    r"(?P<sep>,\s+in\s+|\s+in\s+)(?:U:|U|%:?)(?P<tail>(?:\[[^\]]+\])+)(?=\s|$|!|,|\bor\b)",
)
_ENV_SET_MEMBER_MATRIX_SUFFIX_RE = re.compile(
    r"^(?P<host>(?:U|%)(?:\[[^\]]+\])+)(?P<suffix>.+)$",
)
_BARE_SYLLABLE_MATRIX_FRAGMENT_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:U|%)(?:\[[^\]]+\])+",
)
_IN_COMMA_SYLLABLE_HOST_MATRIX_RE = re.compile(
    r",\s+in\s+(?:U:|U|%:?)(?P<tail>(?:\[[^\]]+\])+)",
)
_WHOLE_IN_U_COLON_STRESS_RE = re.compile(r"^in\s+(?:U:|U|%:|%)(?P<feat>\[-stress\])$")
_WHOLE_IN_SYLLABLE_HOST_MATRIX_RE = re.compile(
    r"^in\s+(?:U:|U|%:|%)(?P<tail>(?:\[[^\]]+\])+)$",
)
_WHOLE_SYLLABLE_HOST_BRACKET_MATRIX_RE = re.compile(
    r"^(?:in\s+)?(?:U|%)(?P<tail>(?:\[[^\]]+\])+)$",
)

_IN_MECHANICAL_HASH_U_TAIL_RE = re.compile(r"\bin\s+#(U|%)(?=\s*$|\s*!)")
_IN_MECHANICAL_U_HASH_TAIL_RE = re.compile(r"\bin\s+(U|%)#(?=\s*$|\s*!)")
_COMPOUND_MECHANICAL_SYLLABLE_EDGE_RE = re.compile(
    r"^(?P<left>.+)\s+in\s+(?P<target>#U|U#|#%|%#)\s*$",
    re.IGNORECASE,
)


def normalize_syllable_position_marker(text: str) -> str | None:
    """Return a mechanical ``#U`` / ``U#`` key when ``text`` matches exactly."""
    normalized = strip_editorial_in_before_syllable_position(text.strip())
    if _COMMA_U_HASH_RE.fullmatch(normalized):
        return "#%, %#"
    if normalized in SYLLABLE_AT_WORD_BOUNDARY:
        return normalized
    return None


def compile_syllable_position_exception(raw: str | None) -> str | None:
    if raw is None:
        return None
    key = normalize_syllable_position_marker(raw)
    if key is None:
        return None
    return SYLLABLE_AT_WORD_BOUNDARY[key]


def compile_syllable_position_env(raw: str | None) -> str | None:
    if raw is None:
        return None
    key = normalize_syllable_position_marker(raw)
    if key is None:
        return None
    return SYLLABLE_AT_WORD_BOUNDARY.get(key)


def _scope_from_whole_syllable_host_matrix(text: str) -> str | None:
    """Map whole-field ``U[±F]`` / ``%[±F]`` env hosts to underline syllable scope."""
    match = _WHOLE_SYLLABLE_HOST_BRACKET_MATRIX_RE.fullmatch(text.strip())
    if match is None:
        return None
    return f"<(..)_(..)>:{match.group('tail')}"


def _compile_syllable_stress_env_from_raw(raw: str | None) -> str | None:
    if raw is None:
        return None
    stripped = raw.strip()
    if stripped in _SYLLABLE_STRESS_ENV_RAW:
        return _SYLLABLE_STRESS_ENV_RAW[stripped]
    if stripped in _STRESSED_MONOSYLLABLE_ENVS_RAW:
        return _STRESSED_MONOSYLLABLE_ENV_COMPILED
    return _scope_from_whole_syllable_host_matrix(stripped)


def _rewrite_syllable_matrix_fragments_in_segment(segment: str) -> str:
    def repl(match: re.Match[str]) -> str:
        scope = _scope_from_whole_syllable_host_matrix(match.group(0))
        return scope if scope is not None else match.group(0)

    return _BARE_SYLLABLE_MATRIX_FRAGMENT_RE.sub(repl, segment)


def _project_env_set_segment(segment: str) -> str:
    segment = segment.strip()
    scope = _scope_from_whole_syllable_host_matrix(segment)
    if scope is not None:
        return scope
    matrix_suffix = _ENV_SET_MEMBER_MATRIX_SUFFIX_RE.match(segment)
    if matrix_suffix is not None:
        host_scope = _scope_from_whole_syllable_host_matrix(matrix_suffix.group("host"))
        if host_scope is not None:
            return host_scope + matrix_suffix.group("suffix")
    return _rewrite_syllable_matrix_fragments_in_segment(segment)


def _rewrite_env_set_syllable_host_members(text: str) -> str:
    """Rewrite bare ``U[±F]`` / ``%[±F]`` members inside ``:{…}:`` env sets."""
    stripped = text.strip()
    if not stripped.startswith(":{") or not stripped.endswith("}:"):
        return text
    inner = stripped[2:-2]
    members = [member.strip() for member in inner.split(",")]
    rewritten = [_project_env_set_segment(member) for member in members]
    if rewritten == members:
        return text
    return f":{{{', '.join(rewritten)}}}:"


def _rewrite_in_syllable_host_matrix_tail(text: str) -> str:
    return _SYLLABLE_HOST_IN_MATRIX_RE.sub(
        lambda match: f"{match.group('sep')}<(..)_(..)>:{match.group('tail')}",
        text,
    )


def _rewrite_comma_in_syllable_host_matrix(text: str) -> str:
    return _IN_COMMA_SYLLABLE_HOST_MATRIX_RE.sub(
        lambda match: f", in <(..)_(..)>:{match.group('tail')}",
        text,
    )


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
        return "<(..)_(..)>:[-stress]"
    matrix_tail = _matrix_brackets_from_tail(tail)
    if matrix_tail is None:
        return text
    return f"<(..)_(..)>:{matrix_tail}"


def _rewrite_compound_mechanical_syllable_edge_env(text: str) -> str | None:
    match = _COMPOUND_MECHANICAL_SYLLABLE_EDGE_RE.match(text.strip())
    if match is None:
        return None
    left = match.group("left").strip()
    if left.lower() == "in":
        return None
    classified = project_position_in_target(match.group("target"))
    if classified is None:
        return None
    return materialize_position_in_asca(classified, structural_context=left)


def project_position_in_compiled_field(text: str | None) -> str | None:
    """Rewrite legacy string env tails with embedded ``in U…`` / ``in #U`` (ticket 174)."""
    if text is None:
        return None
    compound = _rewrite_compound_mechanical_syllable_edge_env(text)
    if compound is not None:
        return compound
    projected = text
    if not _PROSE_AFTER_HASH_U_RE.search(projected):
        projected = _IN_MECHANICAL_HASH_U_TAIL_RE.sub(" #<(..)_(..)>", projected)
        projected = _IN_MECHANICAL_U_HASH_TAIL_RE.sub(" <(..)_(..)>#", projected)

    projected = _rewrite_legacy_whole_in_syllable_host_matrix(projected)
    projected = _rewrite_in_syllable_host_matrix_tail(projected)
    projected = _WHOLE_IN_U_COLON_STRESS_RE.sub(
        lambda match: f"<(..)_(..)>:{match.group('feat')}",
        projected,
    )
    parts = projected.split(" in ")
    if len(parts) == 2:
        left = _project_env_set_segment(parts[0])
        right = _project_env_set_segment(parts[1])
        return _rewrite_env_set_syllable_host_members(f":{{{left}, {right}}}:")

    projected = _rewrite_env_set_syllable_host_members(projected.strip())
    return projected


def project_syllable_stress_compiled_env(
    env_raw: str | None,
    compiled_env: str | None,
) -> str | None:
    """Project Index syllable-stress env strings to ASCA with segment focus ``_``."""
    from_raw = _compile_syllable_stress_env_from_raw(env_raw)
    if from_raw is not None:
        return normalize_symbols_for_asca(from_raw)

    if compiled_env is None:
        return None

    projected = compiled_env

    if projected in ("U[-stress]", "in U[-stress]", "%[-stress]", "in %[-stress]"):
        return "<(..)_(..)>:[-stress]"
    if projected in ("U[+stress]", "in U[+stress]", "%[+stress]", "in %[+stress]"):
        return "<(..)_(..)>:[+stress]"

    whole_scope = _scope_from_whole_syllable_host_matrix(projected)
    if whole_scope is not None:
        return whole_scope

    def _comma_in_stress_repl(match: re.Match[str]) -> str:
        feature = match.group(1) or match.group(2)
        return f" in <(..)_(..)>:[{feature}]"

    projected = _IN_STRESS_COMMA_RE.sub(_comma_in_stress_repl, projected)
    projected = _rewrite_comma_in_syllable_host_matrix(projected)
    projected = project_position_in_compiled_field(projected)
    if projected is None:
        return None
    return _rewrite_env_set_syllable_host_members(projected)


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
