"""Extract correspondence-series mappings from Index Diachronica HTML."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lxml import html

from conlanger.utils.file_io import (
    DEFAULT_SERIES_MAPPINGS_CSV,
    load_series_mappings,
    write_series_mappings_csv,
)
from conlanger.utils.parsing import (
    extract_rule_parts,
    extract_text_with_subs,
    parse_section_heading,
    strip_whitespace,
)
from conlanger.utils.series import (
    _CORRESPONDENCE_INDEX_RE,
    SeriesMapping,
    asca_digit_segment,
    classify_subscript_token,
    find_correspondence_series_tokens,
    find_subscript_tokens,
    in_scope_series_token,
    is_collective_subscript_token,
    is_correspondence_series_token,
    is_identity_subscript_token,
    is_positional_slot_token,
    lookup_series_target,
)

DEFAULT_SERIES_MAPPINGS_REPORT = (
    Path(__file__).resolve().parents[3]
    / ".scratch"
    / "cleaned-rule-corpus"
    / "series-mappings-coverage.md"
)

# Whitespace split respecting {...} groups (single level).
_RULE_TOKEN_RE = re.compile(
    r"\{[^{}]+\}|[A-Za-zÀ-ÿɑæøåɡɢʃʒθðβγχħʕʔəɨʊɪɛɔ]+(?:\[[^\]]+\])?|[^\s{}]+"
)
_SUBSCRIPT_CHARS = frozenset("₀₁₂₃₄₅₆₇₈₉ₓ")
_LENGTH_MARKS = frozenset("ːˑ")
# Trailing Index glosses like ``(not sure…)`` or ``“(reduced)”``.
_TRAILING_GLOSS_RE = re.compile(r"(?:\s*\([^)]*\)\s*|\s*[\"“][^\"”]*[\"”]\s*)+$")


@dataclass(frozen=True)
class SeriesExtractionAudit:
    """Confidence metrics for HTML → ``series_mappings.csv`` extraction."""

    csv_rows: int
    html_defined_pairs: int
    html_defined_mapped: int
    in_scope_rule_pairs: int
    in_scope_rule_mapped: int
    out_of_scope_rule_pairs: int
    in_scope_gaps: tuple[tuple[str, str], ...]
    family_in_scope: dict[str, tuple[int, int]]

    @property
    def html_definition_coverage(self) -> float:
        if not self.html_defined_pairs:
            return 1.0
        return self.html_defined_mapped / self.html_defined_pairs

    @property
    def in_scope_rule_coverage(self) -> float:
        if not self.in_scope_rule_pairs:
            return 1.0
        return self.in_scope_rule_mapped / self.in_scope_rule_pairs


def update_series_mappings_from_html(
    html_path: Path,
    *,
    csv_path: Path = DEFAULT_SERIES_MAPPINGS_CSV,
    report_path: Path = DEFAULT_SERIES_MAPPINGS_REPORT,
) -> int:
    """Extract correspondence-series mappings from HTML; write CSV and coverage report."""
    rows = extract_series_mappings_from_html(html_path)
    write_series_mappings_csv(rows, csv_path)
    write_coverage_report(html_path, csv_path, report_path)
    return len(rows)


def _strip_trailing_gloss(text: str) -> str:
    return _TRAILING_GLOSS_RE.sub("", text.strip()).strip()


def _tokenize_rule_side(text: str) -> list[str]:
    cleaned = _strip_trailing_gloss(text)
    rough = [token for token in _RULE_TOKEN_RE.findall(cleaned) if token.strip()]
    merged: list[str] = []
    for token in rough:
        if (
            merged
            and len(token) == 1
            and (token in _SUBSCRIPT_CHARS or token in _LENGTH_MARKS)
        ):
            merged[-1] += token
        else:
            merged.append(token)
    return merged


def _brace_parts(token: str) -> list[str] | None:
    if not (token.startswith("{") and token.endswith("}")):
        return None
    parts = [part.strip() for part in token[1:-1].split(",") if part.strip()]
    return parts or None


def _is_asca_side_token(token: str) -> bool:
    if token in {"∅", "Ø", "0"}:
        return True
    if token.startswith("*"):
        return False
    parts = _brace_parts(token)
    if parts is not None:
        return all(_is_asca_side_token(part) for part in parts)
    if is_correspondence_series_token(token):
        return False
    if is_positional_slot_token(token) or is_identity_subscript_token(token):
        return False
    if re.fullmatch(r"[A-Z](?:\[[^\]]+\])?", token):
        return False
    return not re.search(r"[₀₁₂₃₄₅₆₇₈₉ₓ]", token)


def _series_members_from_input_token(token: str) -> list[str]:
    """Return correspondence-series members from a plain or braced input token."""
    parts = _brace_parts(token)
    if parts is not None:
        return [
            part
            for part in parts
            if is_correspondence_series_token(part)
            and not is_collective_subscript_token(part)
        ]
    if is_correspondence_series_token(token) and not is_collective_subscript_token(
        token
    ):
        return [token]
    return []


def _is_brace_input_token(token: str) -> bool:
    return _brace_parts(token) is not None


def _rule_io_strings(parts: dict[str, Any]) -> tuple[str, str]:
    stages = [stage for stage in parts.get("stages", []) if stage and stage.strip()]
    if len(stages) < 2:
        return "", ""
    return stages[0], stages[-1]


def infer_parallel_rule_mappings(
    raw_rule: str,
    *,
    section_index: str,
    source: str,
) -> list[SeriesMapping]:
    """Infer series→segment mappings from parallel input/output tokens in one rule.

    Emits only aligned series↔ASCA pairs. Non-series inputs (class letters, plain
    segments) and braced mixes are skipped per slot so one bad token does not
    discard the whole chain. Braced inputs expand each series member to the
    aligned output target.
    """
    parts = extract_rule_parts(raw_rule)
    if parts is None:
        return []
    inp, out = _rule_io_strings(parts)
    if not inp or not out:
        return []
    input_tokens = _tokenize_rule_side(inp)
    output_tokens = _tokenize_rule_side(out)
    if not input_tokens or len(input_tokens) != len(output_tokens):
        return []

    rows: list[SeriesMapping] = []
    for inp_tok, out_tok in zip(input_tokens, output_tokens, strict=True):
        if not _is_asca_side_token(out_tok):
            continue
        from_brace = _is_brace_input_token(inp_tok)
        notes = (
            "inferred from braced parallel rule I/O"
            if from_brace
            else "inferred from parallel rule I/O"
        )
        for member in _series_members_from_input_token(inp_tok):
            rows.append(
                SeriesMapping(
                    section_index=section_index,
                    token=member,
                    asca_target=out_tok,
                    source=source,
                    notes=notes,
                )
            )
    return rows


def infer_singleton_rule_mappings(
    raw_rule: str,
    *,
    section_index: str,
    source: str,
) -> list[SeriesMapping]:
    """Infer mappings from ``series_token → segment`` rules with one input token."""
    parts = extract_rule_parts(raw_rule)
    if parts is None:
        return []
    inp, out = _rule_io_strings(parts)
    if not inp or not out:
        return []
    input_tokens = _tokenize_rule_side(inp)
    output_tokens = _tokenize_rule_side(out)
    if len(input_tokens) != 1 or len(output_tokens) != 1:
        return []
    inp_tok, out_tok = input_tokens[0], output_tokens[0]
    if not _is_asca_side_token(out_tok):
        return []
    members = _series_members_from_input_token(inp_tok)
    if not members:
        return []
    from_brace = _is_brace_input_token(inp_tok)
    notes = "inferred from braced rule I/O" if from_brace else "inferred from rule I/O"
    return [
        SeriesMapping(
            section_index=section_index,
            token=member,
            asca_target=out_tok,
            source=source,
            notes=notes,
        )
        for member in members
    ]


def infer_attested_series_digit_mappings(
    raw_rule: str,
    *,
    section_index: str,
    source: str,
) -> list[SeriesMapping]:
    """Emit digit-segment rows for correspondence-series tokens attested in a rule.

    Lowest-priority fallback when citation/table/I/O inference did not define a
    target (e.g. Slavic ``æ₂``/``i₂`` only appearing in an output set, or
    compounds named only in an environment gloss).
    """
    parts = extract_rule_parts(raw_rule)
    if parts is None:
        return []
    fields: list[str] = [
        stage for stage in parts.get("stages", []) if stage and stage.strip()
    ]
    for key in ("env", "exception"):
        value = parts.get(key)
        if value and str(value).strip():
            fields.append(str(value))

    rows: list[SeriesMapping] = []
    seen: set[str] = set()
    for field in fields:
        for token in sorted(find_correspondence_series_tokens(field)):
            if token in seen:
                continue
            if not is_correspondence_series_token(token):
                continue
            if is_collective_subscript_token(token):
                continue
            match = _CORRESPONDENCE_INDEX_RE.fullmatch(token)
            if not match:
                continue
            seen.add(token)
            base, sub = match.group(1), match.group(2)
            rows.append(
                SeriesMapping(
                    section_index=section_index,
                    token=token,
                    asca_target=asca_digit_segment(base, sub),
                    source=source,
                    notes="series member attested in rule fields",
                )
            )
    return rows


def _citation_series_rows(
    section_index: str,
    prose: str,
    *,
    source: str,
) -> list[SeriesMapping]:
    rows: list[SeriesMapping] = []
    for base, sub in _CORRESPONDENCE_INDEX_RE.findall(prose):
        token = f"{base}{sub}"
        if not is_correspondence_series_token(token):
            continue
        rows.append(
            SeriesMapping(
                section_index=section_index,
                token=token,
                asca_target=asca_digit_segment(base, sub),
                source=source,
                notes="section citation defines correspondence-series member",
            )
        )
    return rows


def _table_series_rows(
    section_index: str,
    table_el,
    *,
    source_file: str,
) -> list[SeriesMapping]:
    rows: list[SeriesMapping] = []
    line = getattr(table_el, "sourceline", None) or 0
    source = f"{source_file}:{line}"
    cell_text = extract_text_with_subs(table_el)
    for base, sub in _CORRESPONDENCE_INDEX_RE.findall(cell_text):
        token = f"{base}{sub}"
        if not is_correspondence_series_token(token):
            continue
        rows.append(
            SeriesMapping(
                section_index=section_index,
                token=token,
                asca_target=asca_digit_segment(base, sub),
                source=source,
                notes="phonology inventory table lists correspondence-series member",
            )
        )
    return rows


def _collective_rows_for_section(
    section_index: str,
    member_rows: list[SeriesMapping],
    *,
    source: str,
) -> list[SeriesMapping]:
    by_base: dict[str, list[SeriesMapping]] = defaultdict(list)
    for row in member_rows:
        if is_collective_subscript_token(row.token):
            continue
        match = _CORRESPONDENCE_INDEX_RE.fullmatch(row.token)
        if not match:
            continue
        by_base[match.group(1)].append(row)

    rows: list[SeriesMapping] = []
    for base, members in sorted(by_base.items()):
        if len(members) < 2:
            continue
        targets = sorted({member.asca_target for member in members})
        collective = f"{base}ₓ"
        rows.append(
            SeriesMapping(
                section_index=section_index,
                token=collective,
                asca_target="{" + ",".join(targets) + "}",
                source=source,
                notes="collective subscript over correspondence-series members",
            )
        )
    return rows


def _dedupe_rows(rows: list[SeriesMapping]) -> list[SeriesMapping]:
    """Keep the best row per (section_index, token); prefer bare I/O over braces."""
    priority = {
        "section citation defines correspondence-series member": 0,
        "phonology inventory table lists correspondence-series member": 0,
        "collective subscript over correspondence-series members": 1,
        "inferred from rule I/O": 2,
        "inferred from parallel rule I/O": 3,
        "inferred from braced rule I/O": 4,
        "inferred from braced parallel rule I/O": 5,
        "series member attested in rule fields": 6,
    }

    def rank(row: SeriesMapping) -> int:
        return priority.get(row.notes, 50)

    best: dict[tuple[str, str], SeriesMapping] = {}
    for row in rows:
        key = (row.section_index, row.token)
        existing = best.get(key)
        if existing is None or rank(row) < rank(existing):
            best[key] = row

    out: list[SeriesMapping] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row.section_index, row.token)
        if key in seen:
            continue
        seen.add(key)
        out.append(best[key])
    return out


def extract_series_mappings_from_html(
    html_path: Path,
    *,
    source_file: str | None = None,
) -> list[SeriesMapping]:
    """Survey HTML and extract section-scoped correspondence-series mappings."""
    source_file = source_file or html_path.name
    parser = html.HTMLParser(encoding="utf-8")
    doc = html.parse(str(html_path), parser=parser)
    root = doc.getroot()
    rows: list[SeriesMapping] = []

    for sec in root.xpath("//section[@id]"):
        h2s = sec.xpath("./h2")
        if not h2s:
            continue
        h2_text = strip_whitespace("".join(h2s[0].itertext()))
        section_index, _name = parse_section_heading(h2_text)
        if not section_index:
            continue

        citation_text: str | None = None
        citation_source = ""
        saw_first_p = False
        rule_io_rows: list[SeriesMapping] = []
        attestation_rows: list[SeriesMapping] = []

        for p in sec.xpath("./p"):
            cls = p.get("class") or ""
            if "schg" in cls:
                saw_first_p = True
                raw = extract_text_with_subs(p)
                line = getattr(p, "sourceline", None) or 0
                source = f"{source_file}:{line}"
                rule_io_rows.extend(
                    infer_parallel_rule_mappings(
                        raw, section_index=section_index, source=source
                    )
                )
                rule_io_rows.extend(
                    infer_singleton_rule_mappings(
                        raw, section_index=section_index, source=source
                    )
                )
                attestation_rows.extend(
                    infer_attested_series_digit_mappings(
                        raw, section_index=section_index, source=source
                    )
                )
                continue

            note = extract_text_with_subs(p)
            if not note:
                continue
            if not saw_first_p:
                citation_text = note
                line = getattr(p, "sourceline", None) or 0
                citation_source = f"{source_file}:{line}"
                saw_first_p = True

        if citation_text:
            citation_rows = _citation_series_rows(
                section_index,
                citation_text,
                source=citation_source,
            )
            rows.extend(citation_rows)
            rows.extend(
                _collective_rows_for_section(
                    section_index,
                    citation_rows,
                    source=citation_source,
                )
            )

        for table_el in sec.xpath("./table"):
            table_rows = _table_series_rows(
                section_index,
                table_el,
                source_file=source_file,
            )
            rows.extend(table_rows)
            if table_rows:
                line = getattr(table_el, "sourceline", None) or 0
                rows.extend(
                    _collective_rows_for_section(
                        section_index,
                        table_rows,
                        source=f"{source_file}:{line}",
                    )
                )

        rows.extend(rule_io_rows)
        rows.extend(attestation_rows)

    return _dedupe_rows(rows)


def survey_subscript_tokens_in_html(
    html_path: Path,
    *,
    source_file: str | None = None,
) -> dict[str, set[str]]:
    """Return correspondence-series tokens used in rules, keyed by section index."""
    source_file = source_file or html_path.name
    parser = html.HTMLParser(encoding="utf-8")
    doc = html.parse(str(html_path), parser=parser)
    root = doc.getroot()
    by_section: dict[str, set[str]] = defaultdict(set)

    for sec in root.xpath("//section[@id]"):
        h2s = sec.xpath("./h2")
        if not h2s:
            continue
        h2_text = strip_whitespace("".join(h2s[0].itertext()))
        section_index, _name = parse_section_heading(h2_text)
        if not section_index:
            continue
        for p in sec.xpath("./p[@class and contains(@class, 'schg')]"):
            raw = extract_text_with_subs(p)
            for field in _rule_fields(raw):
                by_section[section_index].update(
                    find_correspondence_series_tokens(field)
                )
    return dict(by_section)


def survey_all_subscript_tokens_in_html(
    html_path: Path,
    *,
    source_file: str | None = None,
) -> dict[str, set[str]]:
    """Return all subscript-bearing tokens in rule fields, keyed by section index."""
    source_file = source_file or html_path.name
    parser = html.HTMLParser(encoding="utf-8")
    doc = html.parse(str(html_path), parser=parser)
    root = doc.getroot()
    by_section: dict[str, set[str]] = defaultdict(set)

    for sec in root.xpath("//section[@id]"):
        h2s = sec.xpath("./h2")
        if not h2s:
            continue
        h2_text = strip_whitespace("".join(h2s[0].itertext()))
        section_index, _name = parse_section_heading(h2_text)
        if not section_index:
            continue
        for p in sec.xpath("./p[@class and contains(@class, 'schg')]"):
            raw = extract_text_with_subs(p)
            for field in _rule_fields(raw):
                by_section[section_index].update(find_subscript_tokens(field))
    return dict(by_section)


def survey_html_defined_series(
    html_path: Path,
    *,
    source_file: str | None = None,
) -> dict[str, set[str]]:
    """Return in-scope series tokens declared in section citations or inventory tables."""
    source_file = source_file or html_path.name
    parser = html.HTMLParser(encoding="utf-8")
    doc = html.parse(str(html_path), parser=parser)
    root = doc.getroot()
    by_section: dict[str, set[str]] = defaultdict(set)

    for sec in root.xpath("//section[@id]"):
        h2s = sec.xpath("./h2")
        if not h2s:
            continue
        h2_text = strip_whitespace("".join(h2s[0].itertext()))
        section_index, _name = parse_section_heading(h2_text)
        if not section_index or section_index == "5":
            continue

        saw_first_p = False
        for p in sec.xpath("./p"):
            cls = p.get("class") or ""
            if "schg" in cls:
                saw_first_p = True
                continue
            note = extract_text_with_subs(p)
            if not note:
                continue
            if not saw_first_p:
                for token in find_correspondence_series_tokens(note):
                    if in_scope_series_token(token):
                        by_section[section_index].add(token)
                saw_first_p = True

        for table_el in sec.xpath("./table"):
            cell_text = extract_text_with_subs(table_el)
            for token in find_correspondence_series_tokens(cell_text):
                if in_scope_series_token(token):
                    by_section[section_index].add(token)

    return dict(by_section)


def audit_series_extraction(
    html_path: Path,
    mappings_csv: Path | None = None,
) -> SeriesExtractionAudit:
    """Compute confidence metrics for HTML extraction vs ``series_mappings.csv``."""
    csv_path = (
        DEFAULT_SERIES_MAPPINGS_CSV if mappings_csv is None else Path(mappings_csv)
    )
    rows = load_series_mappings(csv_path)
    defined = survey_html_defined_series(html_path)
    rules = survey_all_subscript_tokens_in_html(html_path)

    html_defined_pairs = 0
    html_defined_mapped = 0
    in_scope_rule_pairs = 0
    in_scope_rule_mapped = 0
    out_of_scope_rule_pairs = 0
    gaps: list[tuple[str, str]] = []
    family_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for section_index, tokens in defined.items():
        for token in tokens:
            html_defined_pairs += 1
            if lookup_series_target(section_index, token, rows) is not None:
                html_defined_mapped += 1

    for section_index, tokens in rules.items():
        for token in tokens:
            if in_scope_series_token(token):
                in_scope_rule_pairs += 1
                if lookup_series_target(section_index, token, rows) is not None:
                    in_scope_rule_mapped += 1
                else:
                    gaps.append((section_index, token))
                top = section_index.split(".", 1)[0]
                family_counts[top][0] += 1
                if lookup_series_target(section_index, token, rows) is not None:
                    family_counts[top][1] += 1
            else:
                out_of_scope_rule_pairs += 1

    family_in_scope = {
        family: (counts[0], counts[1])
        for family, counts in sorted(family_counts.items())
    }

    return SeriesExtractionAudit(
        csv_rows=len(rows),
        html_defined_pairs=html_defined_pairs,
        html_defined_mapped=html_defined_mapped,
        in_scope_rule_pairs=in_scope_rule_pairs,
        in_scope_rule_mapped=in_scope_rule_mapped,
        out_of_scope_rule_pairs=out_of_scope_rule_pairs,
        in_scope_gaps=tuple(sorted(gaps)),
        family_in_scope=family_in_scope,
    )


def _rule_fields(raw_rule: str) -> list[str]:
    parts = extract_rule_parts(raw_rule)
    if parts is None:
        return [raw_rule]
    inp, out = _rule_io_strings(parts)
    fields = [inp, out]
    if parts.get("env"):
        fields.append(parts["env"])
    if parts.get("exception"):
        fields.append(parts["exception"])
    return [field for field in fields if field]


def write_coverage_report(
    html_path: Path,
    mappings_csv: Path,
    report_path: Path,
) -> None:
    """Emit mapped vs unmapped correspondence-series tokens by section."""
    rows = load_series_mappings(mappings_csv)
    audit = audit_series_extraction(html_path, mappings_csv)
    mapped_by_section: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        mapped_by_section[row.section_index].add(row.token)

    used_by_section = survey_subscript_tokens_in_html(html_path)
    section_names = _section_names_from_html(html_path)

    def pct(num: int, den: int) -> str:
        return f"{100 * num / den:.1f}%" if den else "n/a"

    family_lines = [
        f"| {family} | {total} | {mapped} | {pct(mapped, total)} |"
        for family, (total, mapped) in audit.family_in_scope.items()
        if total
    ]

    lines = [
        "# Correspondence-series mapping coverage",
        "",
        f"HTML source: `{html_path.name}`",
        f"Mappings: `{mappings_csv.name}` ({audit.csv_rows} rows)",
        "",
        "## Extraction confidence",
        "",
        (
            "Use **in-scope rule coverage** (correspondence-series + collective subscripts only) "
            "— not the raw rule-token total, which includes positional slots (`C₁`), identity "
            "subscripts (`V₀`), and uppercase/template compounds (`CV₁`, `Hₓ`) deferred elsewhere."
        ),
        "",
        (
            f"- **HTML citation/table definitions mapped:** "
            f"{audit.html_defined_mapped}/{audit.html_defined_pairs} "
            f"({pct(audit.html_defined_mapped, audit.html_defined_pairs)})"
        ),
        (
            f"- **In-scope tokens in rules mapped:** "
            f"{audit.in_scope_rule_mapped}/{audit.in_scope_rule_pairs} "
            f"({pct(audit.in_scope_rule_mapped, audit.in_scope_rule_pairs)})"
        ),
        f"- **Out-of-scope subscript tokens in rules (excluded):** {audit.out_of_scope_rule_pairs}",
        f"- **In-scope gaps remaining:** {len(audit.in_scope_gaps)}",
        "",
        "### By top-level section family",
        "",
        "| Family | In-scope rule tokens | Mapped | Coverage |",
        "| --- | ---: | ---: | ---: |",
    ]
    lines.extend(family_lines or ["| _none_ | 0 | 0 | n/a |"])
    lines.extend(
        [
            "",
            (
                "Families **6** (Afro-Asiatic) and **17** (Indo-European) are the historical "
                "ticket-28 benchmarks; ticket 65 also tracks Austronesian (§10) and meta "
                "vowel-shift (§46) in-scope coverage."
            ),
            "",
            "## Inference methods",
            "",
            "1. **Section citation** — prose or comments listing series members (e.g. Afro-Asiatic §6).",
            "2. **Phonology inventory tables** — cells listing indexed tokens (e.g. PIE laryngeals §17).",
            "3. **Parallel rule I/O** — equal-length input/output chains mapping series members to IPA segments (including mixed/non-series slots and braced alternates).",
            "4. **Singleton rule I/O** — single indexed input token (or braced series set) mapping to one output segment.",
            "5. **Collective subscript** — `Xₓ` expands to the set of `Xₙ` members declared in the same section citation or inventory table.",
            "6. **Attested digit fallback** — correspondence-series tokens named in rule fields without an I/O target get `{base}{digit}` ASCA names (lowest priority).",
            "",
            (
                "ASCA targets use `{base}{ascii_digit}` segment names (e.g. `h₁` → `h1`). "
                "For bases that collide with ASCA grouping letters (`S`, `C`, …), "
                "targets use `f{N}` placeholders (e.g. `s₁` → `f1`)."
            ),
            "",
            "## By section",
            "",
            "| Section | Name | Tokens in rules | Mapped | Unmapped |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )

    all_rules = survey_all_subscript_tokens_in_html(html_path)
    out_of_scope_lines: list[str] = []
    for section_index in sorted(all_rules, key=_section_sort_key):
        name = section_names.get(section_index, "")
        for token in sorted(all_rules[section_index]):
            if not in_scope_series_token(token):
                out_of_scope_lines.append(
                    f"- `{token}` ({classify_subscript_token(token)}) — "
                    f"section {section_index} ({name})"
                )

    all_sections = sorted(
        set(used_by_section) | set(mapped_by_section),
        key=_section_sort_key,
    )
    total_used = 0
    total_mapped = 0
    detail_lines: list[str] = []

    for section_index in all_sections:
        used = used_by_section.get(section_index, set())
        mapped = set()
        for token in used:
            if lookup_series_target(section_index, token, rows) is not None:
                mapped.add(token)
        unmapped = sorted(used - mapped)
        total_used += len(used)
        total_mapped += len(mapped)
        name = section_names.get(section_index, "")
        lines.append(
            f"| {section_index} | {name} | {len(used)} | {len(mapped)} | {len(unmapped)} |"
        )
        if used:
            mapped_sorted = sorted(mapped)
            detail_lines.extend(
                [
                    f"### {section_index} {name}",
                    "",
                    f"- Mapped ({len(mapped_sorted)}): "
                    + (
                        ", ".join(f"`{t}`" for t in mapped_sorted)
                        if mapped_sorted
                        else "_none_"
                    ),
                    f"- Unmapped ({len(unmapped)}): "
                    + (", ".join(f"`{t}`" for t in unmapped) if unmapped else "_none_"),
                    "",
                ]
            )
    lines.extend(
        [
            "",
            "## Token detail (sections with rules)",
            "",
        ]
    )
    if detail_lines:
        lines.extend(detail_lines)
    else:
        lines.append("_No correspondence-series tokens in rule fields._")

    lines.extend(
        [
            "## Summary",
            "",
            f"- Sections with correspondence-series rules: **{len(used_by_section)}**",
            (
                f"- In-scope rule token occurrences: **{audit.in_scope_rule_pairs}** "
                f"(mapped **{audit.in_scope_rule_mapped}**, "
                f"**{pct(audit.in_scope_rule_mapped, audit.in_scope_rule_pairs)}**)"
            ),
            (
                f"- Out-of-scope subscript tokens (positional / identity / compound): "
                f"**{audit.out_of_scope_rule_pairs}**"
            ),
            "",
            "## In-scope gaps",
            "",
        ]
    )
    if audit.in_scope_gaps:
        for section_index, token in audit.in_scope_gaps:
            name = section_names.get(section_index, "")
            lines.append(f"- `{token}` — section {section_index} ({name})")
    else:
        lines.append("_None._")

    lines.extend(["", "## Out-of-scope subscript tokens (all sections)", ""])
    if out_of_scope_lines:
        lines.extend(out_of_scope_lines)
    else:
        lines.append("_None._")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _section_sort_key(section_index: str) -> tuple:
    return tuple(int(part) for part in section_index.split("."))


def _section_names_from_html(html_path: Path) -> dict[str, str]:
    parser = html.HTMLParser(encoding="utf-8")
    doc = html.parse(str(html_path), parser=parser)
    names: dict[str, str] = {}
    for sec in doc.getroot().xpath("//section[@id]"):
        h2s = sec.xpath("./h2")
        if not h2s:
            continue
        h2_text = strip_whitespace("".join(h2s[0].itertext()))
        section_index, name = parse_section_heading(h2_text)
        if section_index:
            names[section_index] = name
    return names
