import re
from functools import lru_cache
from typing import ClassVar

from conlanger.tools.parsers import load_group_mappings

_GROUPING_PREC = r"(?:^|(?<=[\{\[\s/,>_A-Z#$%|!\(-]))"
_GROUPING_FOLLOW = r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z])"
_GROUPING_FOLLOW_LABIALIZED = (
    r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z]|[a-z\u0250-\u02AF])"
)
_LABIAL = "\u02b7"
_ASCA_NATIVE_GROUPINGS = frozenset("COSPFLNGV")
_ELLIPSIS = "\u2026"
_ELLIPSIS_SRC = rf"(?:{_ELLIPSIS}|\.\.\.?)"
# Index ``(C…)`` / ``(VC…)`` / ``(C…?)`` → ASCA ``(C,0)`` (zero-or-more).
_TRAILING_GROUPING_ELLIPSIS_RE = re.compile(rf"\(([A-Z$%#]+){_ELLIPSIS_SRC}\??\)")
# Index ``(…X)`` (“for any number of X remaining”) → ASCA ``(..)X``.
_LEADING_GROUPING_ELLIPSIS_RE = re.compile(rf"\({_ELLIPSIS_SRC}([A-Z$%#]+)\)")
_HAS_GROUPING_ELLIPSIS_RE = re.compile(
    rf"\((?:{_ELLIPSIS_SRC}[A-Z$%#]+|[A-Z$%#]+{_ELLIPSIS_SRC}\??)\)"
)


def normalize_asca_optional_grouping_ellipsis(text: str) -> str:
    """Map Index grouping ellipsis in optionals to ASCA zero-or-more / skip forms."""
    if not text or not _HAS_GROUPING_ELLIPSIS_RE.search(text):
        return text

    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
        else:
            segment = _TRAILING_GROUPING_ELLIPSIS_RE.sub(r"(\1,0)", segment)
            segment = _LEADING_GROUPING_ELLIPSIS_RE.sub(r"(..)\1", segment)
            parts.append(segment)
    return "".join(parts)


# Index length marks → ASCA [+long] feature (compile-time, ASCA only).
_LENGTH = "\u02d0"
_IPA_MODIFIER = r"[\u02B0-\u02B8\u02BC\u02D1\u02E4\u0300-\u036F]"
_IPA_SEGMENT = (
    r"[a-zA-Z\u00C0-\u024F\u0250-\u02AF\u1D00-\u1DBF]+"
    rf"(?:{_IPA_MODIFIER})*"
)
_OPT_LENGTH_COMMA_RE = re.compile(rf"({_IPA_SEGMENT}|[A-Z])\({_LENGTH},([^)]+)\)")
_OPT_LENGTH_RE = re.compile(rf"({_IPA_SEGMENT}|[A-Z])\({_LENGTH}\)")
_SET_OPT_LENGTH_RE = re.compile(rf"\}}\({_LENGTH}\)")
_GROUPING_LENGTH_RE = re.compile(r"([A-Z])" + re.escape(_LENGTH))
_SEGMENT_LENGTH_RE = re.compile(rf"({_IPA_SEGMENT}){re.escape(_LENGTH)}")
_SET_SUFFIX_LENGTH_RE = re.compile(r"\}" + re.escape(_LENGTH))
_DOUBLE_LENGTH_RE = re.compile(r":\[\+long\]" + re.escape(_LENGTH))
_BARE_SET_LENGTH_RE = re.compile(rf"(^|,)\s*{re.escape(_LENGTH)}(?=,|$)")


def _expand_bare_length_in_sets(text: str) -> str:
    if _LENGTH not in text:
        return text

    def repl(match: re.Match[str]) -> str:
        inner = _BARE_SET_LENGTH_RE.sub(r"\1V:[+long]", match.group(1))
        return "{" + inner + "}"

    return re.sub(r"\{([^}]*)\}", repl, text)


