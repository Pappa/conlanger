#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from lxml import html, etree  # type: ignore
from xml.sax.saxutils import escape as xml_escape

# Project root (…/conlanger)
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "notebooks" / "data"
HTML_PATH = DATA_DIR / "index_diachronica.html"
OUTPUT_PATH = DATA_DIR / "output.xml"

# Basic subscript mapping for digits and common letters
SUBSCRIPT_MAP = str.maketrans({
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
    "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ",
    "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ"
})

def esc_text(s: str) -> str:
    # Escape text node content
    return xml_escape(s)

def esc_attr(s: str) -> str:
    # Escape attribute value content including quotes
    return xml_escape(s, {'"': '&quot;', "'": '&apos;'})


def to_subscript(text: str) -> str:
    return "".join(ch.translate(SUBSCRIPT_MAP) if ch.lower() in "0123456789aehijklmnoprstuvx" else ch for ch in text)


def extract_text_with_subs(el) -> str:
    """Extract text, converting <sub>...</sub> to unicode subscripts."""
    parts: List[str] = []

    def walk(node):
        if node.text:
            if getattr(node, "tag", None) == "sub":
                parts.append(to_subscript(node.text))
            else:
                parts.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                parts.append(child.tail)

    walk(el)
    text = "".join(parts)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def expand_optional_length(token: str) -> str:
    def repl_optional(m: re.Match) -> str:
        base = m.group(1)
        return f"{{ {base}, {base}:[+ long] }}"
    token = re.sub(r"([^{}/\s()]+)\(ː\)", repl_optional, token)
    token = token.replace("ː", ":[+ long]")
    return token


def normalize_features(text: str) -> str:
    text = expand_optional_length(text)
    text = re.sub(r"\[\s*\+\s*voiced\s*\]", "[+ voice]", text)
    text = re.sub(r"\[\s*-\s*voiced\s*\]", "[- voice]", text)
    text = re.sub(r"\s+:\s*\[", ":[", text)
    # Ensure a colon before any feature bracket directly after a token (e.g., C[+ voice] -> C:[+ voice])
    # Don't add a colon if the character before '[' is already a colon
    text = re.sub(r"(?<!:)([^\s{}\(\)/:])\s*(\[)", r"\1:\2", text)
    # Compact feature brackets: [+ voice] -> [+voice], [- long] -> [-long]
    def _compact_features(m: re.Match) -> str:
        inner = m.group(1)
        inner = re.sub(r"([+\-])\s+([A-Za-z\.]+)", r"\1\2", inner)
        inner = re.sub(r"\s*,\s*", ", ", inner)
        return f"[{inner}]"
    text = re.sub(r"\[\s*([^\]]+?)\s*\]", _compact_features, text)
    return text.strip()


def normalize_env_fragment(env: str) -> str:
    """
    Ensure environment/exception fragments avoid putting '_' inside sets.
    Transform patterns like '{ _i, _i:[+long] }' -> '_{ i, i:[+long] }'.
    """
    s = env
    # Fast-path: whole string is a set of underscore-prefixed items
    m_whole = re.match(r"^\{\s*(_[^}]*(?:\s*,\s*_[^}]*)*)\s*\}$", s)
    if m_whole:
        items = [x.strip().lstrip("_").strip() for x in m_whole.group(1).split(",")]
        return "_{ " + ", ".join(items) + " }"
    def _lift_underscore_set(m: re.Match) -> str:
        before = m.group(1) or ""
        items_str = m.group(2)
        items = [x.strip() for x in items_str.split(",") if x.strip()]
        if items and all(it.startswith("_") for it in items):
            items = [it.lstrip("_").strip() for it in items]
            prefix_underscore = "" if before.strip().endswith("_") else "_"
            return f"{before}{prefix_underscore}{{ " + ", ".join(items) + " }}"
        return m.group(0)
    s = re.sub(r"([^{]|^)\{\s*([^}]*)\s*\}", _lift_underscore_set, s)
    s = re.sub(r"__+", "_", s)
    return s.strip()


def split_mapping_and_context(rule_text: str) -> Tuple[str, Optional[str], Optional[str]]:
    exception = None
    m_exc = re.search(r",\s*except\s+(.*)$", rule_text, flags=re.IGNORECASE)
    if m_exc:
        exception = m_exc.group(1).strip()
        rule_text = rule_text[: m_exc.start()].rstrip()
    env = None
    if " / " in rule_text:
        mapping_part, env_part = rule_text.split(" / ", 1)
        env = env_part.strip()
    else:
        mapping_part = rule_text.strip()
    return mapping_part.strip(), env, exception


