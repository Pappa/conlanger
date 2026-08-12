from typing import ClassVar

from conlanger.tools.compile.asca.chains import expand_chained_corpus_rule
from conlanger.tools.compile.asca.group_mappings import (
    apply_asca_group_mappings_to_string,
)
from conlanger.tools.compile.asca.parallel_null_columns import (
    drop_mixed_parallel_null_columns,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_string
from conlanger.tools.compile.asca.tilde import normalize_corpus_rule_tilde_fields

_SUPPORTED_FORMATS = frozenset({"asca"})


class RulePartBase:
    prefix: ClassVar[str] = "# "

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f"{self.prefix}{self.value}"


class RuleTitle(RulePartBase):
    prefix: ClassVar[str] = "@ "

    def __init__(self, section: dict):
        title = section["index"] + " - " + section["section"]
        super().__init__(title)


class RuleCitation(RulePartBase):
    prefix: ClassVar[str] = "# citation: "

    def __init__(self, value: str):
        super().__init__(value.replace("\n", "\n# "))


class RuleComment(RulePartBase):
    prefix: ClassVar[str] = "\t# "

    def __init__(self, value: str):
        super().__init__(value.replace("\n", "\n\t# "))


class SoundChangeRule(RulePartBase):
    rule: dict[str, str]
    prefix: ClassVar[str] = "\t"
    skip_prefix: ClassVar[str] = "#\t"
    output_separator: ClassVar[str] = " > "
    env_separator: ClassVar[str] = " / "
    exception_separator: ClassVar[str] = " // "

    def __init__(
        self,
        rule: dict[str, str],
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
            self.prefix = self.skip_prefix
        # Compile ASCA rule text once at construction (stored in ``value``).
        super().__init__(self._format())

    def _format(self) -> str:
        input_text = drop_mixed_parallel_null_columns(self.input)
        output_text = drop_mixed_parallel_null_columns(self.output)

        result = input_text + self.output_separator + output_text
        if self.env:
            result += self.env_separator + self.env
        if self.exception:
            result += self.exception_separator + self.exception

        return compile_asca_rule_string(
            result,
            group_mappings=self._group_mappings,
        )

    def _apply_asca_group_mappings(self, rule: str) -> str:
        return apply_asca_group_mappings_to_string(rule, self._group_mappings)


class DiachronicSeries:
    def __init__(
        self,
        section: dict,
        format: str = "asca",
        *,
        group_mappings: dict[str, str] | None = None,
    ):
        if format not in _SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}")

        mappings = {} if group_mappings is None else group_mappings
        self._parts = [RuleTitle(section)]
        if section.get("citation"):
            self._parts.append(RuleCitation(section["citation"]))
        if section.get("comment"):
            self._parts.append(RuleComment(section["comment"]))
        if section.get("rules"):
            for rule in section["rules"]:
                normalized = normalize_corpus_rule_tilde_fields(rule)
                for step in expand_chained_corpus_rule(normalized):
                    self._parts.append(SoundChangeRule(step, group_mappings=mappings))

    def __str__(self):
        return "\n".join([str(part) for part in self._parts])

    @property
    def title(self):
        return self._parts[0].value
