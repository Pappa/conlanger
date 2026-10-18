Type: task
Status: resolved
Blocked by: 171

# Task: agent environment improvements (Oct 2026 retro)

Implement decisions from [171 grill](171-grill-agent-environment-retro-oct-2026.md) (2026-10-18).

## Decisions (from grill)

| Topic | Choice |
| --- | --- |
| Guardrails | **pre-commit only** (no GitHub Actions in this task) |
| Gate commands | pytest + `per_file_coverage_gate` + ruff check/format; **plus import-linter** |
| Map/ticket sync | **Checklist doc only** (no `check_scratch_sync` script) |
| Import contract | **import-linter** + document in **docs/agents/coding-standards.md** |
| Coding standards path | **docs/agents/coding-standards.md** |
| ASCA YAML schema | **docs/system/asca-rules-yaml-schema.md** + link from SYSTEM.md |
| rule-index spec | **Delete** `.scratch/rule-index/spec.md`; fix pointers to `map.md` + `issues/` |

## Work items

### 1. Single gate entrypoint + pre-commit

- Add a project script (e.g. `uv run check` or `[project.scripts] check = ...`) that runs in order:
  1. `uv run pytest`
  2. `uv run per_file_coverage_gate`
  3. `uvx ruff check src tests` then `uvx ruff format src tests --check`
  4. `uv run lint-imports` (or whatever import-linter exposes after config)
- Add **`.pre-commit-config.yaml`** hooks that call the same steps (or the unified script once).
- Document in [docs/DEV.md](../../../docs/DEV.md): install hooks (`uv run pre-commit install` or equivalent), run `uv run check` before push.
- **User must approve** any new dev dependencies (`pre-commit`, `import-linter`) via `uv add --dev` before lockfile changes.

### 2. import-linter

- Contracts: `conlanger.ingest` must not import `conlanger.compile` (and any other layers documented in [index-diachronica-parser.md](../../../docs/system/index-diachronica-parser.md) § Package imports).
- Wire into gate script / pre-commit.

### 3. Implement / map closure

- Create [docs/agents/implement-closure.md](../../../docs/agents/implement-closure.md) with checklist:
  - Close ticket: `Status: resolved` (not `done`); `## Answer` when decision ticket.
  - Update [map.md](../map.md) Decisions-so-far / strike-through per existing style when ticket is indexed on map.
- Cross-link from [issue-tracker.md](../../../docs/agents/issue-tracker.md).
- One-line pointer in [AGENTS.md](../../../AGENTS.md).

### 4. docs/agents/coding-standards.md

- Review-only (for `/code-review` Standards axis).
- Include: no lazy imports to fix circular imports; structural proposal before large refactors when user requests; ingest↛compile (pointer to import-linter + parser doc).

### 5. Navigation

- Fix [docs/SYSTEM.md](../../../docs/SYSTEM.md) rule-index implementation pointers (`ingest`, `compile`, `uv run compile_rules` / `validate_rules`).
- AGENTS.md: pointer to package layout (ingest / compile / utils) → parser doc § Package imports.

### 6. docs/system/asca-rules-yaml-schema.md

- Short schema for compiled `asca_rules.yml` (rule shape, `steps`, `alternatives` block — align with [151](151-grill-validate-rules-asca-rules-yaml-diagnostic.md) / [159](159-task-write-compile-asca-rules-yml.md) policy).
- Link from SYSTEM.md and/or [sound-change-applier.md](../../../docs/system/sound-change-applier.md).

### 7. Hygiene

- **Delete** `.scratch/rule-index/spec.md`; grep repo and update links to `map.md` + `issues/` (and [issue-tracker.md](../../../docs/agents/issue-tracker.md) if it mandates spec.md generically — clarify rule-index is map-led).
- **GLOSSARY.md:** add **RHS** (and any other grill terms still missing) for ASCA/index notation.
- **DEV.md:** if `validate_rules` fails for missing binary, point to ASCA fork install block.

### 8. Map

- Update map **Agent-oriented docs** line: mark 171 resolved, link 172 when implementing; after 172 resolved, note guardrails + implement-closure live.

## Acceptance

- `uv run check` (or chosen name) exits 0 on clean tree.
- `pre-commit run --all-files` exits 0 after `pre-commit install`.
- import-linter fails on a deliberate test violation (or documented contract file present and passing).
- implement-closure discoverable from AGENTS.md.
- SYSTEM.md + ASCA schema doc accurate; no broken links to deleted `spec.md`.
- Full gate passes on branch at end of task.

## Out of scope

- GitHub Actions (deferred; grill chose pre-commit only).
- `check_scratch_sync` automation.
- Upstream mattpocock/skills changes.

## Answer

**Resolved 2026-10-18.** Added `uv run check`, `.pre-commit-config.yaml`, import-linter ingest↛compile contract, [implement-closure.md](../../../docs/agents/implement-closure.md), [coding-standards.md](../../../docs/agents/coding-standards.md), [asca-rules-yaml-schema.md](../../../docs/system/asca-rules-yaml-schema.md); deleted `.scratch/rule-index/spec.md`; updated SYSTEM.md, AGENTS.md, DEV.md, GLOSSARY (**LHS**/**RHS**).
