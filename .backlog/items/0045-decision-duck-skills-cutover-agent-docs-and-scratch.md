Type: epic-duck:decision
Status: resolved
Plan: [0001-plan-migrate-project-to-duck-skills.md](0001-plan-migrate-project-to-duck-skills.md)
Overview: Cutover from wayfinder (`.scratch/`) to duck-skills (`.backlog/`), agent doc shape, living-doc links, and fate of the legacy tree.
Blocked by:

## Question

Plan **0001** can close only after the repo has a single **operational** tracker story for agents and a clear rule for **legacy** wayfinder material. Resolve the following in one **`## Answer`** (policy bullets or tables plus any explicit **follow-on tasks** list).

### Tracker cutover (per effort)

1. **New work** — For rule-index (**0003**), data pipeline (**0004**), and generative sequences (**0005**), where do **new** tickets live after cutover? Choose per effort or one repo-wide rule: dual-write (`.scratch/` + `.backlog/`), **`.backlog/` only** (`.scratch/` frozen), or other.
2. **Open wayfinder frontier** — Any remaining `.scratch/<effort>/issues/` tickets that are not terminal: migrate, abandon, or leave frozen in place? Name the inventory rule (e.g. only `claimed` / `needs-grilling` on rule-index).
3. **Plan 0001 completion** — What must be true before plan **0001** becomes **`Status: resolved`** (checklist the owner can verify)?

### Legacy tree (`.scratch/`)

4. **Retention** — Keep `.scratch/` in the working tree as read-only archive, **delete** it from the repo, or keep only selected subtrees (which)?
5. **Archaeology links** — [0006](0006-decision-wayfinder-ticket-migration-policy.md) allowed merged backlog items to cite `.scratch/` in **source lists**. After cutover, may living docs and **`.backlog/`** items still link into `.scratch/`, or must links point only to `.backlog/`, `docs/`, and ADRs?
6. **Non-ticket assets** — Spike scripts, CSVs, probe fixtures under `.scratch/rule-index/research/` (not copied to `.backlog/spike/`): move into `src/`, `tests/`, or `docs/`, drop, or stay only if `.scratch/` is kept?

### Agent documentation (setup-duck-skills alignment)

7. **Entrypaths** — Target shape for **`AGENTS.md`**, **`CONTEXT.md`**, and **`docs/agents/backlog.md`**: match a clean **`setup-duck-skills`** local backlog install (Backlog, Ticket status, Domain docs only in `AGENTS.md`; no wayfinder read order). List files to **rewrite**, **retire**, or **keep with a one-line legacy note**.
8. **`docs/agents/issue-tracker.md`** — Retire, replace with a pointer to `backlog.md`, or keep for archive-only `.scratch/`?
9. **`docs/agents/ticket-statuses.md` and `triage-labels.md`** — Remove wayfinder-only sections, or keep mapped vocabulary for upstream Matt Pocock skills only?
10. **`docs/agents/implement-closure.md`** — Extend for **`.backlog/`** closure (status, plan table sync, `## Answer`, `uv run check`) and drop map strike-through, or split into two docs?

### Living repository links

11. **`docs/` and `docs/adr/`** — Policy for ~ticket links into `.scratch/rule-index/issues/` (especially `index-diachronica-parser.md`, `validate.md`, `SYSTEM.md`): retarget to backlog items, ADR-only, strip links, or acceptable while archive exists?
12. **`src/` and `tests/`** — Same policy for references such as `sample_asca_guess_fixtures.py` and doc link tests; should CI enforce **no** `.scratch/` paths outside an allowlist?

### Scope boundaries

13. **Efforts 0004 and 0005** — Is cutover for `.scratch/data-processing-pipeline/` and `.scratch/sound-change-sequences/` **in scope** for this decision (minimum backlog seed before delete), or explicitly **deferred** with `.scratch/` kept until those plans migrate?

**Resolution criteria:** The **Answer** gives implementers a ordered checklist (can spawn **`Type: epic-duck:task`** children on plan **0001**). It updates plan **0001** **Destination** / **Out of scope** if the dual-tracker interim story ends. It states whether plan **0003** **Not yet specified** (cutover for new rule-index tickets) is satisfied by the same policy or needs a separate line.

## Comments

### amigo-duck (pre-publish)

- **Fit:** Covers cutover, agent docs, link migration, delete risk, and 0001 closure bar from owner review session.
- **Complete:** Numbered decisions with actors (agents, implementers) and verifiable outcomes in resolution criteria.
- **Plain language:** Lead with decisions; defer execution detail to follow-on tasks named in the Answer.
- **Decision INVEST:** Valuable (unblocks 0001 close); testable when each numbered item has an explicit chosen option in **Answer**.

