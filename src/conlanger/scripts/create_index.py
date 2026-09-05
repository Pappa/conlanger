"""Parse Index Diachronica HTML into applier-neutral YAML and parse diagnostics.

Parse-only: writes cleaned YAML and parse-time artifacts under
``.scratch/rule-index/parse/``. For compile validation and inventory,
run ``validate_rules`` on the parsed YAML.
"""

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from conlanger.scripts.config_loaders import load_parser_config
from conlanger.scripts.pipeline_defaults import (
    DEFAULT_COMMENT_SUMMARY,
    DEFAULT_HTML,
    DEFAULT_PARSE_DIR,
    DEFAULT_YAML,
)
from conlanger.tools.index_io import write_cleaned_index
from conlanger.tools.ingest import (
    IndexDiachronicaParser,
    write_rule_comment_phrase_summary,
)
from conlanger.utils.file_io import (
    MANUAL_MAPPINGS_MATCHED_CSV_NAME,
    write_manual_mappings_matched_csv,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", type=Path, default=DEFAULT_HTML)
    ap.add_argument("--yaml-out", type=Path, default=DEFAULT_YAML)
    ap.add_argument(
        "--parse-dir",
        type=Path,
        default=DEFAULT_PARSE_DIR,
        help=("writes manual_mappings_matched_rules.csv and rule-comment-phrases.md"),
    )
    args = ap.parse_args()

    if not args.html.is_file():
        print(f"ERROR: HTML not found at {args.html}", file=sys.stderr)
        return 1

    parser_config = load_parser_config()
    parser = IndexDiachronicaParser(parser_config)
    doc = parser.parse(args.html)
    write_cleaned_index(doc, args.yaml_out)
    args.parse_dir.mkdir(parents=True, exist_ok=True)
    comment_summary_path = args.parse_dir / DEFAULT_COMMENT_SUMMARY.name
    n_with_comment = write_rule_comment_phrase_summary(doc, comment_summary_path)

    matched_path = args.parse_dir / MANUAL_MAPPINGS_MATCHED_CSV_NAME
    write_manual_mappings_matched_csv(parser.manual_mapping_matches, matched_path)
    for unused in parser.unmatched_manual_mappings():
        print(
            f"WARNING: unmatched manual mapping from={unused.from_text!r}",
            file=sys.stderr,
        )
    for unused_id in parser.unmatched_corrections():
        print(
            f"WARNING: unmatched correction rule_id={unused_id!r}",
            file=sys.stderr,
        )

    n_sections = len(doc["sections"])
    n_rules = sum(len(s.get("rules") or []) for s in doc["sections"])
    n_skipped = sum(
        1
        for section in doc["sections"]
        for rule in section.get("rules") or []
        if rule.get("status") == "skipped"
    )
    print(
        f"wrote {args.yaml_out} sections={n_sections} rules={n_rules} "
        f"parse_skipped={n_skipped} rules_with_comment={n_with_comment}"
    )
    print(f"wrote {comment_summary_path}")
    print(f"wrote {matched_path} matches={len(parser.manual_mapping_matches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
