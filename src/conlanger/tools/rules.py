from typing import ClassVar

from conlanger.tools.asca_compile.aliases import apply_asca_aliases
from conlanger.tools.asca_compile.apostrophes import normalize_typographic_apostrophes
from conlanger.tools.asca_compile.chains import expand_chained_corpus_rule
from conlanger.tools.asca_compile.ejectives import normalize_asca_ejective_marks
from conlanger.tools.asca_compile.ellipsis import (
    normalize_asca_optional_grouping_ellipsis,
)
from conlanger.tools.asca_compile.group_mappings import (
    apply_asca_group_mappings_to_string,
    asca_group_mappings_dict,
)
from conlanger.tools.asca_compile.group_mappings import (
    expand_grouping_letter as _expand_grouping_letter,
)
from conlanger.tools.asca_compile.length_marks import normalize_asca_length_marks
from conlanger.tools.asca_compile.pipeline import compile_asca_rule_string

# Public re-exports for tests and callers that import transform helpers from ``rules``.
__all__ = [
    "DebugRules",
    "RuleChange",
    "RuleCitation",
    "RuleComment",
    "RulePartBase",
    "RuleTitle",
    "SoundChangeRuleSet",
    "_expand_grouping_letter",
    "apply_asca_group_mappings_to_string",
    "asca_group_mappings_dict",
    "compile_asca_rule_string",
    "normalize_asca_ejective_marks",
    "normalize_asca_length_marks",
    "normalize_asca_optional_grouping_ellipsis",
    "normalize_typographic_apostrophes",
]


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
            result = compile_asca_rule_string(
                result,
                group_mappings=self._group_mappings,
            )
        else:
            result = apply_asca_aliases(result)
        return result

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
                for step in expand_chained_corpus_rule(rule):
                    self._parts.append(
                        RuleChange(step, format, group_mappings=group_mappings)
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
