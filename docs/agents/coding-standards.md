# Coding standards (review axis)

Judgement and mechanical expectations for `/code-review` **Standards**. Not a substitute for the automated gate (`uv run check`).

## Imports and package layers

- **No lazy imports** inside functions to paper over circular dependencies — propose a structural fix (move shared code to `utils`, narrow imports, split modules) before landing a large refactor.
- **Parse ↔ compile boundary:**
   - `conlanger.ingest` must not import `conlanger.compile`
   - `conlanger.compile` must not import `conlanger.ingest`
   - `conlanger.ingest` and `conlanger.compile` may import `conlanger.utils`
   - Enforced by import-linter ([pyproject.toml](../../pyproject.toml) `[tool.importlinter]`). Narrative: [index-diachronica-parser.md](../system/index-diachronica-parser.md) § Package imports.

## Refactors

When the user asks for a substantial refactor, outline the structural proposal (modules, data flow, test plan) before rewriting wide swaths of code.

## Mechanical gates

Python style and coverage: [DEV.md](../DEV.md), `.cursor/rules/python-quality-gates.mdc`.
