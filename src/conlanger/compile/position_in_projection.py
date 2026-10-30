"""Classified ``position.in`` target → ASCA env fragments (tickets 156, 174)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from conlanger.utils.syllable_position import (
    strip_editorial_in_before_syllable_position,
)

_MECHANICAL_ENV_ASCA = {
    "#U": "#<.._>",
    "U#": "<.._>#",
}
_COMMA_U_HASH_RE = re.compile(r"^#U\s*,\s*U#$")

_STRESSED_MONOSYLLABLE_TARGET = "#U[+stress]#"
_STRESSED_MONOSYLLABLE_ASCA = "#_[+stress]"

_POSITION_IN_CONTEXT_STRESS_RE = re.compile(
    r"^.+ in \$[\[(](?:\+stress|-stress)\]$",
)
_POSITION_IN_CONTEXT_EDGE_RE = re.compile(r"^.+ #<.._>$")
_WHOLE_POSITION_IN_STRESS_RE = re.compile(r"^_\s*\$[\[(](?:\+stress|-stress)\]$")
_WHOLE_POSITION_IN_MATRIX_RE = re.compile(
    r"^_\s*%\[\+stress\](?:\[[^\]]+\])*$",
)


@dataclass(frozen=True, slots=True)
class PositionInAsca:
    """ASCA env from a classified ``position.in`` **target** (never editorial ``in``)."""

    alone: str
    beside_context: str


def _normalize_position_in_target(target: str) -> str:
    return strip_editorial_in_before_syllable_position(target.strip())


def _mechanical_position_in_env(target: str) -> str | None:
    normalized = _normalize_position_in_target(target)
    if _COMMA_U_HASH_RE.fullmatch(normalized):
        return None
    return _MECHANICAL_ENV_ASCA.get(normalized)


def _matrix_brackets_from_u_colon_target(target: str) -> str | None:
    if not target.startswith("U:"):
        return None
    tail = target[2:]
    if re.fullmatch(r"\[-stress\]", tail):
        return None
    if re.fullmatch(r"\[\+stress\](?:\[[^\]]+\])*", tail):
        return tail
    if re.fullmatch(r"\[\+stress,\s*.+\]", tail) is None:
        return None
    features = re.findall(r"\+[^\s,\]]+", tail)
    if not features or features[0] != "+stress":
        return None
    return "".join(f"[{feature}]" for feature in features)


def project_position_in_target(target: str) -> PositionInAsca | None:
    """Map a ``position.in`` target value to ASCA, or ``None`` for ``in {{v}}`` fallback."""
    normalized = _normalize_position_in_target(target)
    if not normalized:
        return None

    mechanical_asca = _mechanical_position_in_env(normalized)
    if mechanical_asca is not None:
        return PositionInAsca(alone=mechanical_asca, beside_context=mechanical_asca)

    if normalized == _STRESSED_MONOSYLLABLE_TARGET:
        return PositionInAsca(
            alone=_STRESSED_MONOSYLLABLE_ASCA,
            beside_context=_STRESSED_MONOSYLLABLE_ASCA,
        )

    if normalized in ("U[-stress]", "U[+stress]"):
        feature = "[-stress]" if normalized == "U[-stress]" else "[+stress]"
        scope = f"${feature}"
        return PositionInAsca(alone=f"_ {scope}", beside_context=scope)

    matrix_tail = _matrix_brackets_from_u_colon_target(normalized)
    if matrix_tail is not None:
        scope = f"%{matrix_tail}"
        return PositionInAsca(alone=f"_ {scope}", beside_context=scope)

    return None


def materialize_position_in_asca(
    projection: PositionInAsca,
    *,
    structural_context: str | None,
) -> str:
    """Join structural ``context`` with classified ``in`` scope (ticket 163 ``context in $…``)."""
    if structural_context:
        return f"{structural_context} in {projection.beside_context}"
    return projection.alone


def env_is_projected_position_in_compile_string(raw: str | None) -> bool:
    """True when ``env`` was already projected from classified ``position.in`` (skip ASCA rewrites)."""
    if raw is None or not raw.strip():
        return False
    text = raw.strip()
    if text in ("#<.._>", "<.._>#", _STRESSED_MONOSYLLABLE_ASCA):
        return True
    if _WHOLE_POSITION_IN_STRESS_RE.fullmatch(text):
        return True
    if _WHOLE_POSITION_IN_MATRIX_RE.fullmatch(text):
        return True
    if _POSITION_IN_CONTEXT_STRESS_RE.match(text):
        return True
    return bool(_POSITION_IN_CONTEXT_EDGE_RE.match(text))
