"""One-off inventory builder for spike 173 (not installed as project script)."""

from __future__ import annotations

import csv
import re
import subprocess
from collections import Counter
from pathlib import Path

import yaml

from conlanger.compile.resolve_index_rule import materialize_index_rule_env_exception
from conlanger.compile.tools.asca.pipeline import compile_asca_rule_fields
from conlanger.scripts.config_loaders import load_compiler_config

ASCA = Path("lib/bin/asca")
YAML_PATH = Path("data/diachronica/index_diachronica.yml")
OUT = Path(".scratch/rule-index/research/position-in-asca-compile-projection.csv")

TARGET_RE = re.compile(
    r"^(?:#U(?:\s*,\s*U#)?|U#|#U(?:\[[^\]]+\])?#?|"
    r"U(?:\[[^\]]+\]|:\[[^\]]+\](?:\[[^\]]+\])?))$"
)


def classify_target(t: str) -> str:
    t = t.strip().strip("'\"")
    if re.fullmatch(r"#U\s*,\s*U#", t):
        return "syllable_edge_combo"
    if t in ("#U", "U#"):
        return "syllable_edge"
    if re.fullmatch(r"#U\[[^\]]+\]#?", t) or re.fullmatch(r"#U:\[[^\]]+\]", t):
        return "syllable_edge_feature"
    if re.fullmatch(r"U\[-stress\]|U\[\+stress\]", t):
        return "syllable_stress"
    if t.startswith("U:") and "stress" in t:
        return "syllable_stress_height_matrix"
    if t.startswith("U[") or t.startswith("U:"):
        return "syllable_feature_matrix"
    if t in ("prefixes", "the", "Pre-Livonian"):
        return "prose_morpho"
    return "prose_other"


def propose_asca(target_class: str, field: str, target: str, ctx: str) -> str:
    t = target.strip().strip("'\"")
    exc = field == "exception"

    def env_e(mechanical: str, exception: str) -> str:
        return exception if exc else mechanical

    if target_class == "syllable_edge":
        return env_e(
            "#<.._>" if t == "#U" else "<.._>#",
            ":{#_#, #<.._>}:" if t == "#U" else ":{#_#, <.._>#}:",
        )
    if target_class == "syllable_edge_combo":
        return env_e("defer_positive_env", ":{#_#, #<.._>, <.._>#}:")
    if target_class == "syllable_stress":
        stress = "_ $[+stress]" if "+stress" in t else "_ $[-stress]"
        if ctx:
            tail = "in $[+stress]" if "+stress" in t else "in $[-stress]"
            return f"{ctx} {tail}"
        return stress
    if target_class == "syllable_stress_height_matrix":
        feats = re.findall(r"\[[^\]]+\]", t[2:] if t.startswith("U:") else t)
        return "_ %" + "".join(feats)
    if target_class == "syllable_feature_matrix":
        if re.search(r"\+lo|\-hi|\+open", t):
            return "_ %[+lo]"
        if re.search(r"\+hi|\-lo|\+closed", t):
            return "_ %[-hi]"
        if "stress" in t:
            return "_ $[-stress]" if "-stress" in t else "_ $[+stress]"
        if "long" in t and "stress" in t:
            return "defer:U[+long -stress]"
        return "defer:matrix"
    if target_class == "syllable_edge_feature":
        if "+stress" in t:
            return "#<.._>[+stress]"
        return "#<.._>"
    if target_class == "prose_morpho":
        return "defer:manual"
    return "defer:prose"


