"""Index class letters → ASCA groupings."""

import re

from conlanger.utils.features import apply_features_to_token

# Class-letter boundary policy (compile-time tokenisation).
# See docs/sound-change-applier.md — "Class-letter expansion boundaries".
#
# A mapped uppercase letter expands when both lookarounds succeed:
# - BEFORE: start of (non-matrix) segment, or after delimiter / peer class /
#   length mark / hyphen / digit / closing ) ] / ellipsis / ʔ / ç —
#   enables glued clusters (SR, VOR), VːR, digit refs (V3R), (C,0)U, ʔR, çT.
# - AFTER: punctuation (incl. '(' and '…'), length mark ː, end, glued
#   uppercase class, IPA extension (Tʃ), ASCII lowercase (Kr, _Ra), or
#   extra modifiers outside the IPA-ext block (β, ʱ, ŋ, ç). Subscripts
#   (₁) are excluded.
# Unglued pass: remaining mapped letters whose previous char is *not* a
# BEFORE delimiter (lowercase IPA prefix: rK, sTP, nQ, hR). Mapping
# results are not re-expanded (S→P stays P).

_CLASS_BEFORE_CHARS = r"\{\[\s/,>_A-Z#$%|!\(ː0-9)\]…ʔç-"
_CLASS_BEFORE_DELIMS = rf"[{_CLASS_BEFORE_CHARS}]"
_CLASS_BEFORE = rf"(?:^|(?<={_CLASS_BEFORE_DELIMS}))"
_CLASS_UNGLUED_PREFIX = rf"(?<=[^{_CLASS_BEFORE_CHARS}])"

_FOLLOW_PUNCT = r"[:,\[\]\{\}\s/>_#$%|!\)\(…ː-]"
_FOLLOW_GLUED_UPPER = r"[A-Z]"
_FOLLOW_IPA_EXT = r"[\u0250-\u02AF]"
_FOLLOW_ASCII_LOWER = r"[a-z]"
_FOLLOW_ASCII_OR_IPA = r"[a-z\u0250-\u02AF]"
_FOLLOW_EXTRA_MODIFIERS = r"[βʱŋç]"

_CLASS_AFTER = (
    rf"(?={_FOLLOW_PUNCT}|$"
    rf"|{_FOLLOW_GLUED_UPPER}"
    rf"|{_FOLLOW_IPA_EXT}"
    rf"|{_FOLLOW_ASCII_LOWER}"
    rf"|{_FOLLOW_EXTRA_MODIFIERS})"
)
_CLASS_AFTER_LABIALIZED = (
    rf"(?={_FOLLOW_PUNCT}|$|{_FOLLOW_GLUED_UPPER}"
    rf"|{_FOLLOW_ASCII_OR_IPA}|{_FOLLOW_EXTRA_MODIFIERS})"
)

_LABIAL = "\u02b7"
_ASCA_NATIVE_GROUPINGS = frozenset("COSPFLNGV")


def _labialize_mapping(mapping: str) -> str:
    if mapping.startswith("{") and mapping.endswith("}"):
        members = [part.strip() for part in mapping[1:-1].split(",") if part.strip()]
        labialized: list[str] = []
        for member in members:
            if not member.endswith("]"):
                labialized.append(member)
            elif re.fullmatch(r"(.+):\[([^\]]+)\]", member):
                labialized.append(apply_features_to_token(member, ("+round",)))
            else:
                labialized.append(f"{member[:-1]},+round]")
        return "{" + ",".join(labialized) + "}"
    if not mapping.endswith("]"):
        return mapping
    if re.fullmatch(r"(.+):\[([^\]]+)\]", mapping):
        return apply_features_to_token(mapping, ("+round",))
    return f"{mapping[:-1]},+round]"


def expand_grouping_letter(
    letter: str,
    mappings: dict[str, str],
    *,
    labial: bool,
) -> str:
    if letter in mappings:
        mapping = mappings[letter]
        return _labialize_mapping(mapping) if labial else mapping
    if letter in _ASCA_NATIVE_GROUPINGS:
        return f"{letter}:[+round]" if labial else letter
    return letter


def _grouping_letter_pattern(keys: set[str]) -> str:
    return "|".join(re.escape(key) for key in sorted(keys, key=len, reverse=True))


def _class_letter_pattern(
    keys: set[str],
    *,
    before: str,
    after: str,
    suffix: str = "",
) -> re.Pattern[str]:
    letters = _grouping_letter_pattern(keys)
    return re.compile(rf"{before}({letters}){suffix}{after}")


def _apply_asca_group_mappings_outside_brackets(
    text: str,
    mappings: dict[str, str],
) -> str:
    """Expand Index class letters outside ``[...]`` feature matrices."""
    index_keys = set(mappings.keys())
    labial_keys = index_keys | _ASCA_NATIVE_GROUPINGS

    optional_labial = _class_letter_pattern(
        labial_keys,
        before=_CLASS_BEFORE,
        after=_CLASS_AFTER,
        suffix=rf"\({_LABIAL}\)",
    )

    def _replace_optional_labial(match: re.Match[str]) -> str:
        letter = match.group(1)
        lab = expand_grouping_letter(letter, mappings, labial=True)
        base = expand_grouping_letter(letter, mappings, labial=False)
        pair = f"{lab},{base}"
        if match.start() > 0 and match.string[match.start() - 1] in "{,":
            return pair
        return "{" + pair + "}"

    text = optional_labial.sub(_replace_optional_labial, text)

    suffix_labial = _class_letter_pattern(
        labial_keys,
        before=_CLASS_BEFORE,
        after=_CLASS_AFTER_LABIALIZED,
        suffix=re.escape(_LABIAL),
    )
    text = suffix_labial.sub(
        lambda match: expand_grouping_letter(match.group(1), mappings, labial=True),
        text,
    )

    bare = _class_letter_pattern(
        index_keys,
        before=_CLASS_BEFORE,
        after=_CLASS_AFTER,
    )
    text = bare.sub(
        lambda match: expand_grouping_letter(match.group(1), mappings, labial=False),
        text,
    )

    unglued = _class_letter_pattern(
        index_keys,
        before=_CLASS_UNGLUED_PREFIX,
        after=_CLASS_AFTER,
    )
    return unglued.sub(
        lambda match: expand_grouping_letter(match.group(1), mappings, labial=False),
        text,
    )


def apply_asca_group_mappings_to_string(
    text: str,
    mappings: dict[str, str],
) -> str:
    """Expand Index class letters to ASCA tokens in one rule-string field."""
    if not text or not mappings:
        return text

    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
        else:
            parts.append(_apply_asca_group_mappings_outside_brackets(segment, mappings))
    return "".join(parts)
