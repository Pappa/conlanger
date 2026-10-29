Type: task
Status: needs-detail
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Decide section_mappings feature-matrix YAML and compile policy.
Blocked by:

## Problem Statement

Expanding Athabaskan §29.1.1.1 **section_mappings** (class labels to feature matrices) yields multi-line `stages` in YAML and compile validation failures. The fix layer (parse, YAML I/O, compile) and SoT policy are unset.

## Description

Decide root cause, correct fix layer, and whether section-local class labels → feature matrices belong in applier-neutral SoT. Validate on §29.1.1.1 sample rules.

## Acceptance Criteria

- [ ] **Answer** states root cause, fix layer, and SoT policy with passing compile on representative rules or documented hold-outs.
- [ ] Any follow-on implementation beyond one session is filed as a new backlog task.
- [ ] **`Status: resolved`** with **Answer** per implement-closure.

## Comments