def validate_fragment(field: str, fragment: str) -> str:
    if fragment.startswith("defer"):
        return "n/a"
    asca_field = "exception" if field == "exception" else "context"
    try:
        result = subprocess.run(
            [str(ASCA), "validate", "-s", fragment, "-f", asca_field],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return "pass" if result.returncode == 0 else "fail"
    except OSError as exc:
        return f"err:{exc}"


def extract_embedded_phono(val: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    if re.search(
        r"adjacent syllable|even syllables|onset position|in nouns|in prefixes|in the ",
        val,
        re.I,
    ):
        return hits
    match = re.search(
        r"^(.+?)\s+in\s+(#U|U#|#U(?:\[[^\]]+\])?|U(?:\[[^\]]+\]|:\[[^\]]+\](?:\[[^\]]+\])?))",
        val,
    )
    if match:
        hits.append((match.group(0), match.group(2)))
    match2 = re.match(
        r"^in\s+(#U(?:\s*,\s*U#)?|U#|#U(?:\[[^\]]+\])?#?|U(?:\[[^\]]+\]|:\[[^\]]+\](?:\[[^\]]+\])?))",
        val.strip(),
    )
    if match2 and not re.search(r"with the following", val):
        hits.append((match2.group(0), match2.group(1).replace(" ", "")))
    if val.strip().startswith("in #U with"):
        hits.append((val, "#U"))
    return hits


def main() -> None:
    cfg = load_compiler_config()
    rows: list[dict[str, str]] = []
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))

    for section in data.get("sections", []):
        for rule in section.get("rules", []) or []:
            rule_id = rule.get("rule_id", "")
            for field_name in ("env", "exception"):
                val = rule.get(field_name)
                if isinstance(val, dict):
                    position = val.get("position") or {}
                    ctx = val.get("context") or ""
                    if "in" not in position:
                        continue
                    target = position["in"]
                    if isinstance(target, list):
                        target = target[0] if target else ""
                    target_s = str(target)
                    tc = classify_target(target_s)
                    mat_rule = materialize_index_rule_env_exception(
                        {field_name: val}, compiler_config=cfg
                    )
                    materialized = mat_rule.get(field_name, "")
                    compiled = compile_asca_rule_fields(
                        "k",
                        "g",
                        env=materialized if field_name == "env" else None,
                        exception=materialized if field_name == "exception" else None,
                    )
                    proposed = propose_asca(tc, field_name, target_s, ctx)
                    rows.append(
                        {
                            "rule_id": rule_id,
                            "field": field_name,
                            "index_surface": target_s,
                            "context": ctx,
                            "materialized": materialized,
                            "current_compiled_tail": compiled.partition(" / ")[2],
                            "target_class": tc,
                            "proposed_asca": proposed,
                            "defer_or_manual": (
                                "manual"
                                if tc in ("prose_morpho", "prose_other")
                                else ""
                            ),
                            "source": "structured_position.in",
                            "probe_result": validate_fragment(field_name, proposed),
                        }
                    )
                elif isinstance(val, str):
                    for _span, tgt in extract_embedded_phono(val):
                        if " with " in val or "such that" in val:
                            tc = "syllable_feature_prose"
                        else:
                            tc = classify_target(tgt)
                        compiled = compile_asca_rule_fields(
                            "k",
                            "g",
                            env=val if field_name == "env" else None,
                            exception=val if field_name == "exception" else None,
                        )
                        ctx_prefix = ""
                        if " in " in val and tc == "syllable_stress":
                            ctx_prefix = val.split(" in ", 1)[0].strip()
                        proposed = propose_asca(tc, field_name, tgt, ctx_prefix)
                        if tc == "syllable_feature_prose":
                            proposed = "defer:prose_tail"
                        rows.append(
                            {
                                "rule_id": rule_id,
                                "field": field_name,
                                "index_surface": val,
                                "context": "",
                                "materialized": val,
                                "current_compiled_tail": compiled.partition(" / ")[2],
                                "target_class": tc,
                                "proposed_asca": proposed,
                                "defer_or_manual": (
                                    "manual"
                                    if tc == "syllable_feature_prose"
                                    or " with " in val
                                    else ""
                                ),
                                "source": "embedded_string",
                                "probe_result": validate_fragment(
                                    field_name, proposed
                                ),
                            }
                        )

    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    structured = [r for r in rows if r["source"] == "structured_position.in"]
    embedded = [r for r in rows if r["source"] == "embedded_string"]
    print(f"wrote {OUT} rows={len(rows)}")
    print(f"structured={len(structured)} embedded={len(embedded)}")
    print("structured classes", Counter(r["target_class"] for r in structured))
    print("embedded classes", Counter(r["target_class"] for r in embedded))


if __name__ == "__main__":
    main()
