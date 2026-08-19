"""Index breve vowel notation → ASCA ``:[-long]`` or bare segment."""

from __future__ import annotations

import unicodedata

_BREVE = "\u0306"
_PRECOMPOSED_BREVE: dict[str, str] = {
    "\u0103": "a:[-long]",  # ă
    "\u014f": "o:[-long]",  # ŏ
    "\u016d": "u:[-long]",  # ŭ
}
_COMBINING_BREVE: dict[str, str] = {
    "j\u0306": "j",
    "\u0268\u0306": "\u0268",  # ɨ̆ → ɨ
    "\u0259\u0306": "\u0259:[-long]",  # ə̆ → ə:[-long]
    "\u00e6\u0306": "\u00e6:[-long]",  # æ̆ → æ:[-long]
    "a\u0306": "a:[-long]",
    "o\u0306": "o:[-long]",
    "u\u0306": "u:[-long]",
}


def normalize_asca_breve_marks(text: str) -> str:
    """Map Index breve vowels to ASCA ``:[-long]`` or bare segments (Tai glides)."""
    if not text:
        return text
    if _BREVE not in text and not any(char in text for char in _PRECOMPOSED_BREVE):
        return text

    for source, target in _PRECOMPOSED_BREVE.items():
        text = text.replace(source, target)

    text = unicodedata.normalize("NFD", text)
    for source, target in _COMBINING_BREVE.items():
        text = text.replace(source, target)
    text = text.replace(_BREVE, "")
    return unicodedata.normalize("NFC", text)
