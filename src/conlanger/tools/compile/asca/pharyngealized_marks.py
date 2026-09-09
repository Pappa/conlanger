"""Index pharyngealized ``ˤ`` (U+02E4) → ASCA ``:[-atr,+rtr]`` feature notation."""

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT
from conlanger.utils.features import (
    add_features_to_matrix_body,
    apply_features_to_token,
)

_PHARYNGEALIZED = "\u02e4"
_PHARYNGEAL_FEATURES = ("-atr", "+rtr")
_POST_MATRIX_PHARYNGEALIZED_RE = re.compile(
    rf"({IPA_SEGMENT}):\[([^\]]+)\]{re.escape(_PHARYNGEALIZED)}"
)
_SET_SUFFIX_PHARYNGEALIZED_RE = re.compile(
    rf"\{{([^{re.escape(_PHARYNGEALIZED)}]+)\}}{re.escape(_PHARYNGEALIZED)}"
)
_IN_SEGMENT_PHARYNGEALIZED_RE = re.compile(rf"({IPA_SEGMENT})")


def _add_pharyngeal_features(features: str) -> str:
    return add_features_to_matrix_body(features, _PHARYNGEAL_FEATURES)


def _expand_pharyngealized_set_members(members: str) -> str:
    expanded: list[str] = []
    for member in members.split(","):
        member = member.strip()
        if not member:
            continue
        if ":" in member:
            segment, _, feature_body = member.partition(":[")
            if feature_body.endswith("]"):
                features = feature_body[:-1]
                expanded.append(f"{segment}:[{_add_pharyngeal_features(features)}]")
            else:
                expanded.append(f"{member}:[-atr,+rtr]")
        else:
            expanded.append(apply_features_to_token(member, _PHARYNGEAL_FEATURES))
    return "{" + ",".join(expanded) + "}"


def _rewrite_pharyngealized_segment(segment: str) -> str:
    if _PHARYNGEALIZED not in segment:
        return segment
    base = segment.replace(_PHARYNGEALIZED, "")
    return apply_features_to_token(base, _PHARYNGEAL_FEATURES)


def _rewrite_outside_brackets(text: str) -> str:
    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
            continue
        parts.append(
            _IN_SEGMENT_PHARYNGEALIZED_RE.sub(
                lambda match: _rewrite_pharyngealized_segment(match.group(1)),
                segment,
            )
        )
    return "".join(parts)


def normalize_asca_pharyngealized_marks(text: str) -> str:
    """Map Index pharyngealized ``ˤ`` placement to ASCA ``:[-atr,+rtr]`` notation."""
    if not text or _PHARYNGEALIZED not in text:
        return text

    text = _POST_MATRIX_PHARYNGEALIZED_RE.sub(
        lambda match: f"{match.group(1)}:[{_add_pharyngeal_features(match.group(2))}]",
        text,
    )
    text = _SET_SUFFIX_PHARYNGEALIZED_RE.sub(
        lambda match: _expand_pharyngealized_set_members(match.group(1)),
        text,
    )
    return _rewrite_outside_brackets(text)


__all__ = ["normalize_asca_pharyngealized_marks"]