def split_chain_mappings(mapping_text: str) -> List[Tuple[str, str]]:
    parts = [p.strip() for p in mapping_text.split("→")]
    parts = [p for p in parts if p]
    if len(parts) < 2:
        return []
    return [(parts[i], parts[i + 1]) for i in range(len(parts) - 1)]


def format_rule_xml(input_str: str, output_str: str, env: Optional[str], exception: Optional[str], indent: str = "\t\t") -> str:
    lines = [f'{indent}<rule>']
    lines.append(f'{indent}\t<input>{esc_text(input_str)}</input>')
    lines.append(f'{indent}\t<output>{esc_text(output_str)}</output>')
    if env:
        lines.append(f'{indent}\t<env>{esc_text(env)}</env>')
    if exception:
        lines.append(f'{indent}\t<exception>{esc_text(exception)}</exception>')
    lines.append(f'{indent}</rule>')
    return "\n".join(lines)


def parse_section(sec_el) -> Tuple[str, str, str]:
    h2 = sec_el.xpath("./h2")
    if not h2:
        return "", "", ""
    h2_text = "".join(h2[0].itertext()).strip()
    m = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", h2_text)
    if not m:
        idx = ""
        name = h2_text
    else:
        idx, name = m.group(1).strip(), m.group(2).strip()

    non_rule_ps = sec_el.xpath("./p[not(contains(@class,'rule'))]")
    cite_texts: List[str] = []
    for p in non_rule_ps:
        txt = extract_text_with_subs(p)
        if txt:
            cite_texts.append(txt)
    cite_combined = " ".join(cite_texts).strip()

    rule_ps = sec_el.xpath("./p[contains(@class,'rule')]")

    if not cite_combined and not rule_ps:
        return idx, name, f'\t<section index="{esc_attr(idx)}" name="{esc_attr(name)}" />'

    xml_lines: List[str] = [f'\t<section index="{esc_attr(idx)}" name="{esc_attr(name)}">']
    if cite_combined:
        xml_lines.append(f"\t\t<cite>{esc_text(cite_combined)}</cite>")

    for rp in rule_ps:
        raw = extract_text_with_subs(rp)
        if not raw:
            continue
        text = normalize_features(raw)
        mapping_text, env, exception = split_mapping_and_context(text)
        if env:
            env = normalize_env_fragment(normalize_features(env))
        if exception:
            exception = normalize_env_fragment(normalize_features(exception))
        pairs = split_chain_mappings(mapping_text)
        if not pairs:
            continue
        for inp, out in pairs:
            inp_n = normalize_features(inp)
            out_n = normalize_features(out)
            xml_lines.append(format_rule_xml(inp_n, out_n, env, exception))

    # Escape attributes in opening tag — rebuild header with escaped attrs
    xml_lines[0] = f'\t<section index="{esc_attr(idx)}" name="{esc_attr(name)}">'
    xml_lines.append("\t</section>")
    return idx, name, "\n".join(xml_lines)


def build_document(root) -> str:
    sections = root.xpath("//section[contains(@class,'showtarget')]")
    xml_lines: List[str] = ["<document>"]
    for sec in sections:
        _idx, _name, body = parse_section(sec)
        if body:
            xml_lines.append(body)
    xml_lines.append("</document>")
    return "\n".join(xml_lines) + "\n"


def main() -> int:
    if not HTML_PATH.exists():
        print(f"ERROR: HTML not found at {HTML_PATH}", file=sys.stderr)
        return 1
    html_text = HTML_PATH.read_text(encoding="utf-8", errors="ignore")
    try:
        root = html.document_fromstring(html_text)
    except Exception:
        root = html.fromstring(html_text)
    xml_text = build_document(root)
    # Validate XML is well-formed
    try:
        etree.fromstring(xml_text.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        print("ERROR: Generated XML is not well-formed:", file=sys.stderr)
        print(str(e), file=sys.stderr)
        # Write the file for inspection, but exit with failure
        OUTPUT_PATH.write_text(xml_text, encoding="utf-8")
        return 2
    OUTPUT_PATH.write_text(xml_text, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

