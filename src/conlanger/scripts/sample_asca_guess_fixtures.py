"""Sample HTML rules and append heuristic ASCA-guess fixture rows.

Evidence ticket: .scratch/rule-index/issues/08-asca-validator.md
RNG seed is fixed (default 20260802) and recorded beside the fixture.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from conlanger.appliers.asca import (
    ASCAValidationError,
    validate_asca,
)
from conlanger.scripts.config_loaders import load_compiler_config, load_parser_config
from conlanger.tools.ingest import IndexDiachronicaParser
from conlanger.tools.rules import DiachronicSeries

DEFAULT_HTML = ROOT / "data/diachronica/index_diachronica_original.html"
DEFAULT_CSV = ROOT / "tests/fixtures/sound_change_rules.csv"
DEFAULT_SEED = 20260802
DEFAULT_N = 500

# Parenthetical / trailing English prose often glued onto ID output/env fields.
_PAREN_PROSE_RE = re.compile(r"\s*\([^)]*\)\s*$")
_TRAILING_PROSE_RE = re.compile(
    r"\s+(?:when|where|in|if|though|although|sometimes|rarely|"
    r"usually|especially|also|only|before|after|except|typically|"
    r"possibly|sporadic|involving|\(\?\))\b.*$",
    re.IGNORECASE,
)
_SEMICOLON_PROSE_RE = re.compile(r"\s*;.*$")
_QUOTED_PROSE_RE = re.compile(r"[“”\"'].*$")
_LEADING_DASH_RE = re.compile(r"^[—–\-]+\s*")
_LONE_ZERO_RE = re.compile(r"^0$")
_SUBSCRIPT_TRANS = str.maketrans("₀₁₂₃₄₅₆₇₈₉ₓ", "0123456789x")
_SET_THEN_DIAC_RE = re.compile(r"(\{[^}]+\})([ʲʷˤˠʰʱ]+)")
_FEATURE_FIXES = (
    (re.compile(r"\bvoiced\b", re.IGNORECASE), "voice"),
    (re.compile(r"\bunvoiced\b", re.IGNORECASE), "-voice"),
    (re.compile(r"\bhigh\s+tone\b", re.IGNORECASE), "high"),
    (re.compile(r"\blow\s+tone\b", re.IGNORECASE), "low"),
    (re.compile(r"\bsec(?:ondary)?\s+stress\b", re.IGNORECASE), "sec.stress"),
)


def strip_prose(value: str) -> str:
    text = value.strip()
    text = _PAREN_PROSE_RE.sub("", text).strip()
    text = _SEMICOLON_PROSE_RE.sub("", text).strip()
    text = _QUOTED_PROSE_RE.sub("", text).strip()
    text = _TRAILING_PROSE_RE.sub("", text).strip()
    # Drop dangling English leftovers after phonological material.
    text = re.sub(r",\s*typically\b.*$", "", text, flags=re.IGNORECASE).strip()
    return text


def normalise_zero(value: str) -> str:
    if _LONE_ZERO_RE.match(value.strip()):
        return "∅"
    return value


def fix_features(text: str) -> str:
    for pat, repl in _FEATURE_FIXES:
        text = pat.sub(repl, text)

    # Matrix spacing: [+ long + closed] → [+long, +closed] (best-effort)
    def _fix_matrix(m: re.Match[str]) -> str:
        inner = m.group(1)
        parts = re.split(r"\s*,\s*|\s+(?=[+\-])", inner.strip())
        parts = [p.strip().replace(" ", "") for p in parts if p.strip()]
        return "[" + ", ".join(parts) + "]"

    return re.sub(r"\[([^\[\]]+)\]", _fix_matrix, text)


def normalise_length_and_syllabic(text: str) -> str:
    # ASCA 0.10 rejects bare ː in rules; attach as a length feature.
    text = text.replace("ː", ":[+long]")
    text = re.sub(r"(\S)̩", r"\1:[+syll]", text)
    return text


def move_set_diacritics(text: str) -> str:
    """``{d,n}ʲ`` → ``{dʲ,nʲ}`` (ASCA rejects diacritic after a set)."""

    def _expand(m: re.Match[str]) -> str:
        body = m.group(1)[1:-1]
        dia = m.group(2)
        parts = [p.strip() for p in body.split(",")]
        return "{" + ",".join(p + dia for p in parts if p) + "}"

    return _SET_THEN_DIAC_RE.sub(_expand, text)


def parallel_spaces_to_commas(inp: str, out: str) -> tuple[str, str]:
    """``p t ts s`` / ``v r ∅ h`` → comma-joined parallel ASCA I/O."""
    if "," in inp or "," in out:
        return inp, out
    if "{" in inp or "{" in out:
        return inp, out
    left = inp.split()
    right = out.split()
    if len(left) >= 2 and len(left) == len(right):
        return ", ".join(left), ", ".join(right)
    return inp, out


def strip_io_optionals(text: str) -> str:
    """Optionals are env/structure-only; unwrap simple ``(…)`` in I/O."""
    # Repeatedly unwrap non-nested parens used as ID optionality.
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\(([^()]*)\)", r"\1", text)
    return text


def guess_field(value: str | None, *, is_env: bool = False) -> str:
    if value is None:
        return ""
    text = strip_prose(value)
    text = _LEADING_DASH_RE.sub("", text).strip()
    text = text.translate(_SUBSCRIPT_TRANS)
    text = normalise_zero(text)
    text = fix_features(text)
    text = normalise_length_and_syllabic(text)
    text = move_set_diacritics(text)
    if not is_env:
        text = strip_io_optionals(text)
    if is_env and text and "_" not in text:
        if re.fullmatch(r"[#%$].*", text):
            pass
        elif text.endswith(("#", "$")):
            text = f"_{text}" if not text.startswith("_") else text
        else:
            text = f"{text}_"
    return text.strip()


def guess_asca_fields(rule: dict) -> dict[str, str]:
    """Heuristic ASCA field guess from an HTML-parsed rule dict."""
    if rule.get("status") == "skipped":
        return {
            "asca_input": "",
            "asca_output": "",
            "asca_env": "",
            "asca_exception": "",
        }

    stages = [stage for stage in rule.get("stages", []) if stage and str(stage).strip()]
    inp = guess_field(stages[0] if stages else "")
    out = guess_field(stages[-1] if len(stages) >= 2 else "")
    env = guess_field(rule.get("env"), is_env=True)
    exc = guess_field(rule.get("exception"), is_env=True)
    inp, out = parallel_spaces_to_commas(inp, out)

    if not inp:
        inp = "∅"
    if not out:
        out = "∅"

    return {
        "asca_input": inp,
        "asca_output": out,
        "asca_env": env,
        "asca_exception": exc,
    }


def fixture_id(source: str) -> str:
    """Short stable id from provenance ``file:line``."""
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:8]


def build_sound_change_rule(
    guess: dict[str, str], *, source: str
) -> DiachronicSeries | None:
    if not guess["asca_input"] or not guess["asca_output"]:
        return None
    change = {
        "input": guess["asca_input"],
        "output": guess["asca_output"],
    }
    if guess["asca_env"]:
        change["env"] = guess["asca_env"]
    if guess["asca_exception"]:
        change["exception"] = guess["asca_exception"]
    return DiachronicSeries(
        {
            "index": "fixture",
            "section": source.replace(":", "_"),
            "rules": [change],
        },
        format="asca",
        compiler_config=load_compiler_config(),
    )


FIELDNAMES = [
    "id",
    "source",
    "raw",
    "input",
    "output",
    "env",
    "exception",
    "expect_none",
    "kind",
    "asca_input",
    "asca_output",
    "asca_env",
    "asca_exception",
    "asca_expect_ok",
]


def load_existing(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = []
        for row in reader:
            normalised = {k: row.get(k, "") or "" for k in FIELDNAMES}
            # Preserve legacy rows as html_extract.
            if not normalised["kind"]:
                normalised["kind"] = "html_extract"
            rows.append(normalised)
        return rows


def collect_schg_rules(html_path: Path) -> list[dict]:
    doc = IndexDiachronicaParser(load_parser_config()).parse(html_path)
    return [rule for section in doc["sections"] for rule in section.get("rules", [])]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("-n", type=int, default=DEFAULT_N)
    parser.add_argument(
        "--replace-guesses",
        action="store_true",
        help="Drop existing asca_guess rows before appending a fresh sample",
    )
    args = parser.parse_args()

    existing = load_existing(args.csv)
    if args.replace_guesses:
        existing = [r for r in existing if r["kind"] != "asca_guess"]
    else:
        already = sum(1 for r in existing if r["kind"] == "asca_guess")
        if already:
            print(
                f"CSV already has {already} asca_guess rows; "
                f"pass --replace-guesses to regenerate",
                file=sys.stderr,
            )
            return 1

    all_rules = collect_schg_rules(args.html)
    rng = random.Random(args.seed)
    if len(all_rules) < args.n:
        print(f"only {len(all_rules)} rules available", file=sys.stderr)
        return 1
    sample = rng.sample(all_rules, args.n)

    ok_count = 0
    new_rows: list[dict[str, str]] = []
    for rule in sample:
        source = rule.get("source", "")
        raw = rule.get("raw", "")
        stages = [
            stage for stage in rule.get("stages", []) if stage and str(stage).strip()
        ]
        parts = {
            "input": stages[0] if stages else "",
            "output": stages[-1] if len(stages) >= 2 else "",
            "env": rule.get("env", ""),
            "exception": rule.get("exception", ""),
        }
        guess = guess_asca_fields(rule)
        scr = build_sound_change_rule(guess, source=source)
        expect_ok = False
        if scr is not None:
            try:
                validate_asca(scr)
                expect_ok = True
                ok_count += 1
            except ASCAValidationError:
                expect_ok = False

        new_rows.append(
            {
                "id": fixture_id(source),
                "source": source,
                "raw": raw,
                "input": parts["input"],
                "output": parts["output"],
                "env": parts["env"],
                "exception": parts["exception"],
                "expect_none": "True" if rule.get("status") == "skipped" else "False",
                "kind": "asca_guess",
                "asca_input": guess["asca_input"],
                "asca_output": guess["asca_output"],
                "asca_env": guess["asca_env"],
                "asca_exception": guess["asca_exception"],
                "asca_expect_ok": "True" if expect_ok else "False",
            }
        )

    out_rows = existing + new_rows
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    note = args.csv.with_suffix(".asca_guess_seed.txt")
    note.write_text(
        f"seed={args.seed}\nn={args.n}\nhtml={args.html.name}\n"
        f"asca_guess_ok={ok_count}\nasca_guess_total={len(new_rows)}\n"
        f"asca=0.10.2\n",
        encoding="utf-8",
    )
    print(
        f"wrote {len(new_rows)} asca_guess rows ({ok_count} validate ok) to {args.csv}"
    )
    print(f"seed note: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
