Type: epic-duck:decision
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Decide compile policy for grouping letters on insertion rules.
Blocked by:

## Question

Insertion rules (`∅ → …`) with grouping letters or bare matrices on output or env fail compile (for example Cypriot-Arabic-∅ `incomplete_matrix`) while similar env shapes validate (for example Hidatsa-∅).

Lock applier-neutral representation and compile behavior for ASCA grouping on insertions before any correction pass. Distinguish env-driven failures from output-class failures using documented contrast examples. Unblocks [0012](0012-task-correction-pass-asca-grouping-insertion.md).

Wayfinder source: `legacy wayfinder rule-index issue 125-grill-asca-grouping-insertion.md`.

## Answer
