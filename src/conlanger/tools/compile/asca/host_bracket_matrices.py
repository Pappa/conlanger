"""Rewrite Index host+bracket matrices to ASCA colon form (ticket 121)."""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT

_SINGLE_HOST_BRACKET_RE = re.compile(rf"^((?:[A-Z]|{IPA_SEGMENT}))\[([^\]]+)\]$")
_CLASS_HOST_BRACKET_RE = re.compile(
    r"(?<![aeiou]C)(?P<host>[A-Z])\[(?P<matrix>[^\]]+)\]"
)
_IPA_HOST_BRACKET_RE = re.compile(rf"(?P<host>{IPA_SEGMENT})\[(?P<matrix>[^\]]+)\]")


def host_bracket_matrix_to_colon(text: str) -> str:
    """Rewrite a single host+bracket token ``V[-long]`` to ``V:[-long]``."""
    match = _SINGLE_HOST_BRACKET_RE.fullmatch(text.strip())
    if match is None:
        return text
    return f"{match.group(1)}:[{match.group(2)}]"


def normalize_asca_host_bracket_matrices(text: str) -> str:
    """Rewrite host+bracket matrices in I/O compile fields to colon form."""
    if not text or "[" not in text:
        return text

    def class_repl(match: re.Match[str]) -> str:
        return f"{match.group('host')}:[{match.group('matrix')}]"

    def ipa_repl(match: re.Match[str]) -> str:
        host = match.group("host")
        if re.search(r"[A-Z]", host):
            return match.group(0)
        return f"{host}:[{match.group('matrix')}]"

    text = _CLASS_HOST_BRACKET_RE.sub(class_repl, text)
    return _IPA_HOST_BRACKET_RE.sub(ipa_repl, text)
