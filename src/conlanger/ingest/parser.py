"""Parse Index Diachronica HTML into the cleaned rule-index shape (incremental).

Phase 1: section structure + per-rule ``stages`` split on every ``→`` in the change
spine (whitespace around arrows is trimmed).
Phase 2: optional ``/ env`` then optional ``! exception``
(usual form ``input → output /env ! exception``). Word ``except`` and a second `` / `` are edge-case fallbacks.
Phase 3: first ``<p>`` after ``<h2>`` → section ``citation`` (whole text, cleanup later);
other non-``schg`` paragraphs → ``comments``.
Phase 4: pre-lxml ``<sub>``→Unicode normalisation, then element text extract (**``raw``**);
**Index Diachronica correction** on working copy; **Manual mapping**; **index rule
normalisation**; **section mapping** (ancestry merge). Then **collective subscript** expansion via
``series_expansions`` on index fields (``raw`` unchanged). **Symbol** normalization on
index fields only. Remaining Index rule arrows (``→``) in field values become ASCA ``>``.
Chained rules store each spine segment in ``stages``; compile-time expansion is deferred.
Uncertainty glosses
(``sporadic``, ``sometimes``, ``occasionally``, …) are stripped from field values
and recorded as ``sporadic: true``. **Feature matrix** synonym replacement inside ``[...]`` via
``feature_mappings.csv`` (``raw`` unchanged). **IPA character** substitution via
``ipa_mappings.csv`` (``raw`` unchanged). Inline prose stripped for ASCA is captured in optional ``comment`` on each index
rule: the first ``;`` on the working line is partitioned before structural split, then
field-level glosses and env qualifiers. Index word-internal ``medial`` / ``medially`` env
prose becomes ``env: _`` with boundary ``exception: #_, _#`` (``apply_medial_env_conditions``).
Index prose **position** env phrases (``final syllables``, ``next to {X}``, ``syllable-final``,
trailing ``, in monosyllables`` qualifiers, …) normalize via ``apply_prose_position_env_conditions``.
Index prose **conditional** env phrases (``utterance-initially``, ``unstressed penult``,
``syllables with …``, stress-matrix tails, …) normalize via
``apply_prose_conditional_env_conditions``.
Index ``//`` env shorthand and prose exception tails normalize via
``apply_double_slash_env_conditions``.
After catch-all ``else`` resolution, nested ``{}`` in ``env`` / ``exception`` /
``stages`` are flattened (``flatten_nested_sets``; ``raw`` unchanged). Class-letter
expansion is deferred to compile time
(``DiachronicSeries`` + ``group_mappings.csv``).
"""

from __future__ import annotations

from typing import Any

from lxml import html

from conlanger.ingest.models.index_models import Index, IndexRule, IndexSection
from conlanger.ingest.models.mappings import (
    ManualMapping,
    ManualMappingMatch,
    ParserConfig,
    apply_manual_mappings,
    apply_section_mappings,
)
from conlanger.ingest.utils.corpus_apply import (
    apply_feature_mappings,
    apply_ipa_mappings,
    apply_series_expansions,
)
from conlanger.ingest.utils.double_slash_env import apply_double_slash_env_conditions
from conlanger.ingest.utils.flatten_nested_sets import (
    flatten_nested_sets_in_section_rules,
)
from conlanger.ingest.utils.index_rule_normalisation import (
    apply_index_rule_normalisation,
)
from conlanger.ingest.utils.prose_conditional_env import (
    apply_prose_conditional_env_conditions,
)
from conlanger.ingest.utils.prose_position_env import (
    apply_prose_position_env_conditions,
)
from conlanger.ingest.utils.section_policy import resolve_catch_all_else_rules
from conlanger.ingest.utils.transforms import (
    apply_medial_env_conditions,
    apply_sporadic_qualifier,
    apply_stress_conditions,
    apply_syllable_position_editorial_strip,
    apply_trailing_glosses,
)
from conlanger.utils.gloss import is_quoted_prose_paragraph
from conlanger.utils.parsing import (
    extract_element_text,
    normalize_sub_tags,
    parse_section_heading,
    strip_whitespace,
)


