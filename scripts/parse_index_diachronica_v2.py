#!/usr/bin/env python3
"""Parse Index Diachronica HTML into cleaned-corpus YAML (input/output phase)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from conlanger.tools.IndexDiachronicaParser import (  # noqa: E402
    IndexDiachronicaParser,
    load_group_mappings,
)

DEFAULT_HTML = ROOT / "notebooks" / "data" / "index_diachronica_original.html"
DEFAULT_OUT = ROOT / "notebooks" / "data" / "index_diachronica_parsed.yml"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", type=Path, default=DEFAULT_HTML)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    if not args.html.exists():
        print(f"ERROR: HTML not found at {args.html}", file=sys.stderr)
        return 1

    parser = IndexDiachronicaParser(load_group_mappings())
    doc = parser.parse(args.html)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    n_sections = len(doc["sections"])
    n_rules = sum(len(s.get("rules") or []) for s in doc["sections"])
    n_skipped = sum(
        1
        for s in doc["sections"]
        for r in s.get("rules") or []
        if r.get("skipped")
    )
    print(
        f"wrote {args.out} sections={n_sections} rules={n_rules} skipped={n_skipped}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
