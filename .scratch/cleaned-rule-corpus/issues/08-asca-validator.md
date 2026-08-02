Type: task
Blocked by: 01

# Create an ASCA validator for SoundChangeRule

## Question

Implement an ASCA validator that takes a `SoundChangeRule` instance, returns `True` when the rule is valid for ASCA, and raises an error with an appropriate message when it is not. Validity criteria come from [What counts as a valid ASCA rule string?](01-valid-asca-rule-string.md) findings: [../research/asca-rule-validity.md](../research/asca-rule-validity.md).

## Notes

- Wayfinder role: AFK task that makes post-compile ASCA checking concrete so [Correction workflow for invalid rules](05-correction-workflow-invalid-rules.md) can decide workflow against a real validator (does not deliver the cleaned corpus itself).
- Aligns with ADR-0003 (validate after applier compile): this is the ASCA-side check, not an HTML→YAML ingest gate.
- Spec source of truth for accept/reject behaviour: `.scratch/cleaned-rule-corpus/research/asca-rule-validity.md` (whole-rule form, per-field checklists, operators, ID failure patterns, CLI validation approach in §4).
- API contract (required):
  - **Input:** an instance of `SoundChangeRule` (`src/conlanger/tools/SoundChangeRule.py`).
  - **Valid:** return `True`.
  - **Invalid:** raise an error whose message explains the failure appropriately (surface ASCA/syntax reason when available).
- Prefer driving validation via the installed `asca` CLI / compile path described in the research file (no dedicated `asca validate` subcommand) rather than re-implementing the full grammar by hand — unless a thin pre-check is clearly cheaper and still faithful to that spec.
- AFK-capable once claimed; add unit tests covering valid and invalid cases drawn from the research checklists / known Index Diachronica failure patterns.

