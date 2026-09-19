"""Index segment-level combining diacritics → ASCA segments (ticket 135)."""

from __future__ import annotations

import re

from conlanger.tools.compile.asca.subscript_references import (
    _SUBSCRIPT_TO_ASCII,
)
from conlanger.utils.bracket_scanner import is_square_bracket_wrapped

_RING_ABOVE = "\u030a"
_NO_AUDIBLE_RELEASE = "\u031a"
_LAMINAL = "\u033b"
_APICAL = "\u033a"
_LINGUOLABIAL = "\u033c"
_CIRCUMFLEX = "\u0302"
_GRAVE = "\u0300"

# Longest-first literal replacements (NFC precomposed or base+mark sequences).
_LITERAL_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("r̝̊", "ʂ"),
    ("r̝", "ʐ"),
    ("s̻", "s:[+dist,+cor]"),
    ("s̺", "s:[+dist,+cor,+ant]"),
    ("ts̻", "ts"),
    ("ts̺", "ts"),
    ("r̀", "r"),
    ("ĩ", "i\u0303"),
    ("Ạ", "a"),
    ("ɿ", "ɻ"),
    ("ʅ", "ʂ"),
    ("ḛ", "e"),
)

_PROSE_CLASS_SUBSCRIPT_RE = re.compile(r"([A-Z])([₀₁₂₃₄₅₆₇₈₉])")
_ACUTE_R_NOT_PROTO_RE = re.compile(r"(?<!\*)\u0155")


def _rewrite_prose_class_subscripts(text: str) -> str:
    if "//" not in text:
        return text
    head, tail = text.split("//", 1)
    tail = _PROSE_CLASS_SUBSCRIPT_RE.sub(
        lambda match: (
            f"{match.group(1)}={int(match.group(2).translate(_SUBSCRIPT_TO_ASCII))}"
        ),
        tail,
    )
    return f"{head}//{tail}"


def _rewrite_combining_marks(text: str) -> str:
    for source, target in _LITERAL_REPLACEMENTS:
        text = text.replace(source, target)
    text = _ACUTE_R_NOT_PROTO_RE.sub("r", text)

    if not any(
        mark in text
        for mark in (
            _RING_ABOVE,
            _NO_AUDIBLE_RELEASE,
            _LAMINAL,
            _APICAL,
            _LINGUOLABIAL,
            _CIRCUMFLEX,
            _GRAVE,
        )
    ):
        return text

    # Voiceless ring (U+030A) on non-IPA class segments → U+0325 (IPA voiceless).
    text = text.replace(f"j{_RING_ABOVE}", "j\u0325")
    text = text.replace(f"n{_RING_ABOVE}", "n\u0325")
    text = text.replace(f"r{_RING_ABOVE}", "r\u0325")
    text = text.replace(f"w{_RING_ABOVE}", "w\u0325")

    # No audible release on stops (Latin and IPA).
    for letter in "bcdgkptɡ":
        text = text.replace(f"{letter}{_NO_AUDIBLE_RELEASE}", f"{letter}:[-cont]")

    # Basque / Index laminal-apical on other segments (after s̻/s̺ literals).
    text = text.replace(f"t{_LINGUOLABIAL}", "t:[+dist,+cor,+ant]")
    text = text.replace(f"n{_LINGUOLABIAL}", "n:[+dist,+cor,+ant]")

    # Muskogean / Tai raised vowel env (V̂).
    text = text.replace(f"V{_CIRCUMFLEX}", "V:[+long]")

    return text


def _rewrite_outside_brackets(text: str) -> str:
    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if is_square_bracket_wrapped(segment):
            parts.append(segment)
            continue
        segment = _rewrite_combining_marks(segment)
        segment = _rewrite_prose_class_subscripts(segment)
        parts.append(segment)
    return "".join(parts)


def normalize_index_segment_diacritics(text: str) -> str:
    """Map Index segment diacritics to ASCA-accepted segments and features."""
    if not text:
        return text
    return _rewrite_outside_brackets(text)


__all__ = ["normalize_index_segment_diacritics"]
