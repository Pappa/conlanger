Type: task
Status: ready
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Remove `rule-comment-phrases.md` parse diagnostic and code used only to generate it.
Blocked by:

## Problem Statement

`uv run create_index` writes `diagnostics/parse/rule-comment-phrases.md`, a markdown survey that counts editorial qualifier phrases in parsed rule **`comment`** fields. That artifact is no longer used in the correction loop or operator workflow. Keeping it adds dead code (phrase regex list, writer, tests, committed file) and stale documentation in the validate pipeline diagram.

## Description

**In scope:** Everything that exists **only** to produce `rule-comment-phrases.md`.

**Out of scope (do not remove):**

- The **`comment`** field on parsed rules (`IndexRule.comment`, semicolon partition in `index_models.py`, sporadic/uncertainty transforms).
- **`manual_mappings_matched_rules.csv`** under the same `--parse-dir` (stays in `create_index`).

**Implementation map (from current tree):**

| Location | Change |
| --- | --- |
| [`create_index.py`](../src/conlanger/scripts/create_index.py) | Stop importing `DEFAULT_COMMENT_SUMMARY` and `write_rule_comment_phrase_summary`; remove write path, stdout lines (`rules_with_comment`, `wrote … rule-comment-phrases.md`); narrow `--parse-dir` help to manual-mapping CSV only. |
| [`pipeline_defaults.py`](../src/conlanger/scripts/pipeline_defaults.py) | Remove `DEFAULT_COMMENT_SUMMARY`. |
| [`file_io.py`](../src/conlanger/utils/file_io.py) | Remove `_RULE_COMMENT_QUALIFIER_PHRASES`, `_RULE_COMMENT_QUALIFIER_PHRASES_RE`, and `write_rule_comment_phrase_summary`; drop unused `re` import if nothing else needs it. |
| [`test_file_io.py`](../tests/conlanger/utils/test_file_io.py) | Remove tests for `write_rule_comment_phrase_summary`; keep manual-mapping CSV tests. |
| [`test_create_index.py`](../tests/conlanger/scripts/test_create_index.py) | Remove `@patch` on `write_rule_comment_phrase_summary`; optionally assert the comment summary file is **not** created. |
| [`docs/system/validate.md`](../docs/system/validate.md) | Remove mermaid `CommentSummary` node/edge and the “Comment phrase survey” table row. |
| [`diagnostics/parse/rule-comment-phrases.md`](../diagnostics/parse/rule-comment-phrases.md) | Delete from the repo. |

## Acceptance Criteria

- [ ] Running `uv run create_index` writes cleaned YAML and `manual_mappings_matched_rules.csv` under `--parse-dir` and does **not** create `rule-comment-phrases.md`.
- [ ] No references to `write_rule_comment_phrase_summary`, `DEFAULT_COMMENT_SUMMARY`, or `rule-comment-phrases.md` remain in `src/` or `tests/` (except git history).
- [ ] `docs/system/validate.md` documents parse diagnostics without the comment phrase survey.
- [ ] `diagnostics/parse/rule-comment-phrases.md` is removed from the working tree.
- [ ] `uv run check` passes.
- [ ] Set **`Status: resolved`** and sync the **Tasks** row on [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md).