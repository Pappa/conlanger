"""Index tilde notation → ASCA alternation sets or output chains."""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import SET_BODY_RE
from conlanger.tools.compile.asca.sets import split_set_members
from conlanger.tools.compile.asca.structures import split_outside_groupers

_SPACED_TILDE_RE = re.compile(r"\s+~\s+")
_PAREN_OPTIONAL_TILDE_RE = re.compile(r"([^\s{}/\[\]()~]+)\(~([^)]+)\)")


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
        for member in split_set_members(content):
            members.extend(_expand_tilde_set_member(member))
        return "{" + ",".join(members) + "}"

    return SET_BODY_RE.sub(repl, text)


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
    tokens = split_outside_groupers(text)
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
    tokens = split_outside_groupers(field)
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


def _append_stage_segments(stages: list[str], stage: str) -> None:
    if " > " in stage:
        parts = [part.strip() for part in stage.split(" > ") if part.strip()]
        if len(parts) >= 2:
            stages.extend(parts)
            return
    stages.append(stage)


def normalize_corpus_rule_tilde_fields(rule: dict[str, str]) -> dict[str, str]:
    """Normalize per-stage tilde notation before chain expansion."""
    result = dict(rule)
    stages = list(result.get("stages") or [])
    if not stages:
        return result
    normalized: list[str] = []
    for index, stage in enumerate(stages):
        if "~" in stage:
            if index == len(stages) - 1:
                stage = _expand_output_tilde_field(stage)
            else:
                stage = expand_index_tilde_notation(stage)
        _append_stage_segments(normalized, stage)
    result["stages"] = normalized
    return result
