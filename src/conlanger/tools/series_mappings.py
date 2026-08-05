"""Extract and load correspondence-series mappings from Index Diachronica HTML."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from lxml import html

from conlanger.tools.parsers import (
    extract_rule_parts,
    extract_text_with_subs,
    parse_section_heading,
    strip_whitespace,
)

DEFAULT_SERIES_MAPPINGS_CSV = (
    Path(__file__).resolve().parents[3] / "data" / "asca" / "series_mappings.csv"
)

# Correspondence-series index: concrete segment base + ordinal subscript (not ₀, not ₓ).
_CORRESPONDENCE_INDEX_RE = re.compile(
    r"(?<![A-Z])([a-zA-Zæøåɑɡɢ]+)([₁₂₃₄₅₆₇₈₉])"
)
_COLLECTIVE_TOKEN_RE = re.compile(r"(?<![A-Z])([a-zA-Z]+)ₓ")
_POSITIONAL_SLOT_RE = re.compile(r"^[A-Z][₁₂₃₄₅₆₇₈₉]$")
_IDENTITY_SUBSCRIPT_RE = re.compile(r"^[A-Za-z]₀$")
# Whitespace split respecting {...} groups (single level).
_RULE_TOKEN_RE = re.compile(
    r"\{[^{}]+\}|[A-Za-zÀ-ÿɑæøåɡɢʃʒθðβγχħʕʔ]+(?:\[[^\]]+\])?|[^\s{}]+"
)
# ASCA grouping letters cannot host a digit suffix (s1 → S + reference 1).
_ASCA_GROUPING_LETTERS = frozenset("CSOPFLNGV")

_SUBSCRIPT_TO_ASCII = str.maketrans("₁₂₃₄₅₆₇₈₉", "123456789")

# Any token containing an Index subscript digit/letter (includes compounds like ``eh₂``, ``CV₁``).
_SUBSCRIPT_TOKEN_RE = re.compile(r"[A-Za-zæøåɑɡɢ]*[₀₁₂₃₄₅₆₇₈₉ₓ]+")


@dataclass(frozen=True)
class SeriesMapping:
    section_index: str
    token: str
    asca_target: str
    source: str = ""
    notes: str = ""


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


def classify_subscript_token(token: str) -> str:
    """Classify a subscript-bearing token for coverage accounting."""
    if is_identity_subscript_token(token):
        return "identity"
    if is_positional_slot_token(token):
        return "positional"
    if is_collective_subscript_token(token):
        return "collective"
    if is_correspondence_series_token(token):
        return "correspondence"
    if _CORRESPONDENCE_INDEX_RE.search(token):
        return "compound"
    if "ₓ" in token or "₀" in token or re.search(r"[₁₂₃₄₅₆₇₈₉]", token):
        return "other"
    return "none"


def in_scope_series_token(token: str) -> bool:
    """Whether ticket-28 extraction applies to this token."""
    return classify_subscript_token(token) in {"correspondence", "collective"}


def is_positional_slot_token(token: str) -> bool:
    return bool(_POSITIONAL_SLOT_RE.match(token))


def is_identity_subscript_token(token: str) -> bool:
    return bool(_IDENTITY_SUBSCRIPT_RE.match(token))


def is_collective_subscript_token(token: str) -> bool:
    base = token[:-1] if token.endswith("ₓ") else ""
    return (
        len(token) >= 2
        and token.endswith("ₓ")
        and base.isalpha()
        and base.islower()
    )


def is_correspondence_series_token(token: str) -> bool:
    if is_positional_slot_token(token) or is_identity_subscript_token(token):
        return False
    if is_collective_subscript_token(token):
        return True
    match = _CORRESPONDENCE_INDEX_RE.fullmatch(token)
    if not match:
        return False
    base = match.group(1)
    # Correspondence-series indices attach to concrete (lowercase) segments, not class letters.
    return base.islower()


def find_subscript_tokens(text: str) -> set[str]:
    """Return subscript-bearing tokens appearing in rule field text."""
    return {
        match.group(0)
        for match in _SUBSCRIPT_TOKEN_RE.finditer(text)
        if match.group(0)
    }


def find_correspondence_series_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for base, sub in _CORRESPONDENCE_INDEX_RE.findall(text):
        tokens.add(f"{base}{sub}")
    for base in _COLLECTIVE_TOKEN_RE.findall(text):
        tokens.add(f"{base}ₓ")
    return tokens


def section_index_prefixes(section_index: str) -> list[str]:
    parts = [part for part in section_index.split(".") if part]
    return [".".join(parts[:index]) for index in range(len(parts), 0, -1)]


def asca_digit_segment(base: str, subscript_digit: str) -> str:
    """Map Index ``base`` + subscript digit to an ASCA-parseable segment name."""
    ascii_digit = subscript_digit.translate(_SUBSCRIPT_TO_ASCII)
    if base.upper() in _ASCA_GROUPING_LETTERS:
        # ``s₁`` cannot become ``s1`` (ASCA reads ``S`` + reference ``1``).
        return f"f{ascii_digit}"
    return f"{base}{ascii_digit}"


def lookup_series_target(
    section_index: str,
    token: str,
    rows: list[SeriesMapping],
) -> SeriesMapping | None:
    keyed = {(row.section_index, row.token): row for row in rows}
    for prefix in section_index_prefixes(section_index):
        hit = keyed.get((prefix, token))
        if hit is not None:
            return hit
    return keyed.get(("*", token))


def load_series_mappings(path: Path | None = None) -> list[SeriesMapping]:
    csv_path = DEFAULT_SERIES_MAPPINGS_CSV if path is None else Path(path)
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    missing = {"section_index", "token", "asca_target"} - set(df.columns)
    if missing:
        raise ValueError(
            f"series mappings CSV missing required columns: {sorted(missing)}"
        )
    has_source = "source" in df.columns
    has_notes = "notes" in df.columns
    return [
        SeriesMapping(
            section_index=row.section_index,
            token=row.token,
            asca_target=row.asca_target,
            source=row.source if has_source else "",
            notes=row.notes if has_notes else "",
        )
        for row in df.itertuples(index=False)
    ]


def write_series_mappings_csv(rows: list[SeriesMapping], path: Path) -> None:
    deduped = _dedupe_rows(rows)
    deduped.sort(key=lambda row: (row.section_index, row.token))
    df = pd.DataFrame(
        [
            {
                "section_index": row.section_index,
                "token": row.token,
                "asca_target": row.asca_target,
                "source": row.source,
                "notes": row.notes,
            }
            for row in deduped
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def _dedupe_rows(rows: list[SeriesMapping]) -> list[SeriesMapping]:
    """Keep the first row per (section_index, token); extraction order = priority."""
    seen: set[tuple[str, str]] = set()
    out: list[SeriesMapping] = []
    for row in rows:
        key = (row.section_index, row.token)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


_SUBSCRIPT_CHARS = frozenset("₀₁₂₃₄₅₆₇₈₉ₓ")


def _tokenize_rule_side(text: str) -> list[str]:
    rough = [token for token in _RULE_TOKEN_RE.findall(text.strip()) if token.strip()]
    merged: list[str] = []
    for token in rough:
        if merged and len(token) == 1 and token in _SUBSCRIPT_CHARS:
            merged[-1] += token
        else:
            merged.append(token)
    return merged


def _is_series_side_token(token: str) -> bool:
    if token.startswith("{") and token.endswith("}"):
        inner = token[1:-1]
        parts = [part.strip() for part in inner.split(",") if part.strip()]
        return bool(parts) and all(is_correspondence_series_token(part) for part in parts)
    return is_correspondence_series_token(token)


def _is_asca_side_token(token: str) -> bool:
    if token in {"∅", "Ø", "0"}:
        return True
    if token.startswith("*"):
        return False
    if token.startswith("{") and token.endswith("}"):
        inner = token[1:-1]
        parts = [part.strip() for part in inner.split(",") if part.strip()]
        return bool(parts) and all(_is_asca_side_token(part) for part in parts)
    if is_correspondence_series_token(token):
        return False
    if is_positional_slot_token(token) or is_identity_subscript_token(token):
        return False
    if re.fullmatch(r"[A-Z](?:\[[^\]]+\])?", token):
        return False
    if re.search(r"[₀₁₂₃₄₅₆₇₈₉ₓ]", token):
        return False
    return True


def infer_parallel_rule_mappings(
    raw_rule: str,
    *,
    section_index: str,
    source: str,
) -> list[SeriesMapping]:
    """Infer series→segment mappings from parallel input/output tokens in one rule."""
    parts = extract_rule_parts(raw_rule)
    if parts is None:
        return []
    input_tokens = _tokenize_rule_side(parts["input"])
    output_tokens = _tokenize_rule_side(parts["output"])
    if not input_tokens or len(input_tokens) != len(output_tokens):
        return []
    if not all(_is_series_side_token(token) for token in input_tokens):
        return []
    if not all(_is_asca_side_token(token) for token in output_tokens):
        return []

    rows: list[SeriesMapping] = []
    for inp, out in zip(input_tokens, output_tokens, strict=True):
        if inp.startswith("{") and inp.endswith("}"):
            continue
        if not is_correspondence_series_token(inp) or is_collective_subscript_token(inp):
            continue
        rows.append(
            SeriesMapping(
                section_index=section_index,
                token=inp,
                asca_target=out,
                source=source,
                notes="inferred from parallel rule I/O",
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
    input_tokens = _tokenize_rule_side(parts["input"])
    output_tokens = _tokenize_rule_side(parts["output"])
    if len(input_tokens) != 1 or len(output_tokens) != 1:
        return []
    inp, out = input_tokens[0], output_tokens[0]
    if not is_correspondence_series_token(inp) or is_collective_subscript_token(inp):
        return []
    if not _is_asca_side_token(out):
        return []
    return [
        SeriesMapping(
            section_index=section_index,
            token=inp,
            asca_target=out,
            source=source,
            notes="inferred from rule I/O",
        )
    ]


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
                notes="collective subscript over correspondence-series members from citation",
            )
        )
    return rows


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
        rule_rows: list[SeriesMapping] = []

        for p in sec.xpath("./p"):
            cls = p.get("class") or ""
            if "schg" in cls:
                saw_first_p = True
                raw = extract_text_with_subs(p)
                line = getattr(p, "sourceline", None) or 0
                source = f"{source_file}:{line}"
                rule_rows.extend(
                    infer_parallel_rule_mappings(
                        raw, section_index=section_index, source=source
                    )
                )
                rule_rows.extend(
                    infer_singleton_rule_mappings(
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
            rows.extend(
                _table_series_rows(
                    section_index,
                    table_el,
                    source_file=source_file,
                )
            )

        rows.extend(rule_rows)

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
                by_section[section_index].update(find_correspondence_series_tokens(field))
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
    csv_path = DEFAULT_SERIES_MAPPINGS_CSV if mappings_csv is None else Path(mappings_csv)
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
        family: (counts[0], counts[1]) for family, counts in sorted(family_counts.items())
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
    fields = [parts["input"], parts["output"]]
    if parts.get("env"):
        fields.append(parts["env"])
    if parts.get("exception"):
        fields.append(parts["exception"])
    return fields


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

    pct = lambda num, den: f"{100 * num / den:.1f}%" if den else "n/a"
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
        "Use **in-scope rule coverage** (correspondence-series + collective subscripts only) "
        "— not the raw rule-token total, which includes positional slots (`C₁`), identity "
        "subscripts (`V₀`), and compounds (`eh₂`) handled by other tickets.",
        "",
        f"- **HTML citation/table definitions mapped:** "
        f"{audit.html_defined_mapped}/{audit.html_defined_pairs} "
        f"({pct(audit.html_defined_mapped, audit.html_defined_pairs)})",
        f"- **In-scope tokens in rules mapped:** "
        f"{audit.in_scope_rule_mapped}/{audit.in_scope_rule_pairs} "
        f"({pct(audit.in_scope_rule_mapped, audit.in_scope_rule_pairs)})",
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
            "Families **6** (Afro-Asiatic) and **17** (Indo-European) are the ticket-28 "
            "benchmarks: citation/table rows at §6 and §17, plus rule-inferred overrides "
            "in subsections.",
            "",
            "## Inference methods",
            "",
            "1. **Section citation** — prose or comments listing series members (e.g. Afro-Asiatic §6).",
            "2. **Phonology inventory tables** — cells listing indexed tokens (e.g. PIE laryngeals §17).",
            "3. **Parallel rule I/O** — equal-length input/output chains mapping series members to IPA segments.",
            "4. **Singleton rule I/O** — single indexed input token mapping to one output segment.",
            "5. **Collective subscript** — `Xₓ` expands to the set of `Xₙ` members declared in the same section citation.",
            "",
            "ASCA targets use `{base}{ascii_digit}` segment names (e.g. `h₁` → `h1`). "
            "For bases that collide with ASCA grouping letters (`S`, `C`, …), "
            "targets use `f{N}` placeholders (e.g. `s₁` → `f1`).",
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
                    + (", ".join(f"`{t}`" for t in mapped_sorted) if mapped_sorted else "_none_"),
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
            f"- In-scope rule token occurrences: **{audit.in_scope_rule_pairs}** "
            f"(mapped **{audit.in_scope_rule_mapped}**, "
            f"**{pct(audit.in_scope_rule_mapped, audit.in_scope_rule_pairs)}**)",
            f"- Out-of-scope subscript tokens (positional / identity / compound): "
            f"**{audit.out_of_scope_rule_pairs}**",
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
