Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Hold out or fix remaining unrelated `expected_underscore` rows (prose, else, //).
Blocked by: 0048

## Problem Statement

After syllable compile tasks **0046**–**0048**, **62** inventory rows should still fail `expected_underscore` for non-syllable reasons (families **U1–U7** in [0045](../spikes/0045-expected-underscore-syllable-compile-review.md)): bare `else`, Index prose env, `//` in env, prose inside `:{…}:`, and other syntax. Without a documented policy and targeted passes, these rows will be mistaken for syllable compile work again.

## Description

For each unrelated family (U1–U7), pick **one** outcome per rule or family: **compile fix** (if a mechanical ASCA mapping exists), **`status: skipped`** in index with reason, or **correction-pass** edit — per **[0025](0025-decision-env-and-prose-conditions.md)** and historical-fidelity policy **[0017](0017-decision-historical-fidelity-vs-validity.md)**.

Use triplet CSV [`diagnostics/inventory/analysis/0045-expected-underscore-triplets.csv`](../../diagnostics/inventory/analysis/0045-expected-underscore-triplets.csv) (`primary_category` = unrelated).

**Out of scope:** Re-opening F1–F4 syllable underline work; changing ASCA.

## Acceptance Criteria

- [ ] Summary table in **Comments** (or linked spike addendum) lists each U-family, row count, and chosen disposition (fixed / skipped / deferred).
- [ ] Any rule marked fixed passes validate for its inventory row; skipped rules have documented reason in YAML or corrections config.
- [ ] Fresh inventory: no remaining `expected_underscore` rows are classified F1–F4 in a re-run of the 0045 classifier (or reclassify script updated and noted).
- [ ] `uv run check` passes; **`Status: resolved`**; sync plan **Tasks** table.

## Comments
