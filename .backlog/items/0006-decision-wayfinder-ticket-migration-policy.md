Type: epic-duck:decision
Status: resolved
Plan: [0001-plan-migrate-project-to-duck-skills.md](0001-plan-migrate-project-to-duck-skills.md)
Overview: Rules for which wayfinder tickets move to `.backlog/`, how to merge and summarize them, and how much to compress the rule-index map.
Blocked by:

## Question

What **migration policy** applies when copying wayfinder work from the legacy wayfinder tree into the duck-skills **`.backlog/`** (planning and implementation items), so agents do not replay obsolete or redundant tickets?

Resolve all of the following in one documented answer (usable as checklist for plan **0003** and the other product plans):

1. **Merged implementation tasks** — When may several related wayfinder **task** tickets become **one** backlog item with heavily summarized content (problem, outcome, and acceptance criteria), instead of a 1:1 file copy? What makes tickets “related” enough to merge (same failure class, same pipeline stage, same correction-pass theme, etc.)?
2. **Terminal exclusions** — Confirm that wayfinder tickets closed as **out of scope** or **wontfix** (and epic-duck **`out-of-scope`** / **`wontfix`**) are **never** migrated as active backlog work. Where, if anywhere, should a one-line summary live (plan **Out of scope**, **Decisions so far** gist only, or archive pointer)?
3. **Superseded work** — How to identify and **exclude** tickets whose decisions or implementations were **overruled or overwritten** by later tickets (e.g. map strike-through chains, “supersedes” / “wontfix (superseded by …)” in the legacy rule-index wayfinder map). What is the rule for keeping historical gists in **Decisions so far** vs omitting them entirely from `.backlog/`?
4. **Spikes** — Under what conditions is a wayfinder **spike** (repo alias for upstream **research**) copied to `.backlog/`? Owner leaning: **only if still valuable** — define “still valuable” (feeds open work, documents unresolved constraints, findings not captured elsewhere) and whether findings stay in `.backlog/spike/` vs legacy wayfinder research paths.
5. **Rule-index map compression** — Target scale when migrating the legacy rule-index wayfinder map: owner leaning **~174 wayfinder issues → ~20–25** backlog children (merged/summarized). Decide exact band, what rolls up into **Decisions so far** on plan **0003** vs standalone **`Type: task`** / **`Type: spike`** items, and what remains only as links into the legacy wayfinder tree for archaeology.

**Resolution criteria:** A short policy section (bullets or table) that implementers can apply ticket-by-ticket, plus any updates needed to plan **0001** **Out of scope** / **Not yet specified** and plan **0003** **Notes**.

## Answer

### Merge rule (Q1) — **pipeline stage** (Approach 2)

Group wayfinder tickets for merge when they primarily touch the **same pipeline stage** in [docs/SYSTEM.md](../../docs/SYSTEM.md) (**parse**, **compile**, **validate**, or cross-cutting **tooling/docs**). Within a stage, merge **correction-pass** tickets that share the same transform family (even if failure classes differ).

| Stage bucket | ~Wayfinder tickets rolled up | Becomes on plan **0003** |
|--------------|------------------------------|---------------------------|
| **Parse** — surface cleanup, rule-line normalization, parse-time mappings/config | ~25 (many `correction-pass-*`, parse implements, semicolon/section/manual mapping) | 1 merged **`Type: task`** summary *or* **Decisions so far** gist if fully closed |
| **Compile** — segment/env transforms, group mappings, length/ejective/paren expansions | ~28 | 1–2 merged summaries |
| **Structured env / IndexContext / position** — grills 149/162, tasks 156/163–166/174, related env correction passes | ~22 | 1 merged summary + **Decisions so far** for closed grills |
| **Validate / inventory / operator CLI** — inventory CSV, `validate_rules`, ok enum, compiled YAML pipeline | ~18 | 1 merged summary |
| **Foundation & policy** — early decisions, schema, fidelity, workflow, ADRs 140–141 | ~15 | **Decisions so far** lines (merged gists), not standalone tasks |
| **Docs & agent environment** | ~6 | **Decisions so far** or 1 small merged note |
| **Open frontier** — not superseded; still `claimed`, `ready-for-agent`, or `needs-grilling` | ~7 | **Separate** rubber-duck **`Type: task`** items (do not merge with closed work) |

Each merged backlog item must include: **problem**, **outcome**, **acceptance criteria**, and a **source list** (links to `legacy wayfinder rule-index issue …` ticket numbers merged).

Similar **correction-pass** tickets in the same stage bucket **should** merge even when filenames differ (owner preference).

### Terminal exclusions (Q2) — **A**

- Never create `.backlog/` **`Type: task`**, **`Type: spike`**, or active planning children for wayfinder **`wontfix`**, **`out-of-scope`**, or epic-duck terminal equivalents.
- **No** parallel row on `.backlog/` for those outcomes — full history stays in **the legacy wayfinder tree** only.

### Superseded work (Q3) — **B**

- **Identify** via map strike-through, explicit “supersedes”, “wontfix (superseded by …)”, or a later ticket that replaces the implementation.
- **Do not** migrate superseded tickets as standalone `.backlog/` children.
- **Decisions so far** on **0003**: include a **one-line merged gist** only when the **underlying decision** still constrains current work; otherwise omit from `.backlog/` entirely. Gists must be **self-contained** (no links into the legacy wayfinder tree); cite ADRs and `docs/` only.

### Spikes (Q4) — **deferred**

- Spike migration rules are **not** decided here. Follow [0007-decision-wayfinder-spike-migration-policy.md](0007-decision-wayfinder-spike-migration-policy.md).
- Until **0007** is resolved: plan **0003** **Spikes** table stays **empty**; link legacy wayfinder research paths from merged summaries when needed.

### Rule-index compression (Q5)

- **Cap:** ≤ **25** indexed outcomes on plan **0003** (**Decisions so far** lines + **Tasks** + **Spikes** table rows combined).
- **Target split** (~173 wayfinder issue files):
  - **~12–16** **Decisions so far** bullets (foundation, closed grill chains, merged closed stage work),
  - **~6–9** rubber-duck **`Type: task`** items (open frontier + any merged stage summaries that still need executable acceptance criteria),
  - **0** **`Type: spike`** until **0007** resolves.
- Everything else remains reachable only via **`legacy wayfinder rule-index/`** links cited in merged items.

### Other product plans (**0004**, **0005**)

Apply the same exclusions (Q2, Q3) and merge-by-stage where multiple `legacy wayfinder` issues appear later; scale caps are proportional (those efforts currently have single seed issues).

## Comments

- 2026-10-29: Owner input when filing — prefer **fewer** backlog tickets via **merge + heavy summarization**; **exclude** out-of-scope, wontfix, and superseded/overwritten work; **spikes** only when still valuable; rule-index map migration target **~20–25** items from **~174** wayfinder issues.
- 2026-10-29: Resolved — Q2 **A**, Q3 **B**, Q1 **pipeline stage (Approach 2)**, Q5 **yes** (cap 25, split 12–16 / 6–9 / 0 spikes pending **0007**), Q4 → **0007**.
