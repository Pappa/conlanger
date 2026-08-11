"""Index class letters → ASCA groupings from ``group_mappings.csv``."""

import re
from functools import lru_cache

from conlanger.utils.mappings import load_group_mappings

_GROUPING_PREC = r"(?:^|(?<=[\{\[\s/,>_A-Z#$%|!\(-]))"
_GROUPING_FOLLOW = r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z]|[\u0250-\u02AF])"
_GROUPING_FOLLOW_LABIALIZED = (
    r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z]|[a-z\u0250-\u02AF])"
)
_LABIAL = "\u02b7"
_ASCA_NATIVE_GROUPINGS = frozenset("COSPFLNGV")


@lru_cache(maxsize=1)
def asca_group_mappings_dict() -> dict[str, str]:
    """Load Index→ASCA class-letter mappings from package CSV."""
    return {row.grouping: row.mapping for row in load_group_mappings()}


def _add_features_to_matrix_body(features: str, extra: tuple[str, ...]) -> str:
    body = features
    for feature in extra:
        token = feature if feature.startswith(("+", "-")) else f"+{feature}"
        if token in body or f"-{token.lstrip('+-')}" in body:
            continue
        body = f"{body},{token}" if body else token
    return body


def _apply_features_to_token(token: str, extra: tuple[str, ...]) -> str:
    if not extra:
        return token
    match = re.fullmatch(r"(.+):\[([^\]]+)\]", token)
    if match:
        host, body = match.group(1), match.group(2)
        return f"{host}:[{_add_features_to_matrix_body(body, extra)}]"
    return f"{token}:[{_add_features_to_matrix_body('', extra)}]"


def _labialize_single_token(token: str) -> str:
    if not token.endswith("]"):
        return token
    if re.fullmatch(r"(.+):\[([^\]]+)\]", token):
        return _apply_features_to_token(token, ("+round",))
    return f"{token[:-1]},+round]"


def _labialize_mapping(mapping: str) -> str:
    if mapping.startswith("{") and mapping.endswith("}"):
        members = [part.strip() for part in mapping[1:-1].split(",") if part.strip()]
        return (
            "{" + ",".join(_labialize_single_token(member) for member in members) + "}"
        )
    return _labialize_single_token(mapping)


def _merge_mapping_with_features(mapping: str, features: str) -> str:
    extra = tuple(part.strip() for part in features.split(",") if part.strip())
    if mapping.startswith("{") and mapping.endswith("}"):
        members = [part.strip() for part in mapping[1:-1].split(",") if part.strip()]
        return (
            "{"
            + ",".join(
                _merge_mapping_with_features(member, features) for member in members
            )
            + "}"
        )
    return _apply_features_to_token(mapping, extra)


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


def _apply_asca_group_mappings_outside_brackets(
    text: str,
    mappings: dict[str, str],
) -> str:
    """Expand Index class letters outside ``[...]`` feature matrices."""
    if not text or not mappings:
        return text

    index_keys = set(mappings.keys())
    labial_keys = index_keys | _ASCA_NATIVE_GROUPINGS

    optional_labial = re.compile(
        rf"{_GROUPING_PREC}({_grouping_letter_pattern(labial_keys)})"
        rf"\({_LABIAL}\){_GROUPING_FOLLOW}"
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

    suffix_labial = re.compile(
        rf"{_GROUPING_PREC}({_grouping_letter_pattern(labial_keys)})"
        rf"{_LABIAL}{_GROUPING_FOLLOW_LABIALIZED}"
    )
    text = suffix_labial.sub(
        lambda match: expand_grouping_letter(match.group(1), mappings, labial=True),
        text,
    )

    bare = re.compile(
        rf"{_GROUPING_PREC}({_grouping_letter_pattern(index_keys)}){_GROUPING_FOLLOW}"
    )
    return bare.sub(
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
