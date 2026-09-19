"""Parse-time normalization for Index prose conditional env phrases (ticket 134)."""

from __future__ import annotations

import re
from typing import Any

from conlanger.tools.ingest.transforms import _append_rule_comment_parts

_BARE_MATRIX_RE = re.compile(r"^\[(?P<inner>[^\]]+)\]$")
_UNSTRESSED_PENULT_RE = re.compile(
    r"^(?:in\s+the\s+)?(?:the\s+)?unstressed\s+penult\s*$",
    re.IGNORECASE,
)
_UTTERANCE_INITIALLY_RE = re.compile(r"^utterance-initially\s*$", re.IGNORECASE)
_BEFORE_MODAL_SUFFIXES_RE = re.compile(r"^before\s+modal\s+suffixes\s*$", re.IGNORECASE)
_SHORT_ONLY_RE = re.compile(r"^short\s+only\s*$", re.IGNORECASE)
_SYLLABLES_WITH_RE = re.compile(r"^syllables\s+with\s+.+$", re.IGNORECASE)
_IF_NOT_STRESSED_RE = re.compile(
    r"^if\s+the\s+\*(?P<seg>\S+)\s+is\s+not\s+stressed\s*$",
    re.IGNORECASE,
)
_IF_IN_SAME_SYLLABLE_RE = re.compile(
    r"^if\s+/?(?P<seg>[^/\s]+)/?\s+is\s+present\s+in\s+the\s+same\s+syllable\s*$",
    re.IGNORECASE,
)
_MATRIX_COMMA_PROSE_RE = re.compile(r"^(\[[^\]]+\]),\s*(?P<prose>.+)$")
_STRESS_USUALLY_WHEN_PREFIX_RE = re.compile(
    r"^\[\+stress\],\s*usually\s+when\s+(?P<env>.+)$",
    re.IGNORECASE,
)
_TRAILING_WHERE_CLAUSE_RE = re.compile(
    r"^(?P<env>.+?),\s*where\s+.+$",
    re.IGNORECASE,
)
_VAGUE_BARE_ENV_RE = re.compile(
    r"^(?:by\s+analogy\s+in\s+some\s+cases|the\s+name\s+of\s+the\s+river|"
    r"a\s+few\s+data\s+sets|something\s+to\s+do\s+with.+)$",
    re.IGNORECASE,
)


def _attach_bare_matrix_to_input_stage(
    stages: list[str], matrix: str
) -> list[str] | None:
    """Merge a standalone feature matrix onto the rule input stage when unambiguous."""
    if not stages:
        return None
    input_stage = stages[0].strip()
    if not input_stage or ":" in input_stage or "[" in input_stage:
        return None
    if " " in input_stage or "{" in input_stage:
        return None
    return [f"{input_stage}:{matrix}", *stages[1:]]


def normalize_prose_conditional_env_field(
    text: str,
) -> tuple[str, list[str], dict[str, Any], str | None]:
    """Normalize prose conditional env; return optional bare matrix for input merge."""
    if not text:
        return text, [], {}, None
    stripped = text.strip()
    flags: dict[str, Any] = {}
    captures: list[str] = []
    input_matrix: str | None = None

    match = _STRESS_USUALLY_WHEN_PREFIX_RE.match(stripped)
    if match:
        captures.append(stripped[: match.start("env")].strip().rstrip(","))
        stripped = match.group("env").strip()
        input_matrix = "[+stress]"

    match = _MATRIX_COMMA_PROSE_RE.match(stripped)
    if match:
        matrix = match.group(1)
        captures.append(match.group("prose").strip())
        stripped = matrix
        if _BARE_MATRIX_RE.fullmatch(matrix):
            input_matrix = input_matrix or matrix

    if _UNSTRESSED_PENULT_RE.match(stripped):
        captures.append(stripped)
        return "%_", captures, flags, input_matrix

    if _UTTERANCE_INITIALLY_RE.match(stripped):
        return "#_", [stripped], flags, input_matrix

    if _BEFORE_MODAL_SUFFIXES_RE.match(stripped):
        return "_$", [stripped], flags, input_matrix

    if _SHORT_ONLY_RE.match(stripped):
        return "_", [stripped], flags, input_matrix

    if _SYLLABLES_WITH_RE.match(stripped):
        return "_", [stripped], flags, input_matrix

    match = _IF_NOT_STRESSED_RE.match(stripped)
    if match:
        seg = match.group("seg")
        captures.append(stripped)
        return f"_ *{seg}[-stress]", captures, flags, input_matrix

    match = _IF_IN_SAME_SYLLABLE_RE.match(stripped)
    if match:
        flags["sporadic"] = True
        return "_", [stripped], flags, input_matrix

    match = _TRAILING_WHERE_CLAUSE_RE.match(stripped)
    if match:
        captures.append(stripped[match.end("env") :].strip().lstrip(","))
        stripped = match.group("env").rstrip()

    if _VAGUE_BARE_ENV_RE.match(stripped):
        flags["sporadic"] = True
        return "_", [stripped], flags, input_matrix

    if _BARE_MATRIX_RE.fullmatch(stripped):
        input_matrix = input_matrix or stripped

    return stripped, captures, flags, input_matrix


def apply_prose_conditional_env_conditions(parts: dict[str, Any]) -> dict[str, Any]:
    """Rewrite Index prose conditional env phrases on ``env`` (``raw`` unchanged)."""
    result: dict[str, Any] = dict(parts)
    env = result.get("env")
    if env:
        normalized, captures, flags, input_matrix = (
            normalize_prose_conditional_env_field(env)
        )
        comment_fragments = list(captures)
        if normalized != env or comment_fragments or flags or input_matrix:
            if normalized:
                result["env"] = normalized
            elif "env" in result:
                del result["env"]
            if input_matrix and result.get("stages"):
                merged = _attach_bare_matrix_to_input_stage(
                    result["stages"], input_matrix
                )
                if merged is not None:
                    result["stages"] = merged
            if flags.get("sporadic"):
                result["sporadic"] = True
            _append_rule_comment_parts(result, comment_fragments)

    exception = result.get("exception")
    if exception:
        exc_norm, exc_caps, exc_flags, _ = normalize_prose_conditional_env_field(
            exception
        )
        if exc_norm != exception or exc_caps or exc_flags:
            if exc_norm:
                result["exception"] = exc_norm
            else:
                del result["exception"]
            if exc_flags.get("sporadic"):
                result["sporadic"] = True
            _append_rule_comment_parts(result, exc_caps)

    return result
