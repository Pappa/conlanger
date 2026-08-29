from __future__ import annotations

import random
from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from conlanger.tools.compile.asca.chains import expand_chained_index_rule
from conlanger.tools.compile.asca.parallel import expand_parallel_output_null_branches
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.asca.sets import (
    is_whole_field_set,
    split_braced_set_members,
)
from conlanger.tools.compile.asca.tilde import normalize_index_rule_tilde_fields
from conlanger.utils.file_io import load_compiler_config
from conlanger.utils.mappings import CompilerConfig

_SUPPORTED_FORMATS = frozenset({"asca"})


class RulePartBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prefix: ClassVar[str] = "# "
    value: str = ""

    def __str__(self) -> str:
        return f"{self.prefix}{self.value}"


class RuleTitle(RulePartBase):
    prefix: ClassVar[str] = "@ "

    def __init__(self, index: str, section: str, **kwargs: object) -> None:
        super().__init__(value=f"{index} - {section}", **kwargs)


class RuleCitation(RulePartBase):
    prefix: ClassVar[str] = "# citation: "

    def __init__(self, value: str = "", **kwargs: object) -> None:
        super().__init__(value=value.replace("\n", "\n# "), **kwargs)


class RuleComment(RulePartBase):
    prefix: ClassVar[str] = "\t# "

    def __init__(self, value: str = "", **kwargs: object) -> None:
        super().__init__(value=value.replace("\n", "\n\t# "), **kwargs)


class SoundChangeRule(RulePartBase):
    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    prefix: ClassVar[str] = "\t"
    skip_prefix: ClassVar[str] = "#\t"

    input: str = ""
    output: str = ""
    env: str | None = None
    exception: str | None = None
    status: str | None = None
    raw: str = ""

    alternatives: list[SoundChangeRule] = Field(default_factory=list)
    group_mappings: dict[str, str] = Field(
        default_factory=dict, exclude=True, repr=False
    )
    compiler_config: CompilerConfig | None = Field(
        default=None, exclude=True, repr=False
    )
    section_index: str = Field(default="", exclude=True, repr=False)
    rng: random.Random = Field(default_factory=random.Random, exclude=True, repr=False)
    detect_alternatives: bool = Field(default=True, exclude=True, repr=False)

    @model_validator(mode="before")
    @classmethod
    def normalize_rng(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        updated = dict(data)
        if "rng" not in updated and "seed" in updated:
            updated["rng"] = random.Random(updated.pop("seed"))
        return updated

    @model_validator(mode="after")
    def compile_rule(self) -> Self:
        if self.status == "skipped":
            self.value = self.raw
            return self

        if self.detect_alternatives:
            alternatives = self._build_alternatives()
            self.alternatives = alternatives
            if alternatives:
                chosen = alternatives[self.rng.randrange(len(alternatives))]
                self.value = chosen.value
                return self

        self.value = compile_asca_rule_fields(
            self.input,
            self.output,
            self.env,
            self.exception,
            group_mappings=self.group_mappings,
            section_index=self.section_index,
            compiler_config=self.compiler_config,
        )
        return self

    def __str__(self) -> str:
        prefix = self.skip_prefix if self.status == "skipped" else self.prefix
        return f"{prefix}{self.value}"

    def _build_alternatives(self) -> list[SoundChangeRule]:
        """Build peer alternatives for optional outputs or parallel ``∅`` output sets."""
        optional = self._build_optional_output_alternatives()
        if optional:
            return optional
        return self._build_parallel_null_set_alternatives()

    def _build_optional_output_alternatives(self) -> list[SoundChangeRule]:
        """Whole-field output set with unpaired input (ticket 66)."""
        if not (is_whole_field_set(self.output) and not is_whole_field_set(self.input)):
            return []
        members = split_braced_set_members(self.output)
        if not members or any(not member or "{" in member for member in members):
            return []
        return [
            SoundChangeRule(
                input=self.input,
                output=member,
                env=self.env,
                exception=self.exception,
                group_mappings=self.group_mappings,
                section_index=self.section_index,
                compiler_config=self.compiler_config,
                detect_alternatives=False,
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
                group_mappings=self.group_mappings,
                section_index=self.section_index,
                compiler_config=self.compiler_config,
                detect_alternatives=False,
            )
            for branch_input, branch_output in branches
        ]


class DiachronicSeries(BaseModel):
    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    parts: list[RulePartBase] = Field(default_factory=list)

    def __init__(
        self,
        section: dict,
        format: str = "asca",
        *,
        group_mappings: dict[str, str] | None = None,
        compiler_config: CompilerConfig | None = None,
    ) -> None:
        if format not in _SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}")

        mappings = {} if group_mappings is None else group_mappings
        config = load_compiler_config() if compiler_config is None else compiler_config
        section_index = str(section.get("index", ""))
        parts: list[RulePartBase] = [RuleTitle(section["index"], section["section"])]
        if section.get("citation"):
            parts.append(RuleCitation(section["citation"]))
        if section.get("comment"):
            parts.append(RuleComment(section["comment"]))
        if section.get("status") != "skipped":
            for rule in section.get("rules") or []:
                if rule.get("status") == "skipped":
                    parts.append(
                        SoundChangeRule(
                            **rule,
                            group_mappings=mappings,
                            section_index=section_index,
                            compiler_config=config,
                        )
                    )
                    continue
                normalized = normalize_index_rule_tilde_fields(rule)
                for step in expand_chained_index_rule(normalized):
                    parts.append(
                        SoundChangeRule(
                            **step,
                            group_mappings=mappings,
                            section_index=section_index,
                            compiler_config=config,
                        )
                    )
        super().__init__(parts=parts)

    @property
    def _parts(self) -> list[RulePartBase]:
        return self.parts

    def __str__(self) -> str:
        return "\n".join(str(part) for part in self.parts) + "\n"

    @property
    def title(self) -> str:
        return self.parts[0].value
