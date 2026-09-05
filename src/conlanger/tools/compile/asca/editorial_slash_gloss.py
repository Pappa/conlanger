"""Index editorial slash glosses and prose residue in compile fields (ticket 115).

Transforms (compile layer only; index ``raw`` unchanged per ADR-0010):

| Pattern | Example | Expansion |
|---------|---------|-----------|
| Set vowel alternation | ``{a/e}``, ``{o,u/y}`` | ``{a,e}``, ``{o,u,y}`` |
| Editorial phoneme slash | ``/j/``, ``/ts/?``, ``/i/`` | ``j``, ``ts?``, ``i`` |
| Unclosed paren prose tail | ``V_ (if /j/ resulted…`` | ``V_`` (prose peeled) |
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import SET_BODY_RE
from conlanger.tools.compile.asca.sets import split_set_members
from conlanger.utils.gloss import extract_trailing_paren_glosses_from_field

_VOWEL_ALTERNATION_MEMBER_RE = re.compile(
    r"^[a-zA-Z\u0250-\u02AF]+(?:/[a-zA-Z\u0250-\u02AF]+)+$"
)
_EDITORIAL_SLASH_GLOSS_RE = re.compile(r"/([^/\s\[\]{}]{1,6})/\??")
_EDITORIAL_SLASH_PAREN_RE = re.compile(r"\([^)]*/[^/]+/[^)]*\)")


def expand_set_vowel_alternation_slashes(text: str) -> str:
    """Expand Index ``{a/e}`` vowel alternation slashes to ASCA set commas."""

    def repl(match: re.Match[str]) -> str:
        members: list[str] = []
        for member in split_set_members(match.group(1)):
            if _VOWEL_ALTERNATION_MEMBER_RE.fullmatch(member):
                members.extend(member.split("/"))
            else:
                members.append(member)
        return "{" + ",".join(members) + "}"

    return SET_BODY_RE.sub(repl, text)


def strip_editorial_slash_glosses(text: str) -> str:
    """Strip Index editorial ``/phoneme/`` gloss slashes, keeping the segment."""
    if "/" not in text:
        return text
    text = _EDITORIAL_SLASH_PAREN_RE.sub("", text)
    return _EDITORIAL_SLASH_GLOSS_RE.sub(r"\1", text).rstrip()


def peel_unclosed_paren_prose(text: str) -> str:
    """Peel unclosed trailing parenthetical prose glosses from a compile field."""
    if "(" not in text:
        return text
    cleaned, _captures = extract_trailing_paren_glosses_from_field(
        text, include_unclosed=True
    )
    return cleaned


def normalize_editorial_slash_gloss_residue(text: str) -> str:
    """Normalize editorial slash glosses and prose residue toward ASCA-valid fields."""
    if not text:
        return text
    text = expand_set_vowel_alternation_slashes(text)
    text = strip_editorial_slash_glosses(text)
    text = peel_unclosed_paren_prose(text)
    return text.rstrip()


__all__ = [
    "expand_set_vowel_alternation_slashes",
    "normalize_editorial_slash_gloss_residue",
    "peel_unclosed_paren_prose",
    "strip_editorial_slash_glosses",
]