def normalize_asca_length_marks(text: str) -> str:
    """Map Index ``ː`` / ``(ː)`` length notation to ASCA ``:[+long]``."""
    if not text or (_LENGTH not in text and f"({_LENGTH})" not in text):
        return text
    text = _OPT_LENGTH_COMMA_RE.sub(r"{\1:[+long],\1\2}", text)
    text = _SET_OPT_LENGTH_RE.sub("}:[+long]", text)
    text = _OPT_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _GROUPING_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _SEGMENT_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _SET_SUFFIX_LENGTH_RE.sub("}:[+long]", text)
    text = _expand_bare_length_in_sets(text)
    text = _DOUBLE_LENGTH_RE.sub(":[+long]", text)
    return text


_EJECTIVE = "\u02bc"
_TYPO_APOSTROPHE_RE = re.compile(rf"({_IPA_SEGMENT}|[A-Z])(\u2019)")


def normalize_typographic_apostrophes(text: str) -> str:
    """Map Index typographic apostrophe (U+2019) to ejective ``ʼ`` (U+02BC)."""
    if not text or "\u2019" not in text:
        return text
    return _TYPO_APOSTROPHE_RE.sub(rf"\1{_EJECTIVE}", text)


_POST_MATRIX_EJECTIVE_RE = re.compile(
    rf"({_IPA_SEGMENT}):\[([^\]]+)\]{re.escape(_EJECTIVE)}"
)
_SET_SUFFIX_EJECTIVE_RE = re.compile(
    rf"\{{([^{re.escape(_EJECTIVE)}]+)\}}{re.escape(_EJECTIVE)}"
)
_BARE_EJECTIVE_RE = re.compile(rf"({_IPA_SEGMENT}){re.escape(_EJECTIVE)}(?![:\[])")


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


@lru_cache(maxsize=1)
def asca_group_mappings_dict() -> dict[str, str]:
    """Load Index→ASCA class-letter mappings from package CSV."""
    return {row.grouping: row.mapping for row in load_group_mappings()}


def _labialize_single_token(token: str) -> str:
    if token.endswith("]"):
        return f"{token[:-1]},+round]"
    return token


def _labialize_mapping(mapping: str) -> str:
    if mapping.startswith("{") and mapping.endswith("}"):
        members = [part.strip() for part in mapping[1:-1].split(",") if part.strip()]
        return (
            "{" + ",".join(_labialize_single_token(member) for member in members) + "}"
        )
    return _labialize_single_token(mapping)


