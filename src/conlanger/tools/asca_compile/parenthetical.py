"""Index parenthetical segment notation → ASCA alternation sets.

Taxonomy (ticket 48)
--------------------

| Pattern | Example | Compile expansion |
|---------|---------|-------------------|
| Optional modifier suffix | ``ɡ(ʷ)``, ``k(ʼ)`` | ``{ɡ,ɡʷ}``, ``{k:[+cg],k}`` |
| Optional modifier on features | ``e:[+long](ʲ)`` | ``{e:[+long],eʲ:[+long]}`` |
| Optional infix / prefix | ``o(ji)``, ``(v)w`` | ``{o,oji}``, ``{vw,w}`` |
| Optional inside set member | ``{(d)l,θ}``, ``{k(ʼ),q}`` | flatten member alternates into the set |
| In-member optional + tail | ``{k(ʷ)es,keθ}`` | ``{kʷes,kes,keθ}`` |
| Editorial uncertainty | ``(?)``, ``{ɡ,q}(?)`` | strip |
| Chain alternate gloss | ``(> s:[+long]?)`` | strip |
| ASCA env/structure optionals | ``(C,V)``, ``(C,0)`` | leave unchanged |
"""

from __future__ import annotations

import re

from conlanger.tools.asca_compile._patterns import IPA_SEGMENT
from conlanger.tools.parsers import paren_inner_is_gloss

_SET_RE = re.compile(r"\{([^{}]*)\}")
_CHAIN_ALTERNATE_RE = re.compile(r"\s*\(>\s*[^)]*\)\s*")
_UNCERTAINTY_PAREN_RE = re.compile(r"\(\?\)")
_ASCA_ENV_OPTIONAL_RE = re.compile(r"^\([A-Z$%#][A-Z$%#0-9,.…]*\)$")
_EJECTIVE = "\u02bc"
_ROUND = "\u02b7"
_PHONOLOGICAL_OPTIONAL_INNER_RE = re.compile(
    r"^[\u0250-\u02AFa-zA-Z0-9:+ʼʷʲʰː\u02b0-\u02b8\u02bc\u02d1\u02e4\u0300-\u036f\u02b7w]+$"
)


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


def _add_cg_feature(features: str) -> str:
    if "+cg" in features or "-cg" in features:
        return features
    return f"{features},+cg" if features else "+cg"


def _add_round_feature(features: str) -> str:
    if "+round" in features or "-round" in features:
        return features
    return f"{features},+round" if features else "+round"


def _normalize_optional_inner(inner: str) -> str:
    return inner.replace("?", "").strip()


def _is_phonological_optional_inner(inner: str) -> bool:
    text = _normalize_optional_inner(inner)
    if not text or text == "?":
        return False
    if re.search(r"\s", text):
        return False
    if len(text) > 4 and paren_inner_is_gloss(text):
        return False
    return bool(_PHONOLOGICAL_OPTIONAL_INNER_RE.fullmatch(text))


def _apply_optional_modifier(
    base: str,
    features: str | None,
    inner: str,
    *,
    suffix: str = "",
) -> list[str]:
    modifier = _normalize_optional_inner(inner)
    feature_suffix = features or ""
    feature_body = features[2:-1] if features else None

    if modifier in {_EJECTIVE, "ʼ"}:
        if feature_body is not None:
            with_cg = f"{base}:[{_add_cg_feature(feature_body)}]"
        else:
            with_cg = f"{base}:[+cg]"
        return [f"{with_cg}{suffix}", f"{base}{feature_suffix}{suffix}"]

    if modifier in {_ROUND, "w", "ʷ"}:
        if feature_body is not None:
            with_round = f"{base}:[{_add_round_feature(feature_body)}]"
            return [f"{base}{feature_suffix}{suffix}", f"{with_round}{suffix}"]
        return [f"{base}{suffix}", f"{base}{_ROUND}{suffix}"]

    if features:
        return [
            f"{base}{feature_suffix}{suffix}",
            f"{base}{modifier}{feature_suffix}{suffix}",
        ]

    return [f"{base}{suffix}", f"{base}{modifier}{suffix}"]


def _expand_optional_in_token(token: str) -> list[str]:
    if _ASCA_ENV_OPTIONAL_RE.fullmatch(token):
        return [token]

    prefix_match = re.fullmatch(r"\(([^)]+)\)(.+)", token)
    if prefix_match and _is_phonological_optional_inner(prefix_match.group(1)):
        prefix = _normalize_optional_inner(prefix_match.group(1))
        rest = prefix_match.group(2)
        return [f"{prefix}{rest}", rest]

    match = re.match(
        rf"^({IPA_SEGMENT})(:\[[^\]]+\])?\(([^)]+)\)(.*)$",
        token,
    )
    if match and _is_phonological_optional_inner(match.group(3)):
        base, features, inner, tail = (
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
        )
        return _apply_optional_modifier(
            base,
            features,
            inner,
            suffix=tail,
        )

    return [token]


def _expand_set_member(member: str) -> list[str]:
    return _expand_optional_in_token(member)


def _expand_sets(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        members: list[str] = []
        for member in _split_set_members(match.group(1)):
            members.extend(_expand_set_member(member))
        return "{" + ",".join(members) + "}"

    return _SET_RE.sub(repl, text)


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


def _wrap_alternates(variants: list[str]) -> str:
    if len(variants) == 1:
        return variants[0]
    return "{" + ",".join(variants) + "}"


def _expand_bare_tokens(text: str) -> str:
    if "(" not in text:
        return text

    tokens = _split_outside_groupers(text)
    expanded_tokens: list[str] = []
    for token in tokens:
        variants = _expand_optional_in_token(token)
        expanded_tokens.append(_wrap_alternates(variants))
    return " ".join(expanded_tokens)


def _strip_editorial_parentheticals(text: str) -> str:
    if "(" not in text:
        return text
    text = _CHAIN_ALTERNATE_RE.sub("", text).rstrip()
    text = _UNCERTAINTY_PAREN_RE.sub("", text).rstrip()
    while True:
        match = re.search(r"\(([^()]*)\)\s*$", text)
        if not match:
            break
        inner = match.group(1)
        if not paren_inner_is_gloss(inner) or _is_phonological_optional_inner(inner):
            break
        text = text[: match.start()].rstrip()
    return text


def expand_index_parenthetical_notation(text: str) -> str:
    """Expand Index parenthetical optional notation toward ASCA-valid forms."""
    if not text or "(" not in text:
        return text
    text = _strip_editorial_parentheticals(text)
    if "(" not in text:
        return text
    text = _expand_sets(text)
    return _expand_bare_tokens(text)
