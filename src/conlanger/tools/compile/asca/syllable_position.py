"""Index syllable position ``#U`` / ``U#`` → ASCA underline structures (ticket 98)."""

from __future__ import annotations

import re

_MECHANICAL_EXCEPTION_ASCA = {
    "#U": ":{#_#, #<.._>}:",
    "U#": ":{#_#, <.._>#}:",
    "#U, U#": ":{#_#, #<.._>, <.._>#}:",
}

_MECHANICAL_ENV_ASCA = {
    "#U": "#<.._>",
    "U#": "<.._>#",
}

_EDITORIAL_IN_RE = re.compile(
    r"^in\s+(#U(?:\s*,\s*U#)?|U#)\s*$",
    re.IGNORECASE,
)
_COMMA_U_HASH_RE = re.compile(r"^#U\s*,\s*U#$")


def strip_editorial_in_before_syllable_position(text: str) -> str:
    """Strip Index editorial ``in`` before mechanical ``#U`` / ``U#`` markers."""
    stripped = text.strip()
    match = _EDITORIAL_IN_RE.match(stripped)
    if not match:
        return text
    marker = match.group(1)
    if _COMMA_U_HASH_RE.fullmatch(marker):
        return "#U, U#"
    return marker


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


def apply_syllable_position_compiled_overrides(
    env_raw: str | None,
    exception_raw: str | None,
    compiled_env: str | None,
    compiled_exception: str | None,
) -> tuple[str | None, str | None]:
    """Override compiled env/exception when raw fields are mechanical syllable markers."""
    override_env = compile_syllable_position_env(env_raw)
    override_exception = compile_syllable_position_exception(exception_raw)
    if override_env is not None:
        compiled_env = override_env
    if override_exception is not None:
        compiled_exception = override_exception
    return compiled_env, compiled_exception
