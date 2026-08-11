"""Index ejective ``ʼ`` → ASCA ``:[+cg]`` feature notation."""

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT

_EJECTIVE = "\u02bc"
_POST_MATRIX_EJECTIVE_RE = re.compile(
    rf"({IPA_SEGMENT}):\[([^\]]+)\]{re.escape(_EJECTIVE)}"
)
_SET_SUFFIX_EJECTIVE_RE = re.compile(
    rf"\{{([^{re.escape(_EJECTIVE)}]+)\}}{re.escape(_EJECTIVE)}"
)
_BARE_EJECTIVE_RE = re.compile(rf"({IPA_SEGMENT}){re.escape(_EJECTIVE)}(?![:\[])")


def _add_cg_feature(features: str) -> str:
    if "+cg" in features or "-cg" in features:
        return features
    return f"{features},+cg" if features else "+cg"


def _expand_ejective_set_members(members: str) -> str:
    expanded: list[str] = []
    for member in members.split(","):
        member = member.strip()
        if not member:
            continue
        if ":" in member:
            segment, _, feature_body = member.partition(":[")
            if feature_body.endswith("]"):
                features = feature_body[:-1]
                expanded.append(f"{segment}:[{_add_cg_feature(features)}]")
            else:
                expanded.append(f"{member}:[+cg]")
        else:
            expanded.append(f"{member}:[+cg]")
    return "{" + ",".join(expanded) + "}"


def normalize_asca_ejective_marks(text: str) -> str:
    """Map Index ejective ``ʼ`` placement to ASCA ``:[+cg]`` feature notation."""
    if not text or _EJECTIVE not in text:
        return text

    text = _POST_MATRIX_EJECTIVE_RE.sub(
        lambda match: f"{match.group(1)}:[{_add_cg_feature(match.group(2))}]",
        text,
    )
    text = _SET_SUFFIX_EJECTIVE_RE.sub(
        lambda match: _expand_ejective_set_members(match.group(1)),
        text,
    )
    text = _BARE_EJECTIVE_RE.sub(r"\1:[+cg]", text)
    return text
