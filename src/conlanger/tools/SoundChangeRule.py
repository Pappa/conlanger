from xml.etree.ElementTree import Element

class RulePartBase:
    prefixes = {"asca": "# ", "brassica": "; "}
    def __init__(self, value: str, format: str = "asca"):
        if format not in self.prefixes:
            raise ValueError(f"Unsupported format: {format}")
        self.value = value
        self.format = format

    def __str__(self):
        self.prefix = self.prefixes[self.format]
        return f"{self.prefix}{self.value}"


class RuleTitle(RulePartBase):
    prefixes = {"asca": "@ ", "brassica": "; "}
    def __init__(self, el: Element, format: str = "asca"):
        title = el.attrib["index"] + " - " + el.attrib["name"]
        super().__init__(title, format)

class RuleCitation(RulePartBase):
    prefixes = {"asca": "# citation: ", "brassica": "; citation: "}
    def __init__(self, value: str, format: str = "asca"):
        super().__init__(value, format)

class RuleComment(RulePartBase):
    prefixes = {"asca": "\t# ", "brassica": "; "}
    def __init__(self, value: str, format: str = "asca"):
        super().__init__(value, format)


class RuleChange(RulePartBase):
    prefixes = {"asca": "\t", "brassica": ""}
    def __init__(self, value: str, format: str = "asca"):
        super().__init__(self._format(value, format), format)

    def _format(self, value: str, format: str):
        if format == "asca":
            return value.replace('&gt;', '>').replace('!', '|')
        elif format == "brassica":
            return value.replace('&gt;', '/').replace('>', '/')
        else:
            raise ValueError(f"Unsupported format: {format}")


class SoundChangeRule:
    def __init__(self, input: Element, format: str = "asca"):
        self._parts = [RuleTitle(input, format), *[self._add_part(child, format) for child in input]]

    def _add_part(self, part: Element, format):
        if part.tag == "cite":
            return RuleCitation(part.text, format)
        elif part.tag == "comment":
            return RuleComment(part.text, format)
        elif part.tag == "rule":
            return RuleChange(part.text, format)
        else:
            return RulePartBase(part.text, format)

    def __str__(self):
        return "\n".join([str(part) for part in self._parts])