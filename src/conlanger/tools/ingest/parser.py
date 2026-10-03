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
rule: the first ``;`` on the working line is peeled before structural split, then
field-level glosses and env qualifiers. Index word-internal ``medial`` / ``medially`` env
prose becomes ``env: _`` with boundary ``exception: :{#_, _#}:`` (``apply_medial_env_conditions``).
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

from conlanger.tools.ingest.double_slash_env import apply_double_slash_env_conditions
from conlanger.tools.ingest.flatten_nested_sets import (
    flatten_nested_sets_in_section_rules,
)
from conlanger.tools.ingest.index_models import IndexRule
from conlanger.tools.ingest.index_rule_normalisation import (
    apply_index_rule_normalisation,
)
from conlanger.tools.ingest.prose_conditional_env import (
    apply_prose_conditional_env_conditions,
)
from conlanger.tools.ingest.prose_position_env import (
    apply_prose_position_env_conditions,
)
from conlanger.tools.ingest.section_policy import resolve_catch_all_else_rules
from conlanger.tools.ingest.transforms import (
    apply_medial_env_conditions,
    apply_sporadic_qualifier,
    apply_stress_conditions,
    apply_syllable_position_editorial_strip,
    apply_trailing_glosses,
    split_line_semicolon_comment,
)
from conlanger.utils.gloss import (
    apply_dialects_to_context,
    is_quoted_prose_paragraph,
)
from conlanger.utils.mappings import (
    ManualMapping,
    ManualMappingMatch,
    ParserConfig,
    SkipRule,
    apply_feature_mappings,
    apply_ipa_mappings,
    apply_manual_mappings,
    apply_section_mappings,
)
from conlanger.utils.parsing import (
    extract_element_text,
    extract_missing_arrow_rule_parts,
    extract_rule_parts,
    finalize_stages_shape,
    parse_section_heading,
    strip_whitespace,
)
from conlanger.utils.series import apply_series_expansions
from conlanger.utils.symbols import normalize_symbols


def note_from_element(el, *, source_file: str) -> dict[str, Any]:
    raw = extract_element_text(el)
    line = getattr(el, "sourceline", None) or 0
    return {
        "raw": raw,
        "source": f"{source_file}:{line}",
    }


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
        source_file: str = "index",
        section_index: str = "",
        section_name: str = "",
        rule_id: str = "",
        skipped_rule: SkipRule | None = None,
    ) -> list[dict[str, Any]]:
        line = getattr(el, "sourceline", None) or 0
        source = f"{source_file}:{line}"
        raw = extract_element_text(el)

        return self.parse_rule_string(
            rule_id, section_index, section_name, source, skipped_rule, raw
        )

    def parse_rule_string(
        self,
        rule_id: str | None,
        section_index: str,
        section_name: str,
        source: str,
        skipped_rule: SkipRule | None = None,
        raw: str = "",
    ) -> dict[str, Any]:

        if skipped_rule:
            skipped = IndexRule(
                stages=[],
                raw=raw,
                source=source,
                status="skipped",
                rule_id=rule_id,
                comment=skipped_rule.reason,
            )
            return [skipped.to_index_dict()]

        working = raw

        if rule_id and rule_id in self._corrections:
            working = self._corrections[rule_id]
            self._matched_correction_ids.add(rule_id)

        working = apply_index_rule_normalisation(working)

        working, hits = apply_manual_mappings(working, self._manual_mappings)
        for hit in hits:
            self._matched_manual_froms.add(hit.from_text)
            self._manual_mapping_matches.append(
                ManualMappingMatch(
                    section_index=section_index,
                    section_name=section_name,
                    rule_id=rule_id,
                    source=source,
                    from_text=hit.from_text,
                    to_text=hit.to_text,
                )
            )

        working = apply_section_mappings(working, section_index, self._parser_config)

        if is_quoted_prose_paragraph(working):
            quoted = IndexRule(
                stages=[],
                raw=raw,
                source=source,
                comment=raw.strip(),
                rule_id=rule_id or None,
            )
            return [quoted.to_index_dict()]
        working, rule_comment = split_line_semicolon_comment(working)
        normalized = normalize_symbols(working)
        parts = extract_rule_parts(normalized)
        if parts is None:
            parts = extract_missing_arrow_rule_parts(normalized)
        if rule_comment:
            parts["comment"] = rule_comment
        parts = apply_series_expansions(parts, self._parser_config.series_expansions)
        parts = apply_sporadic_qualifier(parts)
        sporadic = parts.pop("sporadic", False)
        parts = apply_trailing_glosses(parts)
        parts = apply_stress_conditions(parts)
        parts = apply_prose_conditional_env_conditions(parts)
        parts = apply_medial_env_conditions(parts)
        parts = apply_prose_position_env_conditions(parts)
        parts = apply_double_slash_env_conditions(parts)
        parts = apply_syllable_position_editorial_strip(parts)
        parts = apply_feature_mappings(parts, self._feature_mappings)
        parts = apply_ipa_mappings(parts, self._ipa_mappings)
        parts = finalize_stages_shape(parts)

        if "env" in parts:
            parts["env"] = apply_dialects_to_context(parts["env"])
        if "exception" in parts:
            parts["exception"] = apply_dialects_to_context(parts["exception"])

        index_rule = IndexRule.from_parse_fields(
            parts,
            raw=raw,
            source=source,
            sporadic=sporadic,
            rule_id=rule_id or None,
        )
        return [index_rule.to_index_dict()]

    def parse(
        self,
        doc: html.HtmlElement,
        *,
        source_file: str,
    ) -> dict[str, Any]:
        """Parse a loaded Index Diachronica HTML tree into ``{sections: [...]}``."""
        self._manual_mapping_matches = []
        self._matched_manual_froms = set()
        self._matched_correction_ids = set()
        sections_out: list[dict[str, Any]] = []
        skip_rules = {rule.id: rule for rule in self._parser_config.skip_rules}
        skip_sections = {
            section.id: section for section in self._parser_config.skip_sections
        }

        for sec in doc.xpath("//section[@id]"):
            h2s = sec.xpath("./h2")
            if not h2s:
                continue
            h2_text = strip_whitespace("".join(h2s[0].itertext()))
            index, name = parse_section_heading(h2_text)
            if not name or not index:
                continue

            rules: list[dict[str, Any]] = []
            citation: str | None = None
            comments: list[dict[str, Any]] = []
            saw_first_p = False

            for p in sec.xpath("./p"):
                cls = p.get("class", "")
                if "schg" in cls:
                    saw_first_p = True
                    rule_id = p.get("id", "")
                    rules.extend(
                        self.parse_rule_element(
                            p,
                            source_file=source_file,
                            section_index=index,
                            section_name=name,
                            rule_id=rule_id,
                            skipped_rule=skip_rules.get(rule_id),
                        )
                    )
                    continue

                note = note_from_element(p, source_file=source_file)
                if not note["raw"]:
                    continue

                if not saw_first_p:
                    citation = note["raw"]
                    saw_first_p = True
                else:
                    comments.append(note)

            section_obj: dict[str, Any] = {
                "section": name,
                "index": index,
            }
            if citation is not None:
                section_obj["citation"] = citation
            if comments:
                section_obj["comments"] = comments
            if rules:
                section_obj["rules"] = flatten_nested_sets_in_section_rules(
                    resolve_catch_all_else_rules(rules)
                )
            if index and index in skip_sections:
                section_obj["status"] = "skipped"
            sections_out.append(section_obj)

        return {"sections": sections_out}
