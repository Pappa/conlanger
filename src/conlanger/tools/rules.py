from __future__ import annotations

import random
from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from conlanger.tools.compile.asca.chains import expand_chained_index_rule
from conlanger.tools.compile.asca.parallel import (
    expand_parallel_output_null_branches_from_tokens,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_compile_fields
from conlanger.tools.compile.asca.structures import join_asca_rule_fields
from conlanger.tools.compile.asca.tilde import normalize_index_rule_tilde_fields
from conlanger.tools.compile.compile_fields import RuleEnv, RuleInput, RuleOutput
from conlanger.tools.compile.field_tokens import (
    FieldToken,
    is_optional_output_shape,
    peel_embedded_output_env,
    render_field_tokens,
    set_token_members,
)
from conlanger.utils.mappings import CompilerConfig

_SUPPORTED_FORMATS = frozenset({"asca"})
_SPORADIC_APPLY_PROBABILITY = 0.5


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

    input: RuleInput = Field(default_factory=RuleInput)
    output: RuleOutput = Field(default_factory=RuleOutput)
    env: RuleEnv | None = None
    exception: RuleEnv | None = None
    status: str | None = None
    sporadic: bool = False
    sporadic_skipped: bool = False
    raw: str = ""

    alternatives: list[SoundChangeRule] = Field(default_factory=list)
    compiler_config: CompilerConfig = Field(
        default_factory=CompilerConfig, exclude=True, repr=False
    )
    section_index: str = Field(default="", exclude=True, repr=False)
    rng: random.Random = Field(default_factory=random.Random, exclude=True, repr=False)
    detect_alternatives: bool = Field(default=True, exclude=True, repr=False)
    sample_sporadic: bool = Field(default=False, exclude=True, repr=False)

    @field_validator("input", mode="before")
    @classmethod
    def coerce_input(cls, value: object) -> object:
        if isinstance(value, str):
            return RuleInput.from_raw(value)
        return value

    @field_validator("output", mode="before")
    @classmethod
    def coerce_output(cls, value: object) -> object:
        if isinstance(value, str):
            return RuleOutput.from_raw(value)
        return value

    @field_validator("env", "exception", mode="before")
    @classmethod
    def coerce_env(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return RuleEnv.from_raw(value)
        return value

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

        if (
            self.sporadic
            and self.sample_sporadic
            and self.rng.random() >= _SPORADIC_APPLY_PROBABILITY
        ):
            self.sporadic_skipped = True

        if self.sporadic_skipped:
            self.input, self.output, self.env, self.exception = (
                compile_asca_rule_compile_fields(
                    self.input,
                    self.output,
                    self.env,
                    self.exception,
                    section_index=self.section_index,
                    compiler_config=self.compiler_config,
                )
            )
            self.value = self._join_compiled_fields()
            return self

        if self.detect_alternatives:
            alternatives = self._build_alternatives()
            self.alternatives = alternatives
            if alternatives:
                chosen = alternatives[self.rng.randrange(len(alternatives))]
                self.input = chosen.input
                self.output = chosen.output
                self.env = chosen.env
                self.exception = chosen.exception
                self.value = self._join_compiled_fields()
                return self

        self.input, self.output, self.env, self.exception = (
            compile_asca_rule_compile_fields(
                self.input,
                self.output,
                self.env,
                self.exception,
                section_index=self.section_index,
                compiler_config=self.compiler_config,
            )
        )
        self.value = self._join_compiled_fields()
        return self

    def _join_compiled_fields(self) -> str:
        return join_asca_rule_fields(
            self.input.compiled,
            self.output.compiled,
            self.env.compiled if self.env is not None else None,
            self.exception.compiled if self.exception is not None else None,
        )

    def __str__(self) -> str:
        if self.status == "skipped":
            return f"{self.skip_prefix}{self.raw}"
        if self.sporadic_skipped:
            return f"{self.skip_prefix}{self._join_compiled_fields()}"
        return f"{self.prefix}{self._join_compiled_fields()}"

    def _build_alternatives(self) -> list[SoundChangeRule]:
        """Build peer alternatives for optional outputs or parallel ``∅`` output sets."""
        output_tokens, peeled_env = peel_embedded_output_env(self.output.tokens)
        env = self.env
        if env is None and peeled_env is not None:
            env = RuleEnv.from_raw(peeled_env)
        optional = self._build_optional_output_alternatives(output_tokens, env)
        if optional:
            return optional
        return self._build_parallel_null_set_alternatives(output_tokens, env)

    def _build_optional_output_alternatives(
        self,
        output_tokens: tuple[FieldToken, ...],
        env: RuleEnv | None,
    ) -> list[SoundChangeRule]:
        """Whole-field output set with unpaired input (ticket 66)."""
        if not is_optional_output_shape(self.input.tokens, output_tokens):
            return []
        members = set_token_members(output_tokens[0])
        return [
            SoundChangeRule(
                input=self.input,
                output=RuleOutput.from_raw(member),
                env=env,
                exception=self.exception,
                section_index=self.section_index,
                compiler_config=self.compiler_config,
                detect_alternatives=False,
            )
            for member in members
        ]

    def _build_parallel_null_set_alternatives(
        self,
        output_tokens: tuple[FieldToken, ...],
        env: RuleEnv | None,
    ) -> list[SoundChangeRule]:
        """Paired parallel columns with ``∅`` inside output sets (ticket 81)."""
        branches = expand_parallel_output_null_branches_from_tokens(
            self.input.tokens,
            output_tokens,
        )
        if branches is None:
            return []
        return [
            SoundChangeRule(
                input=RuleInput.from_raw(render_field_tokens(branch_input)),
                output=RuleOutput.from_raw(render_field_tokens(branch_output)),
                env=env,
                exception=self.exception,
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
        compiler_config: CompilerConfig | None = None,
        sample_sporadic: bool = True,
        rng: random.Random | None = None,
    ) -> None:
        if format not in _SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}")

        config = compiler_config or CompilerConfig()
        section_index = str(section.get("index", ""))
        series_rng = rng or random.Random()
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
                            section_index=section_index,
                            compiler_config=config,
                            sample_sporadic=sample_sporadic,
                            rng=series_rng,
                        )
                    )
        super().__init__(parts=parts)

    @property
    def _parts(self) -> list[RulePartBase]:
        return self.parts

    @classmethod
    def from_parts(cls, parts: list[RulePartBase]) -> Self:
        """Wrap pre-built parts without re-parsing index YAML."""
        return cls.model_construct(parts=parts)

    def __str__(self) -> str:
        return "\n".join(str(part) for part in self.parts) + "\n"

    @property
    def title(self) -> str:
        return self.parts[0].value
