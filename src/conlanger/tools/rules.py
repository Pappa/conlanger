from typing import ClassVar

import re
from functools import lru_cache

from conlanger.tools.parsers import load_group_mappings

_GROUPING_PREC = r"(?:^|(?<=[\{\[\s/,>_A-Z#$%|!\(-]))"
_GROUPING_FOLLOW = r"(?=[:,\[\]\{\}\s/>_#$%|!\)-]|$|[A-Z])"

# Index length marks → ASCA [+long] feature (compile-time, ASCA only).
_IPA_SEGMENT = r"[a-zA-Z\u0250-\u02AF\u1D00-\u1DBF\u0300-\u036F]+"
_OPT_LENGTH_RE = re.compile(rf"({_IPA_SEGMENT}|[A-Z])\(ː\)")
_GROUPING_LENGTH_RE = re.compile(r"([A-Z])ː")
_SEGMENT_LENGTH_RE = re.compile(rf"({_IPA_SEGMENT})ː")

# Index Diachronica leading em dash (U+2014) marks a sub-rule line, not a segment.
_LEADING_INDEX_RULE_MARKER_RE = re.compile(r"^—\s*")


def strip_leading_index_rule_marker(text: str) -> str:
    """Remove Index leading em dash rule marker (``— ``) from one rule field."""
    if not text:
        return text
    return _LEADING_INDEX_RULE_MARKER_RE.sub("", text, count=1)


def normalize_asca_length_marks(text: str) -> str:
    """Map Index ``ː`` / ``(ː)`` length notation to ASCA ``:[+long]``."""
    if not text or ("ː" not in text and "(ː)" not in text):
        return text
    text = _OPT_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _GROUPING_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _SEGMENT_LENGTH_RE.sub(r"\1:[+long]", text)
    return text


@lru_cache(maxsize=1)
def asca_group_mappings_dict() -> dict[str, str]:
    """Load Index→ASCA class-letter mappings from package CSV."""
    return {row.grouping: row.mapping for row in load_group_mappings()}


def apply_asca_group_mappings_to_string(
    text: str,
    mappings: dict[str, str],
) -> str:
    """Expand Index class letters to ASCA tokens in one rule-string field."""
    if not text or not mappings:
        return text
    keys = sorted(mappings.keys(), key=len, reverse=True)
    alt = "|".join(re.escape(key) for key in keys)
    regex = re.compile(rf"{_GROUPING_PREC}(?:{alt}){_GROUPING_FOLLOW}")
    return regex.sub(lambda match: mappings[match.group(0)], text)


class RulePartBase:
    prefixes: ClassVar[dict[str, str]] = {"asca": "# ", "brassica": "; "}

    def __init__(self, value: str, format: str = "asca"):
        if format not in self.prefixes:
            raise ValueError(f"Unsupported format: {format}")
        self.value = value
        self.format = format

    def __str__(self):
        return f"{self.prefixes[self.format]}{self.value}"


class RuleTitle(RulePartBase):
    prefixes: ClassVar[dict[str, str]] = {"asca": "@ ", "brassica": "; "}

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
    prefixes: ClassVar[dict[str, str]] = {"asca": "\t# ", "brassica": "; "}

    def __init__(self, value: str, format: str = "asca"):
        super().__init__(self._format(value, format), format)

    def _format(self, value: str, format: str):
        if format == "asca":
            return value.replace("\n", "\n\t# ")
        if format == "brassica":
            return value.replace("\n", "\n; ")


class RuleChange(RulePartBase):
    rule: dict[str, str]
    prefixes: ClassVar[dict[str, str]] = {"asca": "\t", "brassica": ""}
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
            self.prefixes = {"asca": "#\t", "brassica": ";;\t"}
        # Compile applier-specific rule text once at construction (stored in ``value``).
        super().__init__(self._compile_rule_text(format), format)

    def _compile_rule_text(self, format: str) -> str:
        separator = self.separator.get(format, {})

        if format == "asca":
            inp = strip_leading_index_rule_marker(self.input)
            out = strip_leading_index_rule_marker(self.output)
            env = (
                strip_leading_index_rule_marker(self.env) if self.env else None
            )
            exception = (
                strip_leading_index_rule_marker(self.exception)
                if self.exception
                else None
            )
        else:
            inp, out, env, exception = (
                self.input,
                self.output,
                self.env,
                self.exception,
            )

        result = inp + separator["output"] + out
        if env:
            result += separator["env"] + env
        if exception:
            result += separator["exception"] + exception

        if format == "asca":
            result = self._apply_asca_group_mappings(result, format)
            result = normalize_asca_length_marks(result)
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
