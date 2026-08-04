from typing import ClassVar


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
        "K:[": "[+ cons, - fr, + bk, + hi, - lo, ",
        "K": "[+ cons, - fr, + bk, + hi, - lo]",
        "h₁": "h",
        "h₂": "x",
        "h₃": "ɣʷ",
    }

    def __init__(self, rule: dict[str, str], format: str = "asca"):
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

        if rule.get("skip", False):
            self.prefixes = {"asca": "#\t", "brassica": ";;\t"}
        super().__init__(self._format(format), format)

    def _format(self, format: str):
        separator = self.separator.get(format, {})

        result = self.input + separator["output"] + self.output
        if self.env:
            result += separator["env"] + self.env
        if self.exception:
            result += separator["exception"] + self.exception

        return self._apply_aliases(result)

    def _apply_aliases(self, rule: str):
        for alias, replacement in self.aliases.items():
            rule = rule.replace(alias, replacement)
        return rule


class SoundChangeRuleSet:
    def __init__(self, section: dict, format: str = "asca"):
        self._parts = [RuleTitle(section, format)]
        if section.get("citation"):
            self._parts.append(RuleCitation(section["citation"], format))
        if section.get("comment"):
            self._parts.append(RuleComment(section["comment"], format))
        if section.get("rules"):
            for rule in section["rules"]:
                self._parts.append(RuleChange(rule, format))

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
