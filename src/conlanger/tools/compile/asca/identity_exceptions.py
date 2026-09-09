"""Index identity exceptions ``! Host = seg`` → ASCA compile rewrite (ticket 128)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from conlanger.tools.compile.asca.group_mappings import (
    apply_asca_group_mappings_to_string,
    expand_grouping_letter,
)
from conlanger.tools.compile.asca.host_bracket_matrices import (
    _SINGLE_HOST_BRACKET_RE,
    normalize_asca_host_bracket_matrices,
)
from conlanger.tools.compile.asca.structures import split_outside_groupers

_IDENTITY_EXCEPTION_HOST_RE = re.compile(
    r"^\s*(?P<host>(?:\[[^\]]+\]|[A-Z](?::\[[^\]]+\])?))\s*=\s*(?P<rest>.+?)\s*$"
)
_CLASS_HOST_PREFIX_RE = re.compile(r"^(?P<host>[A-Z](?::\[[^\]]+\])?)(?P<suffix>.*)$")
_MATRIX_HOST_RE = re.compile(r"^\[[^\]]+\]$")


@dataclass(frozen=True)
class IdentityExceptionBinding:
    """Deferred Family B input narrowing after bracket-matrix normalization."""

    host_raw: str
    host_expanded: str
    rhs: str


def _split_outside_brackets(text: str, sep: str = ",") -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in text:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == sep and depth == 0:
            if current:
                parts.append("".join(current).strip())
                current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return parts


def _parse_identity_rhs(rest: str) -> str:
    text = rest.strip()
    if text.startswith("{"):
        depth = 0
        for index, ch in enumerate(text):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[: index + 1]
    if "," in text:
        return text.split(",", 1)[0].strip()
    return text


def parse_index_identity_exception(exception: str | None) -> tuple[str, str] | None:
    """Parse ``Host = RHS`` from a raw Index exception field."""
    if not exception:
        return None
    match = _IDENTITY_EXCEPTION_HOST_RE.match(exception.strip())
    if match is None:
        return None
    host = match.group("host").strip()
    rhs = _parse_identity_rhs(match.group("rest"))
    if not host or not rhs:
        return None
    return host, rhs


def _expand_identity_host(host: str, group_mappings: dict[str, str]) -> str:
    if _MATRIX_HOST_RE.fullmatch(host):
        return host
    if len(host) == 1 and host.isupper():
        return expand_grouping_letter(host, group_mappings, labial=False)
    return apply_asca_group_mappings_to_string(host, group_mappings)


def _expand_identity_rhs(rhs: str, group_mappings: dict[str, str]) -> str:
    return apply_asca_group_mappings_to_string(rhs, group_mappings)


def _hosts_match(
    host_raw: str,
    host_expanded: str,
    token_host: str,
    group_mappings: dict[str, str],
) -> bool:
    if host_raw == token_host or host_expanded == token_host:
        return True
    if len(token_host) == 1 and token_host.isupper():
        expanded = expand_grouping_letter(token_host, group_mappings, labial=False)
        return host_raw == token_host or host_expanded == expanded
    return False


def _normalize_slot_host(slot: str) -> str | None:
    text = slot.strip()
    if text.startswith("[") and "]" in text:
        return text[: text.index("]") + 1]
    inner = text[1:-1] if text.startswith("{") and text.endswith("}") else text
    for part in _split_outside_brackets(inner):
        candidate = part.strip()
        if candidate.startswith("["):
            return candidate
        if re.fullmatch(r"[A-Z]:\[[^\]]+\]", candidate):
            return candidate
    return None


def _token_host_suffix_pairs(token: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    class_match = _CLASS_HOST_PREFIX_RE.match(token)
    if class_match is not None and not token.startswith("{"):
        pairs.append((class_match.group("host"), class_match.group("suffix")))
    if "_" in token:
        slot = token.rsplit("_", 1)[-1]
        slot_host = _normalize_slot_host(slot)
        if slot_host is not None:
            pairs.append((slot_host, f"_{slot}"))
    return pairs


def _compile_family_a_exception(
    env: str,
    host_raw: str,
    host_expanded: str,
    rhs: str,
    group_mappings: dict[str, str],
) -> str | None:
    for token in split_outside_groupers(env):
        for token_host, suffix in _token_host_suffix_pairs(token):
            if _hosts_match(host_raw, host_expanded, token_host, group_mappings):
                return f"{rhs}{suffix}"
    return None


def _input_needs_bracket_normalization(input_text: str) -> bool:
    return bool(_SINGLE_HOST_BRACKET_RE.fullmatch(input_text.strip()))


def _input_token_matches_host(
    token: str,
    host_raw: str,
    host_expanded: str,
    group_mappings: dict[str, str],
) -> bool:
    if _hosts_match(host_raw, host_expanded, token, group_mappings):
        return True
    if len(host_raw) == 1 and host_raw.isupper() and token.startswith(host_raw):
        return "[" in token or ":" in token
    return False


def _narrow_input_token(
    input_text: str,
    host_raw: str,
    host_expanded: str,
    rhs: str,
    group_mappings: dict[str, str],
) -> str | None:
    text = input_text.strip()
    if text.startswith("{") and text.endswith("}"):
        return f"{{{text[1:-1]},-{rhs}}}"
    if _input_token_matches_host(text, host_raw, host_expanded, group_mappings):
        normalized = normalize_asca_host_bracket_matrices(text)
        return f"{{{normalized},-{rhs}}}"
    return None


def apply_identity_exception_input_narrowing(
    input_text: str,
    binding: IdentityExceptionBinding,
) -> str:
    """Apply deferred Family B input narrowing after bracket-matrix normalization."""
    narrowed = _narrow_input_token(
        input_text,
        binding.host_raw,
        binding.host_expanded,
        binding.rhs,
        {},
    )
    if narrowed is None:
        return input_text
    return narrowed


def resolve_index_identity_exceptions(
    inp: str,
    output: str,
    env: str | None,
    exception: str | None,
    *,
    exception_raw: str | None,
    group_mappings: dict[str, str],
) -> tuple[str, str, str | None, str | None, IdentityExceptionBinding | None]:
    """Rewrite identity exceptions before cross-field subscript expansion."""
    parsed = parse_index_identity_exception(exception_raw)
    if parsed is None:
        return inp, output, env, exception, None

    host_raw, rhs_raw = parsed
    host_expanded = _expand_identity_host(host_raw, group_mappings)
    rhs = _expand_identity_rhs(rhs_raw, group_mappings)

    if env is not None:
        family_a = _compile_family_a_exception(
            env,
            host_raw,
            host_expanded,
            rhs,
            group_mappings,
        )
        if family_a is not None:
            return inp, output, env, family_a, None

    if _input_needs_bracket_normalization(inp):
        return (
            inp,
            output,
            env,
            None,
            IdentityExceptionBinding(
                host_raw=host_raw,
                host_expanded=host_expanded,
                rhs=rhs,
            ),
        )

    narrowed = _narrow_input_token(inp, host_raw, host_expanded, rhs, group_mappings)
    if narrowed is not None:
        return narrowed, output, env, None, None

    return inp, output, env, exception, None