## Answer

**Owner resolution (2026-10-29).** Summarized by question number; execution order is [0046](0046-task-align-agent-docs-post-cutover.md) → [0047](0047-task-remove-scratch-links-from-living-tree.md) → [0048](0048-task-delete-scratch-directory.md), then close plan **0001**.

### Tracker cutover

| # | Decision |
|---|----------|
| **1** | **`.backlog/` only** for new work on plans **0003**, **0004**, **0005**. No new wayfinder files under `.scratch/`. |
| **2** | **Abandon** open wayfinder state. Backlog is sole operational tracker; owner already migrated needed items and manually removed redundant backlog copies — no 1:1 scratch audit. |
| **13** | **0004** / **0005** already on `.backlog/`; no extra seed from `.scratch/` before delete. |

### Legacy tree

| # | Decision |
|---|----------|
| **4** | **Delete** `.scratch/` from the repo. Deletion is the **last** migration step (after link and doc passes). |
| **5** | **No** `.scratch/` path links in any **living** file (everything outside deleted `.scratch/`). Strip or retarget in `.backlog/` (including resolved migration tickets **0006–0008**, **0031**, spike source lists) when touched in [0047](0047-task-remove-scratch-links-from-living-tree.md). Archaeology lives in **git history** only. |
| **6** | **Drop** unmigrated research assets (scripts, CSVs, probes under `.scratch/rule-index/research/`). **Do not** move into `src/` / `tests/` / `docs/`. Remove or rewrite **living** references to those artefacts; see Q6 list in session notes / [0047](0047-task-remove-scratch-links-from-living-tree.md). |

### Agent documentation

| # | Decision |
|---|----------|
| **7** | **`setup-duck-skills` minimal `AGENTS.md`** (Backlog, Ticket status, Domain docs) **plus** a **Rule index** subsection: plan [**0003**](0003-plan-cleaned-rule-index.md), `GLOSSARY.md`, `docs/SYSTEM.md`, ADRs — **no** wayfinder or `.scratch/`. Align **`CONTEXT.md`** and **`docs/agents/backlog.md`** (`.backlog/` only; drop dual-tracker paragraph). |
| **8** | **Retire** [`docs/agents/issue-tracker.md`](../../docs/agents/issue-tracker.md) — replace with **`setup-duck-skills`** default: tracker is `.backlog/`; see [`backlog.md`](../../docs/agents/backlog.md). No wayfinder operations. |
| **9** | **Remove** wayfinder / `.scratch/` sections from [`ticket-statuses.md`](../../docs/agents/ticket-statuses.md) and [`triage-labels.md`](../../docs/agents/triage-labels.md). Keep Matt Pocock **triage role** table in `triage-labels.md` only. |
| **10** | **Delete** [`docs/agents/implement-closure.md`](../../docs/agents/implement-closure.md). Remove links from `AGENTS.md`, `DEV.md`, backlog items, and **`0003`** decision text that cite it. Closure hygiene: **`Status: resolved`**, sync parent plan tables, `uv run check` — document in `backlog.md` or `coding-standards.md` if needed. |

### Living repository links

| # | Decision |
|---|----------|
| **11** | **Retarget** ticket links in `docs/` and `docs/adr/` to backlog items or ADRs where they exist; otherwise **strip link**, keep descriptive prose (correction-pass name, ADR id). |
| **12** | **No** CI rule banning `.scratch/` strings. Rely on [0047](0047-task-remove-scratch-links-from-living-tree.md). **Delete** `tests/docs/test_migrated_spike_links.py` in [0046](0046-task-align-agent-docs-post-cutover.md) (doc migration guards retired). |

### Plan 0001 closure checklist (Q3)

Plan **0001** becomes **`Status: resolved`** only when all are true:

1. [0046](0046-task-align-agent-docs-post-cutover.md), [0047](0047-task-remove-scratch-links-from-living-tree.md), and [0048](0048-task-delete-scratch-directory.md) are **`resolved`**.
2. `rg '\.scratch' --glob '!.scratch/**'` returns **no matches** (tree deleted, so entire repo should be clean).
3. **`features.md`** row for **0001** set to **`resolved`**.
4. Plan **0001** **Destination** / **Notes** updated to describe **`.backlog/`** as the sole tracker (no interim dual-tracker language).

### Plan 0003

Cutover for **new rule-index tickets** is satisfied by **Q1** (**.backlog/` only** on plan **0003**). Clear **Not yet specified** cutover line on **0003** when executing [0046](0046-task-align-agent-docs-post-cutover.md).
