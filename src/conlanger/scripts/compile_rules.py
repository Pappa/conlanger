"""Compile applier-neutral index YAML to ``asca_rules.yml`` (compile stage only)."""

import argparse
import sys
from pathlib import Path

from conlanger.scripts.config_loaders import load_compiler_config
from conlanger.scripts.pipeline_defaults import (
    DEFAULT_COMPILED_YAML,
    DEFAULT_YAML,
    ROOT,
)
from conlanger.tools.compiled_rules_yaml import (
    COMPILED_RULES_YAML_NAME,
    build_asca_rules_document,
    write_compiled_rules_yaml,
)
from conlanger.tools.index_inventory import iter_index_compile_bundles
from conlanger.tools.index_io import read_cleaned_index


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--yaml-in", type=Path, default=DEFAULT_YAML)
    ap.add_argument(
        "--compiled-out",
        type=Path,
        default=DEFAULT_COMPILED_YAML,
        help=f"writes {COMPILED_RULES_YAML_NAME} (default: diagnostics/compile/)",
    )
    ap.add_argument("--limit", type=int, default=0, help="optional cap for smoke tests")
    args = ap.parse_args()

    if not args.yaml_in.is_file():
        print(f"ERROR: parsed YAML not found at {args.yaml_in}", file=sys.stderr)
        return 1

    doc = read_cleaned_index(args.yaml_in)
    compiler_config = load_compiler_config()
    bundles = iter_index_compile_bundles(doc, compiler_config=compiler_config)
    if args.limit:
        bundles = bundles[: args.limit]

    document = build_asca_rules_document(bundles, compiler_config=compiler_config)
    write_compiled_rules_yaml(document, args.compiled_out)

    rule_count = sum(
        len(section.get("rules") or []) for section in document.get("sections") or []
    )
    print(
        f"wrote {args.compiled_out.relative_to(ROOT)} "
        f"sections={len(document.get('sections') or [])} rules={rule_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
