"""Index bare Khoisan click glyphs → ASCA inventory clusters (ticket 136).

Index uses bare click letters (``!`` / ``ǃ`` / ``ǀ`` / ``ǁ`` / ``ǂ`` / ``ʘ``).
ASCA accepts clicks only with an explicit rear onset (``kǃ``, ``ɡǂ``, …) or
``[+click]``. See ``.scratch/rule-index/research/asca-khoisan-click-representation.md``.
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import SET_BODY_RE
from conlanger.utils.bracket_scanner import is_square_bracket_wrapped

_CLICK = r"[!ǃǀǁǂʘ]"
_REAR_ONSET = r"[kgNKŋɡq]"
_IPA_MODIFIER = r"[\u02B0-\u02B8\u02BC\u02D1\u02E4\u0300-\u036F]"
_CLICK_TAIL = rf"(?:{_IPA_MODIFIER}|x|n|ˀ|ʼ)*"

_DOUBLE_BANG_RE = re.compile(r"!!")
_CLICK_VOICED_REAR_SUFFIX_RE = re.compile(
    rf"(?<![kgNKŋɡq])({_CLICK})({_CLICK_TAIL})([ɡg])(?![+:\w])"
)
_BARE_CLICK_RE = re.compile(rf"(?<![kgNKŋɡq])({_CLICK})({_CLICK_TAIL})(?![+:\[])")
_CLUSTER_GLOTTAL_RE = re.compile(rf"(({_REAR_ONSET})({_CLICK})({_CLICK_TAIL}))ˀ")


def _expand_double_bang(text: str) -> str:
    return _DOUBLE_BANG_RE.sub("! !", text)


def _reverse_click_voiced_rear_suffix(text: str) -> str:
    return _CLICK_VOICED_REAR_SUFFIX_RE.sub(r"\3\1\2", text)


def _prefix_default_velar_onset(text: str) -> str:
    return _BARE_CLICK_RE.sub(r"k\1\2", text)


def _rewrite_cluster_glottal_diacritic(text: str) -> str:
    return _CLUSTER_GLOTTAL_RE.sub(r"\1:[+cg]", text)


def _rewrite_clicks_in_segment(text: str) -> str:
    text = _expand_double_bang(text)
    text = _reverse_click_voiced_rear_suffix(text)
    text = _prefix_default_velar_onset(text)
    return _rewrite_cluster_glottal_diacritic(text)


def _rewrite_sets(text: str) -> str:
    def expand_set(match: re.Match[str]) -> str:
        body = match.group(1)
        expanded = ",".join(
            _rewrite_clicks_in_segment(member.strip()) if member.strip() else member
            for member in body.split(",")
        )
        return "{" + expanded + "}"

    return SET_BODY_RE.sub(expand_set, text)


def _rewrite_outside_feature_brackets(text: str) -> str:
    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if is_square_bracket_wrapped(segment):
            parts.append(segment)
            continue
        rewritten = _rewrite_sets(segment)
        parts.append(_rewrite_clicks_in_segment(rewritten))
    return "".join(parts)


def normalize_asca_index_click_segments(text: str) -> str:
    """Rewrite Index bare click notation to ASCA-legal click clusters."""
    if not text:
        return text
    if not any(ch in text for ch in "!ǃǀǁǂʘ"):
        return text
    return _rewrite_outside_feature_brackets(text)


__all__ = ["normalize_asca_index_click_segments"]
