"""Index aspiration diacritics that violate ASCA voice prerequisites (ticket 110).

ASCA accepts literal ``ʰ`` (U+02B0) only on voiceless segments. Index rules
often use ``ʰ`` on voiced stops, glides, and sonorants, or on stop+``w`` clusters
where the aspiration attaches to the whole cluster.

Transforms (compile layer only; index ``raw`` unchanged per ADR-0010):

| Pattern | Example | Expansion |
|---------|---------|-----------|
| Voiced / sonorant + ``ʰ`` | ``jʰ``, ``bʰ``, ``lʰ``, ``rʰ`` | ``segment:[+spread,+voice]`` |
| Modulated voiced aspirate | ``ɡʲʰ``, ``gʷʰ``, ``ɢʷʰ`` | ``segment:[+spread,+voice]`` |
| Voiceless stop + ``w`` + ``ʰ`` | ``pwʰ``, ``twʰ`` | ``stopʷʰ`` |
| Voiced stop + ``w`` + ``ʰ`` | ``bwʰ`` | ``stopw:[+spread,+voice]`` |

Literal ``tʰ``, ``pʰ``, ``cʰ``, etc. on voiceless segments are left unchanged
(ticket 50 policy). Input lengthening ``pː`` → ``p:[+long]`` remains in
``length_marks``.
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT
from conlanger.utils.features import apply_features_to_token

_ASPIRATED = "\u02b0"
_BREATHY_FEATURES = ("+spread", "+voice")
_VOICELESS_ONSETS = frozenset("ptckqfstxsθʈʂʃçɕχʔhɸ")
_IPA_ASPIRATED_SEGMENT_RE = re.compile(
    rf"({IPA_SEGMENT}){re.escape(_ASPIRATED)}(?![+:\w])"
)


def _leading_letter(segment: str) -> str:
    match = re.match(
        r"[a-zA-Z\u00C0-\u024F\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]",
        segment,
    )
    return match.group(0) if match else ""


def _is_voiceless_onset(segment: str) -> bool:
    return _leading_letter(segment) in _VOICELESS_ONSETS


def _expand_stop_glide_aspiration(segment: str) -> str | None:
    if not segment.endswith("w") or len(segment) < 2:
        return None
    base = segment[:-1]
    if _is_voiceless_onset(base):
        return f"{base}\u02b7{_ASPIRATED}"
    return apply_features_to_token(segment, _BREATHY_FEATURES)


def _expand_voiced_aspiration(segment: str) -> str:
    stop_glide = _expand_stop_glide_aspiration(segment)
    if stop_glide is not None:
        return stop_glide
    if _is_voiceless_onset(segment):
        return f"{segment}{_ASPIRATED}"
    return apply_features_to_token(segment, _BREATHY_FEATURES)


def _rewrite_outside_brackets(text: str) -> str:
    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
            continue
        parts.append(
            _IPA_ASPIRATED_SEGMENT_RE.sub(
                lambda match: _expand_voiced_aspiration(match.group(1)),
                segment,
            )
        )
    return "".join(parts)


def normalize_asca_voice_prerequisite_diacritics(text: str) -> str:
    """Rewrite IPA ``ʰ`` that violates ASCA voice prerequisites."""
    if not text or _ASPIRATED not in text:
        return text
    return _rewrite_outside_brackets(text)


__all__ = ["normalize_asca_voice_prerequisite_diacritics"]
