"""Index input-side optionals → ASCA structure optionals (ticket 51).

Taxonomy
--------

| Pattern | Example | Expansion |
|---------|---------|-----------|
| Prefix segment features | ``(V:[+long])θt``, ``(t:[+long])sn`` | ``{V:[+long]}θt`` |
| Prefix class features | ``(C:[+labial])ɡ`` | ``{C:[+labial]}ɡ`` |
| Set suffix optional | ``{s,z}(ʔ)`` | ``{s,sʔ,z,zʔ}`` |
| Literal + set + optional | ``a{i,j}(a)`` | ``a{i,j,ia,ja}`` |
| Set + class optional + tail | ``{r,s}(N)k`` | ``{rk,rNk,sk,sNk}`` |
| Set cross optional | ``{p,t,k}({p,t,k})n`` | cross-product members + suffix |

ASCA env/structure optionals like ``(C,V)`` and ``(C,0)`` are left unchanged.
Phonological modifier optionals (``k(ʷ)``, ``(v)w``) are handled upstream in
``parenthetical.py``.
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import ASCA_ENV_OPTIONAL_RE, IPA_SEGMENT
from conlanger.tools.compile.asca.sets import split_set_members
from conlanger.tools.compile.asca.structures import split_outside_groupers

_CLASS_OR_GROUP_INNER_RE = re.compile(
    r"^(?:"
    r"[A-Z]"  # class letter
    r"|[A-Z]:\[[^\]]+\]"  # class with features
    rf"|{IPA_SEGMENT}\[[^\]]+\]"  # segment feature matrix
    rf"|{IPA_SEGMENT}:\[[^\]]+\]"  # segment with colon features
    r"|\{[^{}]+\}[A-Z$%#]?"  # braced group with optional trailing class/segment
    r"|\{[^{}]+\}"  # braced group
    r"|[A-Z$%#][A-Z$%#0-9,#.]*"  # comma-separated class/group list
    r"|0\s*"  # identity subscript zero
    r")$"
)
_BRACED_GROUP_PREFIX_RE = re.compile(r"^\((\{[^{}]+\}[^)]*)\)(.+)$")
_DEFERRED_STRUCTURAL_OPTIONAL_RE = re.compile(r"^(?:V\[-long\]|\{C,#\}V)$")


def _is_deferred_structural_optional(inner: str) -> bool:
    return bool(_DEFERRED_STRUCTURAL_OPTIONAL_RE.fullmatch(inner.strip()))


def _is_structural_optional_inner(inner: str) -> bool:
    text = inner.strip()
    if not text or ASCA_ENV_OPTIONAL_RE.fullmatch(f"({text})"):
        return False
    if _is_deferred_structural_optional(text):
        return False
    return bool(_CLASS_OR_GROUP_INNER_RE.fullmatch(text))


def _expand_set_cross_optional(left: str, right: str, suffix: str) -> str:
    left_members = split_set_members(left)
    right_members = split_set_members(right)
    expanded: list[str] = []
    seen: set[str] = set()
    for member in left_members:
        for optional in ("", *right_members):
            candidate = f"{member}{optional}{suffix}"
            if candidate not in seen:
                seen.add(candidate)
                expanded.append(candidate)
    return "{" + ",".join(expanded) + "}"


def _expand_set_suffix_optionals(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        left = match.group(1)
        inner = match.group(2)
        suffix = match.group(3) or ""
        if inner.startswith("{"):
            return _expand_set_cross_optional(left, inner[1:-1], suffix)
        if re.fullmatch(r"[A-Z]", inner):
            members = split_set_members(left)
            expanded: list[str] = []
            for member in members:
                expanded.append(f"{member}{suffix}")
                expanded.append(f"{member}{inner}{suffix}")
            return "{" + ",".join(expanded) + "}"
        members = split_set_members(left)
        expanded: list[str] = []
        for member in members:
            expanded.append(member)
            expanded.append(f"{member}{inner}")
        return "{" + ",".join(expanded) + "}" + suffix

    return re.sub(
        r"(?:^|(?<=\s))\{([^{}]+)\}\(([^)]+)\)([\w\[\]:+ʼʷʲʰː\u02b0-\u02ff]*)?",
        repl,
        text,
    )


def _expand_literal_set_optionals(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        literal = match.group(1)
        members = split_set_members(match.group(2))
        optional = match.group(3)
        if optional in members:
            return f"{literal}{{{','.join(members)}}}"
        expanded = list(members)
        for member in members:
            candidate = f"{member}{optional}"
            if candidate not in expanded:
                expanded.append(candidate)
        return f"{literal}{{{','.join(expanded)}}}"

    return re.sub(
        rf"({IPA_SEGMENT})\{{([^{{}}]+)\}}\(([^)]+)\)",
        repl,
        text,
    )


def _expand_prefix_structure_optional(token: str) -> str:
    braced = _BRACED_GROUP_PREFIX_RE.fullmatch(token)
    if braced:
        inner = braced.group(1).strip()
        if _is_deferred_structural_optional(inner):
            return token
        rest = braced.group(2)
        set_match = re.fullmatch(r"\{([^{}]+)\}(.+)", inner)
        if set_match:
            members = split_set_members(set_match.group(1))
            members.append(set_match.group(2))
            return "{" + ",".join(members) + "}" + rest
        if inner.startswith("{") and inner.endswith("}"):
            inner = inner[1:-1]
        return f"{{{inner}}}{rest}"

    match = re.fullmatch(r"\(([^)]+)\)(.+)", token)
    if not match or not _is_structural_optional_inner(match.group(1)):
        return token
    inner = match.group(1).strip()
    rest = match.group(2)
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]
    return f"{{{inner}}}{rest}"


def _expand_bare_tokens(text: str) -> str:
    if "(" not in text:
        return text
    tokens = split_outside_groupers(text)
    return " ".join(_expand_prefix_structure_optional(token) for token in tokens)


def _expand_identity_subscript_optionals(text: str) -> str:
    """Convert ``segment(0)`` identity optionals to ASCA structure ``segment{0}``."""
    return re.sub(r"([^\s(){},]+)\((0)\s*\)", r"\1{\2}", text)


def expand_input_optionals_to_structures(text: str) -> str:
    """Rewrite Index input-side optionals as ASCA structure optionals."""
    if not text or "(" not in text:
        return text
    text = _expand_literal_set_optionals(text)
    text = _expand_set_suffix_optionals(text)
    text = _expand_identity_subscript_optionals(text)
    return _expand_bare_tokens(text)