def _expand_grouping_letter(
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
        lab = _expand_grouping_letter(letter, mappings, labial=True)
        base = _expand_grouping_letter(letter, mappings, labial=False)
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
        lambda match: _expand_grouping_letter(match.group(1), mappings, labial=True),
        text,
    )

    bare = re.compile(
        rf"{_GROUPING_PREC}({_grouping_letter_pattern(index_keys)}){_GROUPING_FOLLOW}"
    )
    return bare.sub(
        lambda match: _expand_grouping_letter(match.group(1), mappings, labial=False),
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


class RulePartBase:
    prefixes: ClassVar[dict[str, str]] = {
        "asca": "# ",
        "brassica": "; ",
    }

    def __init__(self, value: str, format: str = "asca"):
        if format not in self.prefixes:
            raise ValueError(f"Unsupported format: {format}")
        self.value = value
        self.format = format

    def __str__(self):
        return f"{self.prefixes[self.format]}{self.value}"


class RuleTitle(RulePartBase):
    prefixes: ClassVar[dict[str, str]] = {
        "asca": "@ ",
        "brassica": "; ",
    }

    def __init__(self, section: dict, format: str = "asca"):
        title = section["index"] + " - " + section["section"]
        super().__init__(title, format)


class RuleCitation(RulePartBase):
    prefixes: ClassVar[dict[str, str]] = {
        "asca": "# citation: ",
        "brassica": "; citation: ",
    }

    def __init__(self, value: str, format: str = "asca"):
        super().__init__(self._format(value, format), format)

    def _format(self, value: str, format: str):
        if format == "asca":
            return value.replace("\n", "\n# ")
        if format == "brassica":
            return value.replace("\n", "\n; ")


class RuleComment(RulePartBase):
    prefixes: ClassVar[dict[str, str]] = {
        "asca": "\t# ",
        "brassica": "; ",
    }

    def __init__(self, value: str, format: str = "asca"):
        super().__init__(self._format(value, format), format)

    def _format(self, value: str, format: str):
        if format == "asca":
            return value.replace("\n", "\n\t# ")
        if format == "brassica":
            return value.replace("\n", "\n; ")


class RuleChange(RulePartBase):
    rule: dict[str, str]
    prefixes: ClassVar[dict[str, str]] = {
        "asca": "\t",
        "brassica": "",
    }
    separator: ClassVar[dict[str, dict[str, str]]] = {
        "asca": {
            "output": " > ",
            "env": " / ",
            "exception": " // ",
        },
        "brassica": {
            "output": " / ",
            "env": " / ",
            "exception": " // ",
        },
    }
    aliases: ClassVar[dict[str, str]] = {
        "h₁": "h",
        "h₂": "x",
        "h₃": "ɣʷ",
    }

    def __init__(
        self,
        rule: dict[str, str],
        format: str = "asca",
        *,
        group_mappings: dict[str, str] | None = None,
    ):
        try:
            self.input = rule["input"]
        except KeyError:
            raise ValueError("input is required")
        try:
            self.output = rule["output"]
        except KeyError:
            raise ValueError("output is required")

        self.env = rule.get("env", None)
        self.exception = rule.get("exception", None)
        self._group_mappings = group_mappings

        if rule.get("skip", False):
            self.prefixes = {
                "asca": "#\t",
                "brassica": ";;\t",
            }
        # Compile applier-specific rule text once at construction (stored in ``value``).
        super().__init__(self._compile_rule_text(format), format)

    def _compile_rule_text(self, format: str) -> str:
        separator = self.separator.get(format, {})

        result = self.input + separator["output"] + self.output
        if self.env:
            result += separator["env"] + self.env
        if self.exception:
            result += separator["exception"] + self.exception

        if format == "asca":
            result = normalize_asca_optional_grouping_ellipsis(result)
            result = self._apply_asca_group_mappings(result, format)
            result = normalize_asca_length_marks(result)
            result = normalize_typographic_apostrophes(result)
            result = normalize_asca_ejective_marks(result)
        return self._apply_aliases(result)

    def _format(self, format: str):
        """Backward-compatible alias for ``_compile_rule_text``."""
        return self._compile_rule_text(format)

    def _apply_asca_group_mappings(self, rule: str, format: str) -> str:
        if format != "asca":
            return rule
        mappings = (
            self._group_mappings
            if self._group_mappings is not None
            else asca_group_mappings_dict()
        )
        return apply_asca_group_mappings_to_string(rule, mappings)

    def _apply_aliases(self, rule: str):
        for alias, replacement in self.aliases.items():
            rule = rule.replace(alias, replacement)
        return rule


class SoundChangeRuleSet:
    def __init__(
        self,
        section: dict,
        format: str = "asca",
        *,
        group_mappings: dict[str, str] | None = None,
    ):
        self._parts = [RuleTitle(section, format)]
        if section.get("citation"):
            self._parts.append(RuleCitation(section["citation"], format))
        if section.get("comment"):
            self._parts.append(RuleComment(section["comment"], format))
        if section.get("rules"):
            for rule in section["rules"]:
                self._parts.append(
                    RuleChange(rule, format, group_mappings=group_mappings)
                )

    def __str__(self):
        return "\n".join([str(part) for part in self._parts])

    @property
    def title(self):
        return self._parts[0].value


class DebugRules:
    def __init__(self, section: dict, format: str = "asca"):
        self._rules = [
            (index, self._create_rule(section, rule, index, format))
            for index, rule in enumerate(section["rules"])
        ]

    def _create_rule(self, section: dict, rule: dict, index: int, format: str):
        item = {"index": section["index"], "section": str(index), "rules": [rule]}
        return SoundChangeRuleSet(item, format)

    def __iter__(self):
        return iter(self._rules)

    def __len__(self):
        return len(self._rules)

    def __getitem__(self, index):
        return self._rules[index]
