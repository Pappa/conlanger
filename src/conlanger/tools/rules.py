from __future__ import annotations

import random
from typing import ClassVar

from conlanger.tools.compile.asca.chains import expand_chained_corpus_rule
from conlanger.tools.compile.asca.parallel_null_columns import (
    drop_mixed_parallel_null_columns,
)
from conlanger.tools.compile.asca.parallel_output_null import (
    expand_parallel_output_null_branches,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_string
from conlanger.tools.compile.asca.tilde import normalize_corpus_rule_tilde_fields
from conlanger.utils.file_io import load_compiler_config
from conlanger.utils.mappings import CompilerConfig

_SUPPORTED_FORMATS = frozenset({"asca"})


def _is_whole_field_set(text: str) -> bool:
    """True when ``text`` is a single ``{…}`` set spanning the whole field."""
    stripped = text.strip()
    if len(stripped) < 2 or not stripped.startswith("{") or not stripped.endswith("}"):
        return False
    depth = 0
    for position, char in enumerate(stripped):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
            if depth == 0 and position != len(stripped) - 1:
                return False
    return depth == 0


def _split_set_members(text: str) -> list[str]:
    inner = text.strip()[1:-1]
    members: list[str] = []
    current: list[str] = []
    depth = 0
    for char in inner:
        if char == "{":
            depth += 1
            current.append(char)
        elif char == "}":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            members.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    members.append("".join(current).strip())
    return members


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
    prefix: ClassVar[str] = "\t"
    skip_prefix: ClassVar[str] = "#\t"
    output_separator: ClassVar[str] = " > "
    env_separator: ClassVar[str] = " / "
    exception_separator: ClassVar[str] = " // "

    def __init__(
        self,
        input: str = "",
        output: str = "",
        env: str | None = None,
        exception: str | None = None,
        *,
        skipped: bool = False,
        raw: str = "",
        group_mappings: dict[str, str] | None = None,
        seed: int | None = None,
        rng: random.Random | None = None,
        section_index: str = "",
        compiler_config: CompilerConfig | None = None,
        **_: object,
    ):
        self.input = input
        self.output = output
        self.env = env
        self.exception = exception
        self._group_mappings = {} if group_mappings is None else group_mappings
        self._section_index = section_index
        self._compiler_config = compiler_config
        # Instance RNG only — never the process-global ``random.seed`` (ticket 66).
        self._rng = rng if rng is not None else random.Random(seed)
        self.alternatives: list[SoundChangeRule] = []

        if skipped:
            self.prefix = self.skip_prefix
            super().__init__(raw)
            return

        self.alternatives = self._build_alternatives()
        if self.alternatives:
            # Freeze one alternative uniformly as the emitted outcome.
            chosen = self.alternatives[self._rng.randrange(len(self.alternatives))]
            value = chosen.value
        else:
            # Compile ASCA rule text once at construction (stored in ``value``).
            value = self._format()
        super().__init__(value)

    def _build_alternatives(self) -> list[SoundChangeRule]:
        """Build peer alternatives for optional outputs or parallel ``∅`` output sets."""
        optional = self._build_optional_output_alternatives()
        if optional:
            return optional
        return self._build_parallel_null_set_alternatives()

    def _build_optional_output_alternatives(self) -> list[SoundChangeRule]:
        """Whole-field output set with unpaired input (ticket 66)."""
        if not (
            _is_whole_field_set(self.output) and not _is_whole_field_set(self.input)
        ):
            return []
        members = _split_set_members(self.output)
        if not members or any(not member or "{" in member for member in members):
            return []
        return [
            SoundChangeRule(
                input=self.input,
                output=member,
                env=self.env,
                exception=self.exception,
                group_mappings=self._group_mappings,
                section_index=self._section_index,
                compiler_config=self._compiler_config,
            )
            for member in members
        ]

    def _build_parallel_null_set_alternatives(self) -> list[SoundChangeRule]:
        """Paired parallel columns with ``∅`` inside output sets (ticket 81)."""
        branches = expand_parallel_output_null_branches(self.input, self.output)
        if branches is None:
            return []
        return [
            SoundChangeRule(
                input=branch_input,
                output=branch_output,
                env=self.env,
                exception=self.exception,
                group_mappings=self._group_mappings,
                section_index=self._section_index,
                compiler_config=self._compiler_config,
            )
            for branch_input, branch_output in branches
        ]

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
            section_index=self._section_index,
            compiler_config=self._compiler_config,
        )


class DiachronicSeries:
    def __init__(
        self,
        section: dict,
        format: str = "asca",
        *,
        group_mappings: dict[str, str] | None = None,
        compiler_config: CompilerConfig | None = None,
    ):
        if format not in _SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}")

        mappings = {} if group_mappings is None else group_mappings
        config = load_compiler_config() if compiler_config is None else compiler_config
        section_index = str(section.get("index", ""))
        self._parts = [RuleTitle(section)]
        if section.get("citation"):
            self._parts.append(RuleCitation(section["citation"]))
        if section.get("comment"):
            self._parts.append(RuleComment(section["comment"]))
        if section.get("status") == "skipped":
            return
        if section.get("rules"):
            for rule in section["rules"]:
                if rule.get("status") == "skipped":
                    self._parts.append(
                        SoundChangeRule(
                            **rule,
                            skipped=True,
                            group_mappings=mappings,
                            section_index=section_index,
                            compiler_config=config,
                        )
                    )
                    continue
                normalized = normalize_corpus_rule_tilde_fields(rule)
                for step in expand_chained_corpus_rule(normalized):
                    self._parts.append(
                        SoundChangeRule(
                            **step,
                            group_mappings=mappings,
                            section_index=section_index,
                            compiler_config=config,
                        )
                    )

    def __str__(self):
        return "\n".join([str(part) for part in self._parts]) + "\n"

    @property
    def title(self):
        return self._parts[0].value
