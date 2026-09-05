"""Index parenthetical segment notation → ASCA alternation sets.

Taxonomy (ticket 48)
--------------------

| Pattern | Example | Compile expansion |
|---------|---------|-------------------|
| Optional modifier suffix | ``ɡ(ʷ)``, ``k(ʼ)`` | ``{ɡ,ɡʷ}``, ``{k:[+cg],k}`` |
| Comma-separated modifiers | ``ɸ(ʼ,ʰ)`` | ``{ɸ,ɸʰ,ɸ:[+cg],ɸʰ:[+cg]}`` |
| Glottal modifier | ``m(ˀ)``, ``(ˀ)t`` | ``{m,mˀ}``, ``{ʔt,t}`` |
| Embedded env suffix | ``_k(ʷ)``, ``_V:[+front]k(ʷ)`` | ``_{k,kʷ}``, ``_V:[+front]{k,kʷ}`` |
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

from conlanger.tools.compile.asca._patterns import (
    ASCA_ENV_OPTIONAL_RE,
    IPA_SEGMENT,
    SET_BODY_RE,
)
from conlanger.tools.compile.asca.ejectives import _add_cg_feature
from conlanger.tools.compile.asca.sets import split_set_members
from conlanger.tools.compile.asca.structures import split_outside_groupers
from conlanger.utils.gloss import paren_inner_is_gloss

_CLASS_LETTER_RE = re.compile(r"^[A-Z$%#][A-Z$%#0-9]*$")
_CHAIN_ALTERNATE_RE = re.compile(r"\s*\(>\s*[^)]*\)\s*")
_UNCERTAINTY_PAREN_RE = re.compile(r"\(\?\)")
_EJECTIVE = "\u02bc"
_ROUND = "\u02b7"
_GLOTTAL = "\u02c0"
_PHONOLOGICAL_MODIFIER_RE = re.compile(
    r"^[\u0250-\u02AFa-zA-Z0-9:+ʼʷʲʰˀː\u02b0-\u02b8\u02bc\u02c0\u02d1\u02e4\u0300-\u036f\u02b7w]+$"
)
_EMBEDDED_MODIFIER_RE = re.compile(
    rf"({IPA_SEGMENT})(:\[[^\]]+\])?\(([^)]+)\)"
)


def _add_round_feature(features: str) -> str:
    if "+round" in features or "-round" in features:
        return features
    return f"{features},+round" if features else "+round"


def _normalize_optional_inner(inner: str) -> str:
    return inner.replace("?", "").strip()


def _split_modifier_inners(inner: str) -> list[str]:
    if "," not in inner:
        return [_normalize_optional_inner(inner)]
    return [
        _normalize_optional_inner(part)
        for part in inner.split(",")
        if _normalize_optional_inner(part)
    ]


def _is_single_phonological_modifier(text: str) -> bool:
    if not text or text == "?":
        return False
    if re.search(r"\s", text):
        return False
    if len(text) > 4 and paren_inner_is_gloss(text):
        return False
    return bool(_PHONOLOGICAL_MODIFIER_RE.fullmatch(text))


def _is_modifier_token(text: str) -> bool:
    if _CLASS_LETTER_RE.fullmatch(text):
        return False
    return _is_single_phonological_modifier(text)


def _is_phonological_optional_inner(inner: str) -> bool:
    modifiers = _split_modifier_inners(inner)
    if not modifiers:
        return False
    if len(modifiers) > 1:
        return all(_is_modifier_token(modifier) for modifier in modifiers)
    return _is_single_phonological_modifier(modifiers[0])


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

    if modifier in {_GLOTTAL, "ˀ"}:
        return [
            f"{base}{feature_suffix}{suffix}",
            f"{base}{_GLOTTAL}{feature_suffix}{suffix}",
        ]

    if features:
        return [
            f"{base}{feature_suffix}{suffix}",
            f"{base}{modifier}{feature_suffix}{suffix}",
        ]

    return [f"{base}{suffix}", f"{base}{modifier}{suffix}"]


def _parse_segment_for_modifier(
    segment: str,
    *,
    suffix: str = "",
) -> tuple[str, str | None, str] | None:
    match = re.match(rf"^({IPA_SEGMENT})(:\[[^\]]+\])?(.*)$", segment)
    if not match:
        return None
    tail = match.group(3)
    if suffix and not tail.endswith(suffix):
        return None
    extra_tail = tail[: -len(suffix)] if suffix else tail
    return match.group(1), match.group(2), extra_tail


def _expand_modifier_variants(
    base: str,
    features: str | None,
    inner: str,
    *,
    suffix: str = "",
) -> list[str]:
    modifiers = _split_modifier_inners(inner)
    if not modifiers:
        return [f"{base}{(features or '')}{suffix}"]
    if len(modifiers) == 1:
        return _apply_optional_modifier(
            base,
            features,
            modifiers[0],
            suffix=suffix,
        )

    variants = [f"{base}{(features or '')}{suffix}"]
    for modifier in modifiers:
        expanded: list[str] = []
        for variant in variants:
            expanded.append(variant)
            parsed = _parse_segment_for_modifier(variant, suffix=suffix)
            if parsed is None:
                continue
            segment_base, segment_features, extra_tail = parsed
            applied = _apply_optional_modifier(
                segment_base,
                segment_features,
                modifier,
                suffix=extra_tail + suffix,
            )
            for candidate in applied:
                if candidate != variant:
                    expanded.append(candidate)
                    break
        variants = list(dict.fromkeys(expanded))
    return variants


def _is_optional_modifier_tail(text: str) -> bool:
    if not text:
        return False
    return text[0] not in " _{,/<>#%$"


def _unwrap_alternate_variants(token: str) -> list[str] | None:
    stripped = token.strip()
    if not stripped.startswith("{") or not stripped.endswith("}"):
        return None
    inner = stripped[1:-1]
    if "{" in inner or "}" in inner:
        return None
    members = split_set_members(inner)
    if len(members) < 2:
        return None
    return members


def _expand_embedded_optional_modifiers(text: str) -> str:
    if "(" not in text:
        return text

    def repl(match: re.Match[str]) -> str:
        base = match.group(1)
        features = match.group(2)
        inner = match.group(3)
        if not _is_phonological_optional_inner(inner):
            return match.group(0)
        suffix_after = text[match.end() :]
        if _is_optional_modifier_tail(suffix_after):
            return match.group(0)
        prefix = text[: match.start()]
        if prefix.endswith(":") and features is None:
            return match.group(0)
        variants = _expand_modifier_variants(
            base,
            features,
            inner,
        )
        return _wrap_alternates(variants)

    previous = text
    for _ in range(8):
        nxt = _EMBEDDED_MODIFIER_RE.sub(repl, previous)
        if nxt == previous:
            return nxt
        previous = nxt
    return previous


def _expand_optional_in_token(token: str) -> list[str]:
    if ASCA_ENV_OPTIONAL_RE.fullmatch(token):
        return [token]

    token = _expand_embedded_optional_modifiers(token)
    unwrapped = _unwrap_alternate_variants(token)
    if unwrapped is not None:
        return unwrapped

    whole_paren = re.fullmatch(r"\(([^)]+)\)$", token)
    if whole_paren and _is_phonological_optional_inner(whole_paren.group(1)):
        return [_normalize_optional_inner(whole_paren.group(1))]

    prefix_match = re.fullmatch(r"\(([^)]+)\)(.+)", token)
    if prefix_match and _is_phonological_optional_inner(prefix_match.group(1)):
        prefix = _normalize_optional_inner(prefix_match.group(1))
        rest = prefix_match.group(2)
        if prefix in {_GLOTTAL, "ˀ"}:
            return [f"ʔ{rest}", rest]
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
        return _expand_modifier_variants(
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
        for member in split_set_members(match.group(1)):
            members.extend(_expand_set_member(member))
        return "{" + ",".join(members) + "}"

    return SET_BODY_RE.sub(repl, text)


def _wrap_alternates(variants: list[str]) -> str:
    if len(variants) == 1:
        return variants[0]
    return "{" + ",".join(variants) + "}"


def _expand_bare_tokens(text: str) -> str:
    if "(" not in text:
        return text

    tokens = split_outside_groupers(text)
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
