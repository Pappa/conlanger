from typing import ClassVar

from conlanger.tools.compile.asca.aliases import apply_asca_aliases
from conlanger.tools.compile.asca.chains import expand_chained_corpus_rule
from conlanger.tools.compile.asca.group_mappings import (
    apply_asca_group_mappings_to_string,
)
from conlanger.tools.compile.asca.parallel_null_columns import (
    drop_mixed_parallel_null_columns,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_string
from conlanger.tools.compile.asca.tilde import normalize_corpus_rule_tilde_fields


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
        self._group_mappings = {} if group_mappings is None else group_mappings

        if rule.get("skip", False):
            self.prefixes = {
                "asca": "#\t",
                "brassica": ";;\t",
            }
        # Compile applier-specific rule text once at construction (stored in ``value``).
        super().__init__(self._compile_rule_text(format), format)

    def _compile_rule_text(self, format: str) -> str:
        separator = self.separator.get(format, {})

        input_text = self.input
        output_text = self.output
        if format == "asca":
            input_text = drop_mixed_parallel_null_columns(input_text)
            output_text = drop_mixed_parallel_null_columns(output_text)

        result = input_text + separator["output"] + output_text
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
        return apply_asca_group_mappings_to_string(rule, self._group_mappings)


class SoundChangeRuleSet:
    def __init__(
        self,
        section: dict,
        format: str = "asca",
        *,
        group_mappings: dict[str, str] | None = None,
    ):
        mappings = {} if group_mappings is None else group_mappings
        self._parts = [RuleTitle(section, format)]
        if section.get("citation"):
            self._parts.append(RuleCitation(section["citation"], format))
        if section.get("comment"):
            self._parts.append(RuleComment(section["comment"], format))
        if section.get("rules"):
            for rule in section["rules"]:
                normalized = normalize_corpus_rule_tilde_fields(rule)
                for step in expand_chained_corpus_rule(normalized):
                    self._parts.append(
                        RuleChange(step, format, group_mappings=mappings)
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
