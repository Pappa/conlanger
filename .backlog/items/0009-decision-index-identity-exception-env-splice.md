Type: epic-duck:decision
Status: in-progress
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Lock compile policy for Index `! Host =` env-slot identity exclusions.
Blocked by:

## Question

Roughly three dozen Index rules use `! Host = RHS` grouping exclusions. Compile still emits invalid ASCA exception tails for some Family B cases after the first identity-exception correction pass (Family A env substitution).

Decide when full env-slot suffix copy is required versus `// RHS_` (or `// {set}_`) only for **env-bound** vs **I/O-bound** forms. Relate policy to existing Family A/B behavior. Scope follow-on compile work ([0010](0010-task-index-identity-exception-residuals.md)) and explicit hold-outs (prose tails, disjunction, compound `Cn` without a C slot). Record outcome under **`## Answer`** here or in an ADR if glossary-bound.

Wayfinder source: `.scratch/rule-index/issues/167-grill-index-identity-exception-env-splice.md`.

## Answer
