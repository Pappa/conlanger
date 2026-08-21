Type: task
Status: ready-for-agent
Blocked by:

# Config-only `status: skipped`; stop parse auto-skip

Grill 2026-08-21 (Q3–Q5, Q7): **`status: skipped` is the only skip field.** A **corpus rule** is skipped only if its **rule id** is in `parser_config.yml` `skip_rules`. A **sound-change section** is skipped only if its `index` is in `skip_sections` (YAML `status: skipped`, not boolean `skipped: true`). Parse must **not** auto-skip missing-arrow, quoted-prose, gloss-only, or short-spine lines. Skipped **rules** compile as ASCA comments (`#\t…`). Glossary: `CONTEXT.md`. ADRs: [0010 amendment](../../../docs/adr/0010-historical-fidelity-class-first-status.md), [0013](../../../docs/adr/0013-parse-compile-validate.md).

## Problem

Parse stamps `status: skipped` + `stages: []` on several automatic paths **and** on `skip_rules`. Compile omits empty-`stages` rules, so unlisted failures never hit ASCA. Section skip uses boolean `skipped: true`. Legacy `skip: true` comments out rules independently of `status`.

## What to build

### 1. Parse — auto-skip off; `skip_rules` on

- Keep `skip_rules`: listed **rule id**s → `status: skipped` (optional `comment` from config `reason` as today).
- Stop emitting `status: skipped` for quoted-prose, missing-`→`, gloss-only, and `finalize_stages_shape`. Those remain ordinary corpus rules (spine shape is [ticket 90](90-missing-arrow-single-stage.md)).
- Do **not** stamp skip on rules inside a skipped section ([ticket 78](78-implement-parser-config-section-skip.md)).

### 2. Parse — sections

- `skip_sections` unchanged as config.
- Listed sections: `status: skipped` instead of `skipped: true`.

### 3. Compile

- Rule `status: skipped` → still a `SoundChangeRule` (or equivalent), prefix `#\t`, body **`raw`**. Excluded from `_active_rule_changes`.
- Remove boolean `skip` / `skip: true` as a separate corpus/compile flag; chain meta copies `status` if needed, not `skip`.
- Section `status: skipped` → early return, no rule parts (ticket 78).

### 4. Inventory

- Rule `status: skipped`: `ok=True`, description `held-out (commented rule)` (config hold-out, not missing-arrow).
- Section `status: skipped`: `failure_class=section_skipped`; no `validate_asca`.
- Drop `rule.get("skip")` and `section.get("skipped")` boolean branches.

### 5. Docs and tests

- Parser/applier/inventory: skip is config-only; boolean fields gone.
- Living docs: compile-time chain expansion only.
- Tests: keep `skip_rules` coverage; remove expectations that missing-arrow / gloss-only are skipped; `test_rules.py` `skip: True` → `status: skipped`; regen YAML sections use `status: skipped`.

## Out of scope

- Missing-arrow `stages: ["text"]` and compile-with-no-output — [ticket 90](90-missing-arrow-single-stage.md)
- Three-stage doc reshape — [ticket 91](91-three-stage-pipeline-docs.md)
- Pydantic compile rewrite — [tickets 92](92-grill-pydantic-compile-refactor.md) / [93](93-pydantic-compile-refactor.md)

## Acceptance criteria

- [ ] Auto-skip paths gone; `skip_rules` still sets rule `status: skipped`
- [ ] Section skip is `status: skipped` only
- [ ] Skipped rules render as `#\t` + `raw`; skipped sections bypass compile
- [ ] No `skip: true` / `skipped: true` in corpus YAML
- [ ] Full gate: `uv run pytest`; `uv run ruff check --fix`; `uv run ruff format && uv run ruff format --check src`