class IndexDiachronicaParser:
    """Parse Index Diachronica HTML into applier-neutral cleaned-index YAML."""

    def __init__(self, parser_config: ParserConfig | None = None) -> None:
        self._parser_config = parser_config or ParserConfig()
        self._manual_mappings = self._parser_config.manual_mappings
        self._feature_mappings = self._parser_config.feature_mappings
        self._ipa_mappings = self._parser_config.resolved_ipa_mappings()
        self._corrections = self._parser_config.corrections
        self._manual_mapping_matches: list[ManualMappingMatch] = []
        self._matched_manual_froms: set[str] = set()
        self._matched_correction_ids: set[str] = set()
        self._skipped_rules = {rule.id: rule for rule in self._parser_config.skip_rules}
        self._skipped_sections = {
            section.id: section for section in self._parser_config.skip_sections
        }
        self._current_section_index = ""
        self._current_section_name = ""
        self._current_section_mappings: dict[str, str] = {}
        self._source_file = "index"

    def update_current_section(self, index: str, name: str) -> None:
        self._current_section_index = index
        self._current_section_name = name
        self._current_section_mappings = self._parser_config.resolved_section_mappings(
            index
        )

    @property
    def manual_mapping_matches(self) -> list[ManualMappingMatch]:
        return self._manual_mapping_matches

    @property
    def unmatched_manual_mappings(self) -> list[ManualMapping]:
        return [
            row
            for row in self._manual_mappings
            if row.from_text not in self._matched_manual_froms
        ]

    @property
    def unmatched_corrections(self) -> list[str]:
        return [
            rule_id
            for rule_id in self._corrections
            if rule_id not in self._matched_correction_ids
        ]

    def parse_rule_element(
        self,
        el,
        *,
        rule_id: str = "",
    ) -> list[IndexRule]:
        line = getattr(el, "sourceline", None) or 0
        source = f"{self._source_file}:{line}"
        raw = extract_element_text(el)

        return self.parse_rule_string(rule_id, source, raw)

    def parse_rule_string(
        self,
        rule_id: str | None,
        source: str,
        raw: str = "",
    ) -> list[IndexRule]:
        rule = IndexRule(raw=raw, source=source, rule_id=rule_id or None)

        if rule_id and rule_id in self._skipped_rules:
            rule.status = "skipped"
            rule.comment = self._skipped_rules[rule_id].reason
            return [rule]

        if rule_id and rule_id in self._corrections:
            rule.text = self._corrections[rule_id]
            self._matched_correction_ids.add(rule_id)

        rule.text = apply_index_rule_normalisation(rule.text)

        working, hits = apply_manual_mappings(rule.text, self._manual_mappings)
        rule.text = working
        for hit in hits:
            self._matched_manual_froms.add(hit.from_text)
            self._manual_mapping_matches.append(
                ManualMappingMatch(
                    section_index=self._current_section_index,
                    section_name=self._current_section_name,
                    rule_id=rule_id,
                    source=source,
                    from_text=hit.from_text,
                    to_text=hit.to_text,
                )
            )

        rule.text = apply_section_mappings(rule.text, self._current_section_mappings)

        if is_quoted_prose_paragraph(rule.text):
            rule.stages = []
            rule.comment = raw.strip()
            return [rule]

        rule.init()

        rule = apply_series_expansions(rule, self._parser_config.series_expansions)
        rule = apply_sporadic_qualifier(rule)
        rule = apply_trailing_glosses(rule)
        rule = apply_stress_conditions(rule)
        rule = apply_prose_conditional_env_conditions(rule)
        rule = apply_medial_env_conditions(rule)
        rule = apply_prose_position_env_conditions(rule)
        rule = apply_double_slash_env_conditions(rule)
        rule = apply_syllable_position_editorial_strip(rule)
        rule = apply_feature_mappings(rule, self._feature_mappings)
        rule = apply_ipa_mappings(rule, self._ipa_mappings)
        rule = rule.apply_dialects_to_env_fields()

        return [rule]

    def parse(
        self,
        doc: html.HtmlElement,
        *,
        source_file: str = "index",
    ) -> dict[str, Any]:
        """Parse a loaded Index Diachronica HTML tree into a document mapping.

        Root keys: ``name`` (``"Index Diachronica"``) and ``sections`` (sound-change
        sections with nested ``IndexRule`` rows serialized to mappings).
        """
        self._source_file = source_file
        self._manual_mapping_matches = []
        self._matched_manual_froms = set()
        self._matched_correction_ids = set()
        self.update_current_section("", "")
        index = Index(name="Index Diachronica")

        normalised = normalize_sub_tags(doc)

        for sec in normalised.xpath("//section[@id]"):
            h2s = sec.xpath("./h2")
            if not h2s:
                continue
            h2_text = strip_whitespace("".join(h2s[0].itertext()))
            section_index, name = parse_section_heading(h2_text)
            if not name or not section_index:
                continue

            self.update_current_section(section_index, name)

            rules: list[IndexRule] = []
            citation: str | None = None
            comments: list[str] = []

            for p in sec.xpath("./p"):
                cls = p.get("class", "")
                if "schg" in cls:
                    rule_id = p.get("id", "")
                    rules.extend(
                        self.parse_rule_element(
                            p,
                            rule_id=rule_id,
                        )
                    )
                    continue

                comment = strip_whitespace(extract_element_text(p))
                if not comment:
                    continue

                if not citation:
                    citation = comment
                else:
                    comments.append(comment)

            section = IndexSection(section=name, index=section_index)
            if citation is not None:
                section.citation = citation
            if comments:
                section.comments = comments
            if rules:
                section.rules = flatten_nested_sets_in_section_rules(
                    resolve_catch_all_else_rules(rules)
                )
            if section_index and section_index in self._skipped_sections:
                section.status = "skipped"
            index.add_section(section)

        return index.model_dump(exclude_none=True, mode="python")
