#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import json

from lxml import html, etree  # type: ignore
from xml.sax.saxutils import escape as xml_escape

# Project root (…/conlanger)
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "notebooks" / "data"
HTML_PATH = DATA_DIR / "index_diachronica.html"
OUTPUT_PATH = DATA_DIR / "output.xml"
SERIES_MAP_PATH = DATA_DIR / "series_mapping.yaml"
UNMAPPED_SERIES_REPORT = DATA_DIR / "unmapped_series.csv"

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


def strip_whitespace(text: str) -> str:
    text = re.sub(r"[\n|\r]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


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
    text = strip_whitespace(text)
    return text


def remove_unicode_subscripts(text: str) -> str:
    # Remove all Unicode subscript digits/letters that ASCA cannot parse (e.g., s₁ → s)
    return re.sub(r"[\u2080-\u209F]+", "", text)


def normalize_parenthetic_diacritics(text: str) -> str:
    # Convert parenthetic diacritics to proper IPA diacritics
    # (ʼ) -> ʼ, (w) or (ʷ) -> ʷ, (j) or (ʲ) -> ʲ
    text = re.sub(r"\(\s*ʼ\s*\)", "ʼ", text)
    text = re.sub(r"\(\s*[wʷ]\s*\)", "ʷ", text)
    text = re.sub(r"\(\s*[jʲ]\s*\)", "ʲ", text)
    return text


def add_affricate_ties(text: str) -> str:
    # Ensure common affricates are tied (ASCA requires tie/caret)
    replacements = [
        (r"(?<![\^͡])tʃ", "t͡ʃ"),
        (r"(?<![\^͡])dʒ", "d͡ʒ"),
        (r"(?<![\^͡])ts", "t͡s"),
        (r"(?<![\^͡])dz", "d͡z"),
        (r"(?<![\^͡])tɬ", "t͡ɬ"),
        (r"(?<![\^͡])dɮ", "d͡ɮ"),
        (r"(?<![\^͡])tɕ", "t͡ɕ"),
        (r"(?<![\^͡])dʑ", "d͡ʑ"),
    ]
    out = text
    for pat, rep in replacements:
        out = re.sub(pat, rep, out)
    return out


def fix_voiced_ejective(text: str) -> str:
    # Replace impossible voiced ejectives with their voiceless counterparts
    text = text.replace("bʼ", "pʼ")
    text = text.replace("dʼ", "tʼ")
    text = text.replace("ɡʼ", "kʼ")
    return text


def normalize_macron_vowels(text: str) -> str:
    macron_map = {
        "ā": "a:[+ long]", "ē": "e:[+ long]", "ī": "i:[+ long]",
        "ō": "o:[+ long]", "ū": "u:[+ long]", "ȳ": "y:[+ long]",
        "Ā": "A:[+ long]", "Ē": "E:[+ long]", "Ī": "I:[+ long]",
        "Ō": "O:[+ long]", "Ū": "U:[+ long]", "Ȳ": "Y:[+ long]",
    }
    return "".join(macron_map.get(ch, ch) for ch in text)


def propagate_set_diacritics(text: str) -> str:
    # Apply trailing diacritic to each member of a set: {x,ɢ}ʷ -> {xʷ, ɢʷ}
    def repl(m: re.Match) -> str:
        items = [strip_whitespace(x) for x in m.group(1).split(",") if strip_whitespace(x)]
        dia = m.group(2)
        items = [f"{it}{dia}" for it in items]
        return "{ " + ", ".join(items) + " }"
    return re.sub(r"\{\s*([^}]*)\s*\}\s*([ʷʲʼ])", repl, text)


def diacriticize_glides(text: str) -> str:
    # Convert labialized/palatalized sequences Cw/Cj to Cʷ/Cʲ, but avoid vowels
    # Basic heuristic: a base consonant followed immediately by w/j
    def rep(match: re.Match) -> str:
        base = match.group(1)
        glide = match.group(2)
        return base + ("ʷ" if glide == "w" else "ʲ")
    return re.sub(r"([ptkbdgɡqɢcszʃʒxɣχhmnɲŋlrɾɬɮfvθðʈɖɟɲɕʑtʃdztsɕʑcɟɸβ])([wj])\b", rep, text)


def map_group_pharyngeal(text: str) -> str:
    # Cˤ -> C:[+phargyn], VCˤ -> V C:[+phargyn]
    return re.sub(r"\b([COSPFLNGV])ˤ", r"\1:[+phargyn]", text)


def strip_textual_env(env: str) -> str:
    # Remove English descriptors from environments
    bad_phrases = [
        r"\bat word boundaries\b", r"\belse\b", r"\bmedially\b", r"\bin coda\b",
        r"\bin southern regions\b", r"\bwhen stressed\b", r"\bshort only\b",
        r"\bdepending on the environment.*$", r"\bthe article.*$", r"\bsometimes.*$",
        r"\bwhen not near emphatics\b", r"\bnear emphatics\b", r"\bnear\b.*$",
        r"\bthough.*$", r"\bif .* elsewhere in the word\b", r"\bonly when short\b",
        r"\bconjectured.*$", r"\bin Form .* verbs.*$", r"\bin verbs.*$",
    ]
    s = env
    for pat in bad_phrases:
        s = re.sub(pat, "", s, flags=re.IGNORECASE)
    s = s.replace("“", "").replace("”", "").replace('"', "")
    s = strip_whitespace(s)
    if s == "#":
        # Default ambiguous single boundary to start of word
        s = "#_"
    return s


def transform_optionals_in_env(env: str) -> str:
    # Turn (X)Y into {XY, Y} and Z(ʼ) into {Zʼ, Z}
    def rep1(m: re.Match) -> str:
        opt = m.group(1)
        foll = m.group(2)
        return "{ " + opt + foll + ", " + foll + " }"
    s = re.sub(r"\(\s*([^\s{}()])\s*\)([^\s{}()])", rep1, env)
    # Z(ʼ) -> {Zʼ, Z}
    s = re.sub(r"([^\s{}()])\(\s*ʼ\s*\)", r"{ \1ʼ, \1 }", s)
    return s


def strip_trailing_annotations(text: str) -> str:
    # Remove trailing commentary like " + $(V)C$ suffix"
    return re.sub(r"\s+\+\s+.*$", "", text)


def normalize_general(text: str) -> str:
    # Apply general normalizations before feature/env handling
    t = text
    t = strip_trailing_annotations(t)
    t = remove_unicode_subscripts(t)
    t = normalize_parenthetic_diacritics(t)
    t = normalize_macron_vowels(t)
    t = propagate_set_diacritics(t)
    t = diacriticize_glides(t)
    t = add_affricate_ties(t)
    t = fix_voiced_ejective(t)
    # Map non-ASCA feature names in a coarse way (handled again in normalize_features)
    t = t.replace("sibilant", "strident")
    t = map_group_pharyngeal(t)
    return strip_whitespace(t)

def expand_optional_length(token: str) -> str:
    def repl_optional(m: re.Match) -> str:
        base = m.group(1)
        return f"{{ {base}, {base}:[+ long] }}"
    token = re.sub(r"([^{}/\s()]+)\(ː\)", repl_optional, token)
    token = token.replace("ː", ":[+ long]")
    return token


def normalize_features(text: str) -> str:
    text = expand_optional_length(text)
    # Map 'sibilant' -> 'strident' (ASCA uses 'strident' feature)
    text = text.replace("sibilant", "strident")
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

#
# Series label resolution (per-section mappings)
#

def load_series_map(path: Path) -> Dict[str, Dict[str, str]]:
    """
    Load a mapping of section -> { series_label: replacement }.
    Supports YAML (if PyYAML present) or JSON; returns {} if file missing/unreadable.
    """
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8", errors="ignore")
    # Try YAML
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(raw)
        return data or {}
    except Exception:
        pass
    # Try JSON
    try:
        data = json.loads(raw)
        return data or {}
    except Exception:
        return {}


def section_ancestry(section_idx: str) -> List[str]:
    """
    Return ancestry list from most specific to least: '6.1.2.3' -> ['6.1.2.3','6.1.2','6.1','6']
    """
    parts = section_idx.split(".")
    chain = []
    for i in range(len(parts), 0, -1):
        chain.append(".".join(parts[:i]))
    return chain


def build_effective_series_map(section_idx: str, global_map: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """
    Merge maps for exact section, then ancestors, then '*' default (last).
    Later (more specific) overrides earlier.
    """
    eff: Dict[str, str] = {}
    # Start from least specific so that specific ones override
    order: List[str] = []
    anc = section_ancestry(section_idx)
    for key in reversed(anc):
        if key in global_map:
            order.append(key)
    if "*" in global_map:
        order.append("*")
    # Now apply in natural order so later entries (more specific) win
    for key in order:
        eff.update(global_map.get(key, {}))
    return eff


SERIES_TOKEN_RE = re.compile(r"([^\s{}\[\]/(),:+]+?)([\u2080-\u209F]+)")

def resolve_series_labels(text: str, eff_map: Dict[str, str], unmapped: Set[str]) -> str:
    """
    Replace series labels like s₁, x₂, h₁ using the effective map.
    If no mapping present, leave as-is but record in unmapped set.
    """
    def subber(m: re.Match) -> str:
        base = m.group(1)
        full = base + m.group(2)
        replacement = eff_map.get(full)
        if replacement:
            return replacement
        # also allow mapping by subscript alone if present like 'ₓ'
        replacement = eff_map.get(m.group(2))
        if replacement:
            return replacement
        unmapped.add(full)
        return full
    return SERIES_TOKEN_RE.sub(subber, text)


def normalize_env_fragment(env: str) -> str:
    """
    Ensure environment/exception fragments avoid putting '_' inside sets.
    Transform patterns like '{ _i, _i:[+long] }' -> '_{ i, i:[+long] }'.
    """
    s = env
    # If already an environment set, leave as is
    if s.strip().startswith(":{") and s.strip().endswith("}:"):
        return s.strip()
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
    # Separate accidental concatenations like 'Cw' -> 'C w'
    s = re.sub(r"\bCw\b", "C w", s)
    # Remove unknown grouping letters inside sets
    s = re.sub(r"\b[ZRHUE]\b", "", s)
    # Map 'R' to 'L' when used as grouping next to V (e.g., VR -> VL)
    s = re.sub(r"\bVR\b", "VL", s)
    # Replace CH with C h (group + literal h)
    s = re.sub(r"\bVCH\b", "VC h", s)
    # If a brace-set appears immediately after '_' or immediately before '_',
    # promote it to an environment set :{ alt1, alt2 }:
    def expand_paren_token(tok: str) -> List[str]:
        # Expand a simple single optional like (d)l -> ['dl', 'l']; else keep as-is
        m = re.match(r"^\(\s*([^\s{}()])\s*\)([^\s{}()]+)$", tok)
        if m:
            return [m.group(1) + m.group(2), m.group(2)]
        return [tok]
    def build_env_set(pre: str, core_items: List[str], post: str) -> str:
        alts: List[str] = []
        for it in core_items:
            for expanded in expand_paren_token(it):
                alts.append(strip_whitespace(f"{pre}_{expanded}{post}"))
        return ":{ " + ", ".join(alts) + " }:"
    # Case A: _{...}suffix
    m_right = re.match(r"^(.*)_\{\s*([^}]*)\s*\}(.*)$", s)
    if m_right:
        pre, items_str, post = m_right.groups()
        items = [x.strip() for x in items_str.split(",") if x.strip()]
        return build_env_set(strip_whitespace(pre), items, strip_whitespace(post))
    # Case B: { ... }_suffix -> produce env set with each item prefixed
    m_left = re.match(r"^\{\s*([^}]*)\s*\}_(.*)$", s)
    if m_left:
        items_str, post = m_left.groups()
        items = [x.strip() for x in items_str.split(",") if x.strip()]
        alts = [strip_whitespace(f"{it}_{post}") for it in items]
        return ":{ " + ", ".join(alts) + " }:"
    # Case C: prefix_(optional)X pattern without braces → env set with two alts
    m_opt_right = re.match(r"^(.*)_\(\s*([^\s{}()])\s*\)([^\s{}()]+)$", s)
    if m_opt_right:
        pre, opt, rest = m_opt_right.groups()
        return ":{ " + ", ".join([
            strip_whitespace(f"{pre}_{opt}{rest}"),
            strip_whitespace(f"{pre}_{rest}")
        ]) + " }:"
    # Fallthrough: transform optionals like (d)l in-place
    s = transform_optionals_in_env(s)
    s = strip_textual_env(s)
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


def format_rule_xml(idx: int, input_str: str, output_str: str, env: Optional[str], exception: Optional[str], indent: str = "\t\t") -> str:
    lines = [f'{indent}<rule index="{idx}">']
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

    # Load per-section series map once per section
    series_map_all = load_series_map(SERIES_MAP_PATH)
    eff_series_map = build_effective_series_map(idx, series_map_all) if idx else series_map_all.get("*", {})
    unmapped_series: Set[str] = set()

    for i, rp in enumerate(rule_ps):
        raw = extract_text_with_subs(rp)
        if not raw:
            continue
        # Resolve series labels for this section BEFORE normalizations
        text = resolve_series_labels(raw, eff_series_map, unmapped_series)
        # Apply general and feature normalizations
        text = normalize_general(text)
        text = normalize_features(text)
        mapping_text, env, exception = split_mapping_and_context(text)
        # Handle inversion-like '!X' in environment by converting to exception
        if env and "!" in env:
            inv = re.findall(r"!\s*([^,]+)", env)
            if inv:
                inv_env = strip_whitespace(inv[0])
                env = re.sub(r"!\s*([^,]+)", "", env)
                exception = f"{inv_env}" if not exception else f"{exception}, {inv_env}"
        if env:
            env = resolve_series_labels(env, eff_series_map, unmapped_series)
            env = normalize_env_fragment(normalize_features(normalize_general(env)))
        if exception:
            exception = resolve_series_labels(exception, eff_series_map, unmapped_series)
            exception = normalize_env_fragment(normalize_features(normalize_general(exception)))
        pairs = split_chain_mappings(mapping_text)
        if not pairs:
            continue
        for inp, out in pairs:
            inp_n = resolve_series_labels(inp, eff_series_map, unmapped_series)
            out_n = resolve_series_labels(out, eff_series_map, unmapped_series)
            inp_n = normalize_features(normalize_general(inp_n))
            out_n = normalize_features(normalize_general(out_n))
            # Prefer compact single-rule forms using sets/lists rather than splitting
            m_out_set = re.match(r"^\{\s*([^}]+)\s*\}$", out_n)
            m_in_set = re.match(r"^\{\s*([^}]+)\s*\}$", inp_n)
            # Case 1: both sides are multi-token sequences of equal length → use brace sets
            in_parts = [p for p in inp_n.split() if p]
            out_parts = [p for p in out_n.split() if p]
            if len(in_parts) > 1 and len(in_parts) == len(out_parts) and not m_in_set and not m_out_set:
                in_braced = "{ " + ", ".join(in_parts) + " }"
                out_braced = "{ " + ", ".join(out_parts) + " }"
                xml_lines.append(format_rule_xml(i, in_braced, out_braced, env, exception))
                continue
            # Case 2: single input mapping to a set output → keep one rule but drop braces to a list
            if m_out_set and not m_in_set:
                outs = [strip_whitespace(x) for x in m_out_set.group(1).split(",") if strip_whitespace(x)]
                out_list = ", ".join(outs)
                xml_lines.append(format_rule_xml(i, inp_n, out_list, env, exception))
                continue
            # Default: emit as-is
            xml_lines.append(format_rule_xml(i, inp_n, out_n, env, exception))

    # Escape attributes in opening tag — rebuild header with escaped attrs
    xml_lines[0] = f'\t<section index="{esc_attr(idx)}" name="{esc_attr(name)}">'
    xml_lines.append("\t</section>")
    # Emit unmapped series report per section (append to a file once after the whole doc)
    if unmapped_series:
        UNMAPPED_BUFFER.append((idx, sorted(unmapped_series)))
    return idx, name, "\n".join(xml_lines)


def build_document(root) -> str:
    # reset report buffer
    global UNMAPPED_BUFFER
    UNMAPPED_BUFFER = []
    sections = root.xpath("//section[contains(@class,'showtarget')]")
    xml_lines: List[str] = ["<document>"]
    for sec in sections:
        _idx, _name, body = parse_section(sec)
        if body:
            xml_lines.append(body)
    xml_lines.append("</document>")
    # write unmapped report if any
    if UNMAPPED_BUFFER:
        try:
            with UNMAPPED_SERIES_REPORT.open("w", encoding="utf-8") as f:
                f.write("section,unmapped_series\n")
                for sec_idx, tokens in UNMAPPED_BUFFER:
                    f.write(f"{sec_idx},{' '.join(tokens)}\n")
        except Exception:
            pass
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

