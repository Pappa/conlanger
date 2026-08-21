"""Parse Index Diachronica HTML into the cleaned rule-corpus shape (incremental).

Phase 1: section structure + per-rule ``stages`` split on every ``→`` in the change
spine (whitespace around arrows is trimmed).
Phase 2: optional ``/ env`` then optional ``! exception``
(usual form ``input → output /env ! exception``). Word ``except`` and a second `` / `` are edge-case fallbacks.
Phase 3: first ``<p>`` after ``<h2>`` → section ``citation`` (whole text, cleanup later);
other non-``schg`` paragraphs → ``comments``.
Phase 4: pre-lxml ``<sub>``→Unicode normalisation, then element text extract; **Index
Diachronica correction** overlay by **rule id**; **Manual mapping** on working copy
(``raw`` unchanged). Then **collective subscript** expansion via ``parser_config.yml``
``series_expansions`` on corpus fields (``raw`` unchanged). **Symbol** normalization on
corpus fields only. Remaining Index rule arrows (``→``) in field values become ASCA ``>``.
Chained rules store each spine segment in ``stages``; compile-time expansion is deferred.
Uncertainty glosses
(``sporadic``, ``sometimes``, ``occasionally``, …) are stripped from field values
and recorded as ``sporadic: true``. **Feature matrix** synonym replacement inside ``[...]`` via
``feature_mappings.csv`` (``raw`` unchanged). **IPA character** substitution via
``ipa_mappings.csv`` (``raw`` unchanged). Inline prose stripped for ASCA is captured in optional ``comment`` on each corpus
rule: the first ``;`` on the working line is peeled before structural split, then
field-level glosses and env qualifiers. Index word-internal ``medial`` / ``medially`` env
prose becomes ``env: _`` with boundary ``exception: :{#_, _#}:`` (``apply_medial_env_conditions``).
Class-letter expansion is deferred to compile time (``DiachronicSeries`` +
``group_mappings.csv``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from conlanger.tools.ingest.section_policy import resolve_catch_all_else_rules
from conlanger.tools.ingest.transforms import (
    apply_medial_env_conditions,
    apply_sporadic_qualifier,
    apply_stress_conditions,
    apply_trailing_glosses,
    split_line_semicolon_comment,
)
from conlanger.utils.gloss import (
    is_quoted_prose_paragraph,
)
from conlanger.utils.mappings import (
    FeatureMapping,
    ManualMapping,
    ManualMappingMatch,
    ParserConfig,
    apply_feature_mappings,
    apply_ipa_mappings,
    apply_manual_mappings,
)
from conlanger.utils.parsing import (
    extract_rule_parts,
    extract_text_with_subs,
    finalize_stages_shape,
    load_html_document,
    parse_section_heading,
    strip_whitespace,
)
from conlanger.utils.series import apply_series_expansions
from conlanger.utils.symbols import normalize_symbols


def note_from_element(el, *, source_file: str) -> dict[str, Any]:
    raw = extract_text_with_subs(el)
    line = getattr(el, "sourceline", None) or 0
    return {
        "raw": raw,
        "source": f"{source_file}:{line}",
    }


class IndexDiachronicaParser:
    """Parse Index Diachronica HTML into applier-neutral cleaned-corpus YAML."""

    def __init__(
        self,
        *,
        manual_mappings: list[ManualMapping],
        parser_config: ParserConfig,
        feature_mappings: dict[str, FeatureMapping],
        ipa_mappings: dict[str, str],
        corrections: dict[str, str] | None = None,
    ) -> None:
        self._manual_mappings = manual_mappings
        self._parser_config = parser_config
        self._feature_mappings = feature_mappings
        self._ipa_mappings = ipa_mappings
        self._corrections = corrections or {}
        self.manual_mapping_matches: list[ManualMappingMatch] = []
        self._matched_manual_froms: set[str] = set()
        self._matched_correction_ids: set[str] = set()

    def abbreviations(self) -> dict[str, str]:
        """Global abbreviation table for the cleaned corpus (empty at ingest)."""
        return {}

    def unmatched_manual_mappings(self) -> list[ManualMapping]:
        """Return loaded mappings whose ``from`` never matched during this parse."""
        return [
            row
            for row in self._manual_mappings
            if row.from_text not in self._matched_manual_froms
        ]

    def unmatched_corrections(self) -> list[str]:
        """Return correction rule ids that matched no HTML rule during this parse."""
        return [
            rule_id
            for rule_id in self._corrections
            if rule_id not in self._matched_correction_ids
        ]

    def parse_rule_element(
        self,
        el,
        *,
        source_file: str,
        section_index: str = "",
        section_name: str = "",
        rule_id: str = "",
    ) -> list[dict[str, Any]]:
        raw = extract_text_with_subs(el)
        if rule_id and rule_id in self._corrections:
            raw = self._corrections[rule_id]
            self._matched_correction_ids.add(rule_id)
        line = getattr(el, "sourceline", None) or 0
        source = f"{source_file}:{line}"
        working, hits = apply_manual_mappings(raw, self._manual_mappings)
        for hit in hits:
            self._matched_manual_froms.add(hit.from_text)
            self.manual_mapping_matches.append(
                ManualMappingMatch(
                    section_index=section_index,
                    section_name=section_name,
                    rule_id=rule_id,
                    source=source,
                    manual_mapping=hit.to_text,
                )
            )
        if is_quoted_prose_paragraph(working):
            rule: dict[str, Any] = {
                "stages": [],
                "raw": raw,
                "source": source,
                "comment": raw.strip(),
            }
            if rule_id:
                rule["rule_id"] = rule_id
            return [rule]
        working, rule_comment = split_line_semicolon_comment(working)
        normalized = normalize_symbols(working)
        parts = extract_rule_parts(normalized)
        if parts is None:
            rule = {
                "stages": [],
                "raw": raw,
                "source": source,
            }
            if rule_comment:
                rule["comment"] = rule_comment
            if rule_id:
                rule["rule_id"] = rule_id
            return [rule]
        if rule_comment:
            parts["comment"] = rule_comment
        parts = apply_series_expansions(parts, self._parser_config.series_expansions)
        parts = apply_sporadic_qualifier(parts)
        sporadic = parts.pop("sporadic", False)
        sporadic_flag = {"sporadic": True} if sporadic else {}
        parts = apply_trailing_glosses(parts)
        parts = apply_stress_conditions(parts)
        parts = apply_medial_env_conditions(parts)
        parts = apply_feature_mappings(parts, self._feature_mappings)
        parts = apply_ipa_mappings(parts, self._ipa_mappings)
        parts = finalize_stages_shape(parts)
        if rule_id and rule_id in self._parser_config.skip_rule_ids:
            skipped: dict[str, Any] = {
                "stages": [],
                "raw": raw,
                "source": source,
                "status": "skipped",
                "rule_id": rule_id,
            }
            comment = self._parser_config.skip_rule_comments.get(rule_id)
            if comment:
                skipped["comment"] = comment
            return [skipped]
        rule = {**parts, "raw": raw, "source": source, **sporadic_flag}
        if rule_id:
            rule["rule_id"] = rule_id
        return [rule]

    def parse(
        self,
        html_path: Path,
        *,
        source_file: str | None = None,
    ) -> dict[str, Any]:
        """Parse HTML into ``{abbreviations, sections: [...]}``."""
        source_file = source_file or html_path.name
        self.manual_mapping_matches = []
        self._matched_manual_froms = set()
        self._matched_correction_ids = set()
        root = load_html_document(html_path)
        sections_out: list[dict[str, Any]] = []

        for sec in root.xpath("//section[@id]"):
            h2s = sec.xpath("./h2")
            if not h2s:
                continue
            h2_text = strip_whitespace("".join(h2s[0].itertext()))
            index, name = parse_section_heading(h2_text)
            if not name:
                continue

            rules: list[dict[str, Any]] = []
            citation: str | None = None
            comments: list[dict[str, Any]] = []
            saw_first_p = False

            for p in sec.xpath("./p"):
                cls = p.get("class") or ""
                if "schg" in cls:
                    saw_first_p = True
                    rule_id = p.get("id") or ""
                    rules.extend(
                        self.parse_rule_element(
                            p,
                            source_file=source_file,
                            section_index=index or "",
                            section_name=name,
                            rule_id=rule_id,
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
                section_obj["rules"] = resolve_catch_all_else_rules(rules)
            if index and index in self._parser_config.skip_section_ids:
                section_obj["status"] = "skipped"
            sections_out.append(section_obj)

        return {
            "abbreviations": self.abbreviations(),
            "sections": sections_out,
        }


def parse_rule_element(
    el,
    *,
    source_file: str,
    section_index: str = "",
    parser: IndexDiachronicaParser,
) -> list[dict[str, Any]]:
    """Delegate to an injected parser instance (callers must supply tables)."""
    return parser.parse_rule_element(
        el,
        source_file=source_file,
        section_index=section_index,
    )
