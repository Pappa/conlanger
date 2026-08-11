Type: task
Status: resolved
Blocked by:

# Document the sound-change rule pipeline in docs/

## Question

Write the step-by-step documentation for the **new** sound-change rule pipeline (parse → applier-neutral validation → applier compile → compile validation), including ordered transform tables with rationale for implemented steps and `Order: TBD` rows for planned work.

## Context

Grill session (2026-08-07): compile transform order must be clearly defined and justified before refactoring `DiachronicSeries` / `RuleChange` ([ticket 39](39-refactor-sound-change-ruleset.md)). Applier compile and parse are **separate** docs; transform order is recorded in docs only (no ADR).

## Deliverables

### 1. `docs/index-diachronica-parser.md`

- Document parse-time transforms in `IndexDiachronicaParser` / `parsers.py` (and related modules such as `series_mappings.py` where parse-time).
- Use a pipeline **table**: columns `Step`, `Status` (`implemented` / `planned` / `spike needed`), `Order`, `Rationale`.
- Applier-neutral scope only — do not duplicate applier compile steps.

### 2. `docs/applier-neutral-corpus-validation.md`

- Document stage **Applier-neutral corpus validation** (inventory, correction pass, regen workflow, validation report — sub-steps may evolve).
- Same table format where ordering applies; prose OK for workflow that is not a strict transform pipeline.
- Cross-link `.scratch/cleaned-rule-corpus/spec.md` and relevant correction-pass tickets; this doc is the stable `docs/` entry point.

### 3. `docs/sound-change-applier.md`

- **Applier compile only:** `PhonologicalRuleSet` → `DiachronicSeries` section assembly → per-rule ASCA transforms → `.rsca` string shape.
- Single pipeline table for per-rule transforms. Implemented steps (current `RuleChange._compile_rule_text` order):
  1. Join corpus fields
  2. `normalize_asca_optional_grouping_ellipsis`
  3. `apply_asca_group_mappings`
  4. `normalize_asca_length_marks`
  5. `normalize_typographic_apostrophes`
  6. `normalize_asca_ejective_marks`
  7. `_apply_aliases` (`h₁`/`h₂`/`h₃`)
- Each implemented row: fixed `Order`, brief rationale, note what breaks if reordered (where non-obvious).
- **Planned compile transforms** (not yet in code): include as table rows with `Status: planned` or `spike needed` and `Order: TBD` — positional slots, identity subscripts, section-local abbreviations, meta-notation, etc. (ASCA projection intent only).
- **Compile validation** section (stage 4): `validate_asca`, probe wordlist, relationship to ADR-0003; link to `.scratch/.../research/asca-rule-validity.md` for ASCA constraint detail.
- **Brassica:** section title + one sentence stating future functionality only.

Primary code references: `src/conlanger/tools/rules.py`, `phonological_ruleset.py`, `asca_validator.py`.

### 4. `docs/SYSTEM.md`

- Rename existing **Pipeline stages** → **Pipeline stages (legacy)** (notebook-centric table unchanged).
- Add **Pipeline stages (new)** — ordered list linking the four stages:

  | Stage | Doc |
  |-------|-----|
  | Index Diachronica parse | [index-diachronica-parser.md](../index-diachronica-parser.md) |
  | Applier-neutral corpus validation | [applier-neutral-corpus-validation.md](../applier-neutral-corpus-validation.md) |
  | Applier compile | [sound-change-applier.md](../sound-change-applier.md) |
  | Compile validation | [sound-change-applier.md](../sound-change-applier.md#compile-validation) (anchor in applier doc) |

- Fix stale link: `DiachronicSeries` lives in `src/conlanger/tools/rules.py`, not `DiachronicSeries.py`.

## Notes

- `CONTEXT.md` is glossary-only — do not move implementation detail there.
- Spike [38](38-spike-asca-compile-transform-order.md) fills TBD `Order` cells for planned ASCA compile transforms; this ticket may leave those rows as TBD with cross-ref to 38.
- Do not refactor `DiachronicSeries` in this ticket.

## Acceptance criteria

- [x] All four deliverables exist and cross-link consistently.
- [x] `sound-change-applier.md` table lists all seven implemented ASCA transforms in code order with rationale.
- [x] Planned compile transforms appear in the applier table with `Order: TBD` and pointer to ticket 38.
- [x] `SYSTEM.md` has legacy + new pipeline sections.
- [x] No code changes required (docs-only); optional typo fixes in existing doc links OK.

## Comments
