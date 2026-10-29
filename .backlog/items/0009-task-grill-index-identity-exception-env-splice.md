Type: task
Status: in-progress
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Lock compile policy for Index `! Host =` env-slot identity exclusions.
Blocked by:

## Problem Statement

Roughly three dozen Index rules use `! Host = RHS` grouping exclusions. Compile still emits invalid ASCA exception tails for some Family B cases after the first identity-exception correction pass (Family A env substitution).

## Description

Decide when full env-slot suffix copy is required versus `// RHS_` (or `// {set}_`) only for **env-bound** vs **I/O-bound** forms. Relate policy to existing Family A/B behavior. Scope follow-on compile work and explicit hold-outs (prose tails, disjunction, compound `Cn` without a C slot). Record outcome under **`## Answer`** on this ticket or in an ADR if glossary-bound.

Unblocks [0010](0010-task-index-identity-exception-residuals.md).

## Acceptance Criteria

- [ ] **Answer** documents env-bound vs I/O-bound policy and suffix inheritance rules.
- [ ] Follow-on work for **0010** is scoped with named hold-out categories.
- [ ] This ticket **`Status: resolved`** with **Answer** per [implement-closure.md](../../docs/agents/implement-closure.md).

## Comments
