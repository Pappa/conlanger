Type: epic-duck:decision
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Decide section_mappings feature-matrix YAML and compile policy.
Blocked by:

## Question

Expanding Athabaskan §29.1.1.1 **section_mappings** (class labels to feature matrices) yields multi-line `stages` in YAML and compile validation failures. The fix layer (parse, YAML I/O, compile) and SoT policy are unset.

Decide root cause, correct fix layer, and whether section-local class labels → feature matrices belong in applier-neutral SoT. Validate on §29.1.1.1 sample rules.

Wayfinder source: `.scratch/rule-index/issues/129-grill-section-mappings-feature-matrices-yaml-compile.md`.

## Answer
