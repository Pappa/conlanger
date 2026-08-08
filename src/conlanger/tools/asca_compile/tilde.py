"""Index tilde notation → ASCA alternation sets or output chains."""

from __future__ import annotations

import re

_SPACED_TILDE_RE = re.compile(r"\s+~\s+")
_PAREN_OPTIONAL_TILDE_RE = re.compile(r"([^\s{}/\[\]()~]+)\(~([^)]+)\)")
_SET_RE = re.compile(r"\{([^{}]*)\}")


def _split_outside_groupers(text: str, sep: str = " ") -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth_brace = 0
    depth_paren = 0
    depth_bracket = 0
    for ch in text:
        if ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace -= 1
        elif ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]":
            depth_bracket -= 1
        if ch == sep and depth_brace == 0 and depth_paren == 0 and depth_bracket == 0:
            if current:
                parts.append("".join(current))
                current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return parts


def _split_set_members(content: str) -> list[str]:
    members: list[str] = []
    current: list[str] = []
    depth_paren = 0
    depth_bracket = 0
    for ch in content:
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]":
            depth_bracket -= 1
        if ch == "," and depth_paren == 0 and depth_bracket == 0:
            members.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        members.append(tail)
    return members


def _expand_tilde_set_member(member: str) -> list[str]:
    token = member.strip()
    token = token.removeprefix("~")
    if "~" not in token:
        return [token] if token else []
    return [part for part in token.split("~") if part]


def _expand_sets_with_tilde(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        content = match.group(1)
        if "~" not in content:
            return match.group(0)
        members: list[str] = []
        for member in _split_set_members(content):
            members.extend(_expand_tilde_set_member(member))
        return "{" + ",".join(members) + "}"

    return _SET_RE.sub(repl, text)


def _expand_paren_optional_tilde(text: str) -> str:
    if "~" not in text or "(" not in text:
        return text
    return _PAREN_OPTIONAL_TILDE_RE.sub(r"{\1,\2}", text)


def _expand_tilde_in_token(token: str) -> str:
    if "~" not in token:
        return token
    parts = [part for part in token.split("~") if part]
    if len(parts) >= 2:
        return "{" + ",".join(parts) + "}"
    return token


def _expand_tilde_tokens(text: str) -> str:
    if "~" not in text:
        return text
    tokens = _split_outside_groupers(text)
    return " ".join(_expand_tilde_in_token(token) for token in tokens)


def _is_multigraph_output_chain(parts: list[str]) -> bool:
    """True when a single output token's 3+ tilde segments look like chain glue."""
    if len(parts) < 3:
        return False
    return sum(1 for part in parts if len(part) >= 2) >= 2


def _expand_output_tilde_field(field: str) -> str:
    """Expand output-field tilde; rare multigraph chains become compile output chains."""
    if "~" not in field:
        return field
    field = _SPACED_TILDE_RE.sub("~", field)
    field = _expand_sets_with_tilde(field)
    field = _expand_paren_optional_tilde(field)
    tokens = _split_outside_groupers(field)
    if len(tokens) == 1 and "~" in tokens[0]:
        parts = [part for part in tokens[0].split("~") if part]
        if _is_multigraph_output_chain(parts):
            return " > ".join(parts)
    return _expand_tilde_tokens(field)


def expand_index_tilde_notation(text: str) -> str:
    """Expand Index ``~`` optional/chain notation toward ASCA-valid forms."""
    if not text or "~" not in text:
        return text
    text = _SPACED_TILDE_RE.sub("~", text)
    text = _expand_sets_with_tilde(text)
    text = _expand_paren_optional_tilde(text)
    return _expand_tilde_tokens(text)


def normalize_corpus_rule_tilde_fields(rule: dict[str, str]) -> dict[str, str]:
    """Normalize ``input`` / ``output`` tilde notation before chain expansion."""
    result = dict(rule)
    if "input" in result and "~" in result["input"]:
        result["input"] = expand_index_tilde_notation(result["input"])
    if "output" in result and "~" in result["output"]:
        result["output"] = _expand_output_tilde_field(result["output"])
    return result
