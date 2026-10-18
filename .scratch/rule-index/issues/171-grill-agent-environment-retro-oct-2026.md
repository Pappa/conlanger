Type: grilling
Status: resolved
Blocked by:

# Grill: agent environment improvements (Oct 2026 retro)

Spawned from agent `/retro` over conlanger sessions **2026-10-16–18** (map/ticket drift, unwired quality gates, ingest/compile seam, navigation staleness).

## Question

Lock implementation choices for a **single follow-on task** that applies the retro recommendations: wired guardrails, implement/map closure ritual, import-layer enforcement, doc fixes, thin review standards, and optional hygiene (spec stub, glossary grill terms).

**Resolve this grill first** (record decisions under `## Answer`), then open **task 172** (or retype this ticket to `task` once decisions are settled) for `/implement`.

## Scope (after decisions)

### 1. Wired guardrails

Mirror `.cursor/rules/python-quality-gates.mdc` in automation:

1. `uv run pytest` (coverage `fail_under` from `pyproject.toml`)
2. `uv run per_file_coverage_gate`
3. `uvx ruff check src tests` (+ format check)

**Decision:** pre-commit vs GitHub Actions vs `uv` script alias — see grill round 1.

### 2. Implement / map closure

- Doc: `docs/agents/implement-closure.md` (or subsection of `issue-tracker.md`) — checklist when closing a `.scratch/.../issues/*.md` ticket: `Status: resolved`, `## Answer` when needed, update `map.md` Decisions-so-far / strike-through per existing map style; never `done` on wayfinder children ([triage-labels.md](../../../docs/agents/triage-labels.md)).
- Pointer in [AGENTS.md](../../../AGENTS.md).
- **Decision:** optional `check_scratch_sync` script vs checklist-only.

### 3. Parse ↔ compile import contract

Enforce documented rule: `ingest` must not import `compile`; `compile` may import `ingest` ([index-diachronica-parser.md](../../../docs/system/index-diachronica-parser.md) § Package imports).

**Decision:** `import-linter` (dev dep) vs docs-only.

### 4. Navigation

- Fix [docs/SYSTEM.md](../../../docs/SYSTEM.md) rule-index row (stale `tools/parsers.py` / `tools/asca_validator.py` → current `ingest` / `compile` / scripts).
- Optional AGENTS.md one-line pointer to package layout (no duplicate table).

### 5. Review standards (judgement + mechanical)

- **Decision:** root `CODING_STANDARDS.md` (review-only) vs `docs/agents/coding-standards.md`.
- Include at minimum: no lazy imports to break cycles; propose structural fix before large refactors when user asks; Standards axis for `/code-review`.

### 6. ASCA / compiled YAML shape anchor

Single short schema reference for `asca_rules.yml` (e.g. `alternatives` under `steps`, not nested list ambiguity — see ticket [5afee11d session / 151+159 policy]).

**Decision:** ADR vs `docs/system/` vs checked-in example under `docs/` or `.scratch/`.

### 7. Optional hygiene

- **rule-index `spec.md` stub** pointing at `map.md` + `issues/` as authoritative (user: full `to-spec` output often stale).
- **GLOSSARY:** add grill-facing terms (e.g. **RHS**) when used in ASCA/index notation.
- **DEV.md:** one-line “missing `lib/bin/asca`” pointer at validate install block.

### 8. Map index

After task is filed and grill resolved, append one line under map **Agent-oriented docs** pointing at implement-closure + this effort.

## Out of scope

- Upstream mattpocock/skills changes (optional human issue [#1180](https://github.com/mattpocock/skills/issues/1180) — not this repo).
- Deduplicating global ctx7 rules (user-level Cursor config).
- Full `validate_rules` in CI unless grill explicitly chooses it (ASCA fork binary install cost).

## Acceptance (for follow-on implement task)

- Chosen guardrail(s) run the four-step gate locally and/or on push/PR.
- Agents can discover implement-closure from AGENTS.md + issue-tracker.
- Import contract fails CI/pre-commit when violated (if import-linter chosen).
- SYSTEM.md rule-index pointers match code layout.
- Review standards file exists at chosen path.
- ASCA YAML schema anchor exists at chosen path.
- Full gate sequence passes on branch.

## Answer

**Resolved 2026-10-18.**

| Q | Decision |
| --- | --- |
| Q1 Guardrail delivery | **A** — `pre-commit` only (no GitHub Actions in this effort) |
| Q2 CI scope | **N/A** for CI; local gate = **A + B** — full pytest/per-file/ruff gate **and** import-linter in the same pre-commit/check script |
| Q3 Map sync | **A** — implement-closure checklist in docs only (no sync script) |
| Q4 Import enforcement | **A + B** — `import-linter` in gate **and** document contract in `docs/agents/coding-standards.md` |
| Q5 Standards file | **B** — `docs/agents/coding-standards.md` |
| Q6 ASCA YAML anchor | **C** — `docs/system/asca-rules-yaml-schema.md` + SYSTEM.md link |
| Q7 rule-index spec | **Delete** `.scratch/rule-index/spec.md` (not stub); update repo pointers to `map.md` + `issues/` |

Follow-on: [172 task](172-task-agent-environment-retro-oct-2026.md).

## Comments

- **2026-10-18:** Ticket created; grill round 1 asked in Cursor session (agent-environment retro).
- **2026-10-18:** Grill answered; 172 filed.
