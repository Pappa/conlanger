"""Index superscript segment modifiers → ASCA feature matrices (ticket 50).

Taxonomy
--------

| Pattern | Example | Expansion |
|---------|---------|-----------|
| Class suffix labial | ``Cʷ`` | ``C:[+round]`` (ticket 23 — ``group_mappings``) |
| Class suffix palatal | ``Cʲ``, ``Lʲ`` | ``C:[+cor,+dist]`` |
| Class suffix aspirated | ``Cʰ``, ``Sʰ`` | ``C:[+spread]`` |
| Class suffix breathy | ``Cʱ`` | ``C:[+spread,+voice]`` |
| Class prefix aspirated | ``ʰC`` in env sets | ``C:[+spread]`` |
| Set suffix modifier | ``{d,n}ʲ`` | ``{d,dʲ,n,nʲ}`` |
| IPA segment suffix | ``tʰ``, ``kʷ``, ``lʲ`` | unchanged — ASCA accepts literal IPA |

Class-letter suffix/prefix rewrites run before ``apply_asca_group_mappings`` so
Index letters like ``Pʲ`` become ``P:[+cor,+dist]`` and group expansion merges
features into ``C:[+labial,+cor,+dist]`` rather than ``C:[+labial]:[+cor,+dist]``.
"""

from __future__ import annotations

import re

from conlanger.tools.asca_compile.group_mappings import (
    expand_grouping_letter,
)
from conlanger.utils.features import (
    apply_features_to_token,
    merge_mapping_with_features,
)

_GROUPING_PREC = r"(?:^|(?<=[\{\[\s/,>_A-Z#$%|!\(-]))"
_GROUPING_FOLLOW = r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z]|[a-z\u0250-\u02AF])"
_ASCA_NATIVE_GROUPINGS = frozenset("COSPFLNGV")

_LABIAL = "\u02b7"
_PALATAL = "\u02b2"
_ASPIRATED = "\u02b0"
_BREATHY = "\u02b1"

_MODIFIER_FEATURES: dict[str, tuple[str, ...]] = {
    _PALATAL: ("+cor", "+dist"),
    _ASPIRATED: ("+spread",),
    _BREATHY: ("+spread", "+voice"),
}

_SET_SUFFIX_MODIFIER_RE = re.compile(
    rf"\{{([^{_PALATAL}{_ASPIRATED}{_BREATHY}{_LABIAL}]+)\}}"
    rf"([{_PALATAL}{_ASPIRATED}{_BREATHY}])"
)


def _grouping_letter_pattern(keys: set[str]) -> str:
    return "|".join(re.escape(key) for key in sorted(keys, key=len, reverse=True))


def _expand_class_letter_modifier(
    letter: str,
    features: tuple[str, ...],
    *,
    index_keys: set[str],
    mappings: dict[str, str],
) -> str:
    if letter in index_keys:
        base = expand_grouping_letter(letter, mappings, labial=False)
        feature_text = ",".join(features)
        if re.fullmatch(r"[A-Z]", base):
            return f"{base}[{feature_text}]"
        return merge_mapping_with_features(base, feature_text)
    return apply_features_to_token(letter, features)


def _apply_class_letter_modifiers_outside_brackets(
    text: str,
    *,
    index_keys: set[str],
    mappings: dict[str, str],
) -> str:
    class_keys = index_keys | _ASCA_NATIVE_GROUPINGS
    if not text or not class_keys:
        return text

    letter_pattern = _grouping_letter_pattern(class_keys)

    for modifier, features in _MODIFIER_FEATURES.items():
        suffix = re.compile(
            rf"{_GROUPING_PREC}({letter_pattern})"
            rf"{re.escape(modifier)}{_GROUPING_FOLLOW}"
        )
        text = suffix.sub(
            lambda match, feats=features: _expand_class_letter_modifier(
                match.group(1),
                feats,
                index_keys=index_keys,
                mappings=mappings,
            ),
            text,
        )

        prefix = re.compile(
            rf"(?<=[\{{,\s/_(#]){re.escape(modifier)}({letter_pattern}){_GROUPING_FOLLOW}"
        )
        text = prefix.sub(
            lambda match, feats=features: _expand_class_letter_modifier(
                match.group(1),
                feats,
                index_keys=index_keys,
                mappings=mappings,
            ),
            text,
        )

    return text


def _expand_set_suffix_modifiers(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        members = [part.strip() for part in match.group(1).split(",") if part.strip()]
        modifier = match.group(2)
        expanded: list[str] = []
        for member in members:
            expanded.append(member)
            expanded.append(f"{member}{modifier}")
        return "{" + ",".join(expanded) + "}"

    return _SET_SUFFIX_MODIFIER_RE.sub(repl, text)


def normalize_asca_superscript_modifiers(
    text: str,
    group_mappings: dict[str, str],
) -> str:
    """Rewrite Index superscript modifiers on class letters and braced sets."""
    if not text:
        return text

    index_keys = set(group_mappings.keys())

    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
        else:
            parts.append(
                _apply_class_letter_modifiers_outside_brackets(
                    segment,
                    index_keys=index_keys,
                    mappings=group_mappings,
                )
            )
    text = "".join(parts)
    return _expand_set_suffix_modifiers(text)


__all__ = ["normalize_asca_superscript_modifiers"]
