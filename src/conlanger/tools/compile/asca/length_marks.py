"""Index length marks → ASCA ``:[+long]`` feature notation.

Transforms (compile layer only; index ``raw`` unchanged per ADR-0010):

- ``segmentː`` → ``segment:[+long]`` (suffix length)
- ``{set}ː`` / bare ``ː`` set members → set or ``V:[+long]`` member
- ``Matrix]ː`` → ``Matrix, +long]`` (matrix-suffix length; ticket 79)

Parenthesized optional length ``(ː)`` is handled by
``optional_length.expand_optional_length_in_text()`` before this pass
(tickets 104 / ADR-0015).

Hold-outs (Iroquoian stress meta — defer to ticket 64 follow-ons):

- ``ː2`` / ``1:[+stress] ː2``
- ``Vː:[+stress]`` inside complex stressed sets
"""

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT

_LENGTH = "\u02d0"
_IPA_SEGMENT = IPA_SEGMENT
_GROUPING_LENGTH_RE = re.compile(r"([A-Z])" + re.escape(_LENGTH) + r"(?!:)")
_REF_LENGTH_RE = re.compile(r"(\d)" + re.escape(_LENGTH))
_SEGMENT_LENGTH_RE = re.compile(rf"({_IPA_SEGMENT}){re.escape(_LENGTH)}(?!:)")
_SET_SUFFIX_LENGTH_RE = re.compile(r"\}" + re.escape(_LENGTH))
_DOUBLE_LENGTH_RE = re.compile(r":\[\+long\]" + re.escape(_LENGTH))
_BARE_SET_LENGTH_RE = re.compile(rf"(^|,)\s*{re.escape(_LENGTH)}(?=,|$)")
_POST_MATRIX_LENGTH_RE = re.compile(r"\]" + re.escape(_LENGTH))
_SYLLABLE_LENGTH_RE = re.compile(r"%" + re.escape(_LENGTH))


def _expand_bare_length_in_sets(text: str) -> str:
    if _LENGTH not in text:
        return text

    def repl(match: re.Match[str]) -> str:
        inner = _BARE_SET_LENGTH_RE.sub(r"\1V:[+long]", match.group(1))
        return "{" + inner + "}"

    return re.sub(r"\{([^}]*)\}", repl, text)


def normalize_asca_length_marks(text: str) -> str:
    """Map Index suffix ``ː`` length notation to ASCA ``:[+long]``."""
    if not text or _LENGTH not in text:
        return text
    text = _GROUPING_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _REF_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _SEGMENT_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _SYLLABLE_LENGTH_RE.sub("%:[+long]", text)
    text = _SET_SUFFIX_LENGTH_RE.sub("}:[+long]", text)
    text = _DOUBLE_LENGTH_RE.sub(":[+long]", text)
    text = _POST_MATRIX_LENGTH_RE.sub(", +long]", text)
    text = _expand_bare_length_in_sets(text)
    return text
