"""Classified ``position.in`` target → ASCA env fragments (tickets 156, 174)."""

from __future__ import annotations

import re

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

_STRESSED_MONOSYLLABLE_TARGETS = ("#U[+stress]#", "%[+stress]#")

_STRESSED_MONOSYLLABLE_ASCA = "#<(..)_(..)>:[+stress]#"

_POSITION_IN_CONTEXT_STRESS_RE = re.compile(
    r"^.+ in \$[\[(](?:\+stress|-stress)\]$",
)
_POSITION_IN_CONTEXT_EDGE_RE = re.compile(r"^.+ #<\(\.\.\)_\(\.\.\)>$")
_POSITION_IN_CONTEXT_SCOPE_RE = re.compile(
    r"^.+ in (?:#)?<\(\.\.\)_\(\.\.\)>:(?:\[[^\]]+\])+$",
)
_WHOLE_POSITION_IN_STRESS_RE = re.compile(r"^_\s*\$[\[(](?:\+stress|-stress)\]$")
_WHOLE_POSITION_IN_MATRIX_RE = re.compile(
    r"^_\s*%\[\+stress\](?:\[[^\]]+\])*$",
)
_WHOLE_POSITION_IN_SCOPE_RE = re.compile(
    r"^(?:#)?<\(\.\.\)_\(\.\.\)>:(?:\[[^\]]+\])+$",
)
_U_BRACKET_MATRIX_RE = re.compile(r"^U(?:\[[^\]]+\])+$")
_HASH_U_COLON_MATRIX_RE = re.compile(r"^#U:(?:\[[^\]]+\])+$")


def _normalize_position_in_target(target: str) -> str:
    return strip_editorial_in_before_syllable_position(target.strip())


def _mechanical_position_in_env(target: str) -> str | None:
    normalized = _normalize_position_in_target(target)
    if _COMMA_U_HASH_RE.fullmatch(normalized):
        return None
    return SYLLABLE_AT_WORD_BOUNDARY.get(normalized)


def _scope_from_matrix_tail(matrix_tail: str, *, word_initial: bool = False) -> str:
    template = "#<(..)_(..)>" if word_initial else "<(..)_(..)>"
    return f"{template}:{matrix_tail}"


def _matrix_brackets_from_u_colon_target(target: str) -> str | None:
    if not target.startswith("U:"):
        return None
    tail = target[2:]
    if re.fullmatch(r"\[-stress\]", tail):
        return None
    if re.fullmatch(r"\[\+stress\](?:\[[^\]]+\])*", tail):
        return tail
    if re.fullmatch(r"\[\+stress,\s*.+\]", tail):
        features = re.findall(r"\+[^\s,\]]+", tail)
        if not features or features[0] != "+stress":
            return None
        return "".join(f"[{feature}]" for feature in features)
    if re.fullmatch(r"(?:\[[^\]]+\])+", tail):
        return tail
    return None


def _matrix_tail_from_u_bracket_target(target: str) -> str | None:
    if not _U_BRACKET_MATRIX_RE.fullmatch(target):
        return None
    return target[1:]


def _matrix_tail_from_hash_u_colon_target(target: str) -> str | None:
    if not _HASH_U_COLON_MATRIX_RE.fullmatch(target):
        return None
    return target[3:]


def project_position_in_target(target: str) -> str | None:
    """Map a ``position.in`` target value to ASCA, or ``None`` for ``in {{v}}`` fallback."""
    normalized = _normalize_position_in_target(target)
    if not normalized:
        return None

    mechanical_asca = _mechanical_position_in_env(normalized)
    if mechanical_asca is not None:
        return mechanical_asca

    if normalized in _STRESSED_MONOSYLLABLE_TARGETS:
        return _STRESSED_MONOSYLLABLE_ASCA

    if normalized in ("U[-stress]", "U[+stress]"):
        feature = "[-stress]" if normalized == "U[-stress]" else "[+stress]"
        return _scope_from_matrix_tail(feature)

    hash_u_tail = _matrix_tail_from_hash_u_colon_target(normalized)
    if hash_u_tail is not None:
        return _scope_from_matrix_tail(hash_u_tail, word_initial=True)

    u_bracket_tail = _matrix_tail_from_u_bracket_target(normalized)
    if u_bracket_tail is not None:
        return _scope_from_matrix_tail(u_bracket_tail)

    matrix_tail = _matrix_brackets_from_u_colon_target(normalized)
    if matrix_tail is not None:
        return _scope_from_matrix_tail(matrix_tail)

    return None


_MECHANICAL_SYLLABLE_EDGE_PROJECTIONS = frozenset(
    {
        "#<(..)_(..)>",
        "<(..)_(..)>#",
        _STRESSED_MONOSYLLABLE_ASCA,
        ":{#<(..)_(..)>, <(..)_(..)>#}:",
    }
)

_SEGMENT_SCOPED_SYLLABLE_HOST_RE = re.compile(r"^(?:%|U|\$)\S*$")


def _context_warrants_syllable_edge_env_set(context: str) -> bool:
    if "_" in context:
        return True
    return _SEGMENT_SCOPED_SYLLABLE_HOST_RE.fullmatch(context.strip()) is not None


def _materialize_syllable_edge_env_set(left: str, right: str) -> str:
    return f":{{{left}, {right}}}:"


def materialize_position_in_asca(
    projection: str,
    *,
    structural_context: str | None,
) -> str:
    """Join structural ``context`` with classified ``in`` scope (ticket 163 ``context in $…``)."""
    if (
        structural_context
        and projection in _MECHANICAL_SYLLABLE_EDGE_PROJECTIONS
        and _context_warrants_syllable_edge_env_set(structural_context)
    ):
        return _materialize_syllable_edge_env_set(structural_context, projection)
    if structural_context:
        return f"{structural_context} in {projection}"
    return projection


def env_is_projected_position_in_compile_string(raw: str | None) -> bool:
    """True when ``env`` was already projected from classified ``position.in`` (skip ASCA rewrites)."""
    if raw is None or not raw.strip():
        return False
    text = raw.strip()
    if text in ("#<(..)_(..)>", "<(..)_(..)>#", _STRESSED_MONOSYLLABLE_ASCA):
        return True
    if _WHOLE_POSITION_IN_STRESS_RE.fullmatch(text):
        return True
    if _WHOLE_POSITION_IN_MATRIX_RE.fullmatch(text):
        return True
    if _WHOLE_POSITION_IN_SCOPE_RE.fullmatch(text):
        return True
    if _POSITION_IN_CONTEXT_STRESS_RE.match(text):
        return True
    if _POSITION_IN_CONTEXT_SCOPE_RE.match(text):
        return True
    return bool(_POSITION_IN_CONTEXT_EDGE_RE.match(text))
