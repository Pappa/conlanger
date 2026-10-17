"""Compile-time operator config (group mappings, series maps, position templates)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from conlanger.ingest.utils.series import section_index_prefixes


class PositionTemplates(BaseModel):
    """Relation-keyed ASCA projection templates for ``IndexContext.position``."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    adjacent_to: str = "{v}_, _{v}"
    near: str = "{v}_, _{v}"
    in_: str = Field(alias="in", default="in {v}")


class CompilerConfig(BaseModel):
    """Fat compile-time config: group mappings plus series token maps."""

    model_config = ConfigDict(frozen=True)

    group_mappings: dict[str, str] = Field(default_factory=dict)
    series_mappings_global: dict[str, str] = Field(default_factory=dict)
    series_mappings_sections: dict[str, dict[str, str]] = Field(default_factory=dict)
    sample_sporadic: bool = True
    sample_dialect: bool = True
    position_templates: PositionTemplates = Field(default_factory=PositionTemplates)

    @field_validator("position_templates", mode="before")
    @classmethod
    def _coerce_position_templates(cls, value: object) -> object:
        if value is None:
            return {}
        return value

    def resolved_series_mappings(self, section_index: str) -> dict[str, str]:
        """Global token map with longest-prefix section rows overlaid."""
        result = dict(self.series_mappings_global)
        if not section_index:
            return result
        for prefix in section_index_prefixes(section_index):
            section_map = self.series_mappings_sections.get(prefix)
            if section_map:
                result.update(section_map)
        return result

    def lookup_series_mapping(self, section_index: str, token: str) -> str | None:
        """Return the target for ``token`` via section longest-prefix, else ``global``."""
        return self.resolved_series_mappings(section_index).get(token)
